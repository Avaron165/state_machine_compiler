from StateMachineParserVisitor import StateMachineParserVisitor
from StateMachineParser import StateMachineParser
from StateMachineObject import DeepHistoryState, DuplicatedEventMemberException, EndState, HistoryState, PortState, StartState, State, StateMachineObject, Event, PortDirection, SubmachinePort, Transition
from collections import deque

class DuplicatedStateMachineNameException(Exception):
    pass

class DuplicatedEventNameException(Exception):
    pass

class UnknownStateException(Exception):
    pass

class DuplicatedMachineMemberException(Exception):
    pass

class UnknowEventException(Exception):
    pass

class StateMachineObjectVisitor(StateMachineParserVisitor) :

    def __init__(self):
        self.state_machine_stack = deque()
        self.state_machines = {}
        self.events = {}
        self.event_stack = deque()
        self.state_stack = deque()

    @property
    def currentState(self):
        return self.state_stack[-1]
    
    @currentState.setter
    def currentState(self,state):
        self.state_stack.append(state)

    @property
    def currentMachine(self):
        return self.state_machine_stack[-1]
    
    @currentMachine.setter
    def currentMachine(self,machine):
        self.state_machine_stack.append(machine)

    def isStateStackEmpty(self):
        return len(self.state_stack) == 0

    @property
    def currentEvent(self):
        return self.event_stack[-1]
    
    @currentEvent.setter
    def currentEvent(self,event):
        self.event_stack.append(event)

    def registerStatemachine(self,name,machine):
        if name in self.state_machines:
            raise DuplicatedStateMachineNameException(name)
        self.state_machines[name] = machine

    def registerEvent(self,name,event):
        if name in self.events:
            raise DuplicatedEventNameException(name)
        self.events[name] = event

    def getEvent(self,name):
        if name not in self.events:
            raise UnknowEventException(name)
        return self.events[name]

    def visitStatemachine(self, ctx:StateMachineParser.StatemachineContext):
        name = self.visitStatemachine_name(ctx.statemachine_name())
        statemachine = StateMachineObject(name)
        try:
            self.registerStatemachine(name,statemachine)
        except DuplicatedStateMachineNameException as e:
            e.add_note(f'in line {ctx.start.line}')
            raise
        self.currentMachine = statemachine
        statemachine.addState(StartState())
        statemachine.addState(EndState())
        self.visitStatemachine_body(ctx.statemachine_body())
        if not self.isStateStackEmpty():
            for (eventname, event) in self.currentMachine.events.items():
                self.state_machine_stack[-2].events[eventname].addAffectedState(self.currentState.name)
        print(f'Events of {name}: {self.currentMachine.events}')
        return self.state_machine_stack.pop()

    def visitStatemachine_name(self, ctx:StateMachineParser.Statemachine_nameContext):
        return str(ctx.IDENTIFIER())

    def visitEvent_definition(self, ctx:StateMachineParser.Event_definitionContext):
        eventname = self.visitEvent_name(ctx.event_name())
        event = Event(eventname)
        try:
            self.registerEvent(eventname,event)
        except DuplicatedEventNameException as e:
            e.add_note(f'in line {ctx.start.line}')
            raise
        self.currentMachine.addEvent(event)
        self.currentEvent = event
        if ctx.event_data_definition() is not None:
            self.visitEvent_data_definition(ctx.event_data_definition())
        self.event_stack.pop()
    
    def visitEvent_use(self, ctx:StateMachineParser.Event_useContext):
        eventname = self.visitEvent_name(ctx.event_name())
        event = self.getEvent(eventname)
        self.currentMachine.addEvent(event)

    def visitEvent_data_member(self, ctx:StateMachineParser.Event_data_memberContext):
        typename = self.visitTypename(ctx.typename())
        membername = self.visitMembername(ctx.membername())
        try:
            self.currentEvent.addMember(membername,typename)
        except DuplicatedEventMemberException as e:
            e.add_note(f'in line {ctx.start.line}')
            raise

        
    def visitTypename(self, ctx:StateMachineParser.TypenameContext):
        return str(ctx.IDENTIFIER())

    def visitMembername(self, ctx:StateMachineParser.MembernameContext):
        return str(ctx.IDENTIFIER())

    def visitEvent_name(self, ctx:StateMachineParser.Event_nameContext):
        return str(ctx.UPPERCASE_IDENTIFIER())

    def visitIn_port_identifier(self, ctx:StateMachineParser.In_port_identifierContext):
        return PortState(str(ctx.IDENTIFIER()),PortDirection.IN)

    def visitOut_port_identifier(self, ctx:StateMachineParser.Out_port_identifierContext):
        self.currentMachine.addState(PortState(str(ctx.IDENTIFIER()),PortDirection.OUT))

    def visitHistory(self, ctx:StateMachineParser.HistoryContext):
        return HistoryState()

    def visitDeephistory(self, ctx:StateMachineParser.DeephistoryContext):
        return DeepHistoryState()

    def visitState_identifier(self, ctx:StateMachineParser.State_identifierContext):
        return str(ctx.IDENTIFIER())

    def aggregateResult(self, aggregate, nextResult):
        if (nextResult is not None):
            aggregate.append(nextResult)
        return aggregate
    
    def defaultResult(self):
        return []
    
    def visitTerminal(self, node):
        return None
    
    def visitIn_port(self, ctx:StateMachineParser.In_portContext):
        self.currentMachine.addState(self.visitChildren(ctx)[0])
        return 
    
    def visitStatemachine_data_member(self, ctx:StateMachineParser.Statemachine_data_memberContext):
        typename = self.visitTypename(ctx.typename())
        membername = self.visitMembername(ctx.membername())
        try:
            self.currentMachine.addDataMember(membername,typename)
        except DuplicatedMachineMemberException as e:
            e.add_note(f'in line {ctx.start.line}')
            raise        

    def visitState_definition(self, ctx:StateMachineParser.State_definitionContext):
        statename = self.visitState_identifier(ctx.state_identifier())
        if ctx.state_qualifier() is not None:
            fork_type = self.visitState_qualifier(ctx.state_qualifier())
            print(fork_type)
        state = State(statename)
        self.currentMachine.addState(state)
        self.currentState = state
        self.visitState_body(ctx.state_body())
        self.state_stack.pop()

    def visitState_qualifier(self, ctx:StateMachineParser.State_qualifierContext):
        return self.visitChildren(ctx)[0]

    def visitJoin(self, ctx:StateMachineParser.JoinContext):
        return "join"


    def visitSplit(self, ctx:StateMachineParser.SplitContext):
        return "split"

    def visitState_function(self, ctx:StateMachineParser.State_functionContext):
        eventname = self.visitState_event(ctx.state_event())
        functionToCall = self.visitFunction_indentifier(ctx.function_indentifier())
        self.currentState.addEventFunction(eventname,functionToCall)
        if ((eventname != "exit") and (eventname != "entry" )):
            self.currentMachine.events[eventname].addAffectedState(self.currentState.name)

    def visitFunction_indentifier(self, ctx:StateMachineParser.Function_indentifierContext):
        return str(ctx.IDENTIFIER())

    def visitState_event(self, ctx:StateMachineParser.State_eventContext):
        return self.visitChildren(ctx)[0]


    def visitEntry(self, ctx:StateMachineParser.EntryContext):
        return "entry"


    def visitExit(self, ctx:StateMachineParser.ExitContext):
        return "exit"
    
    def visitStatemachine_declaration(self, ctx:StateMachineParser.Statemachine_declarationContext):
        submachine = self.visitChildren(ctx)[0]
        self.currentState.addStateMachine(submachine.name, submachine)
        for portState in submachine.states.values():
            if not isinstance(portState, PortState):
                continue
            self.currentMachine.addState(SubmachinePort(f'{submachine.name}.{portState.name}',portState.direction))

    def visitStatemachine_include(self, ctx:StateMachineParser.Statemachine_includeContext):
        raise NotImplementedError("statemachine include")    

    def visitTransition_without_function(self, ctx:StateMachineParser.Transition_without_functionContext):
        eventname = self.visitEvent_classifier(ctx.event_classifier())
        from_state = self.visitFrom_state(ctx.from_state())
        to_state = self.visitTo_state(ctx.to_state())
        machine = self.currentMachine
        try:
            fromState = machine.states[from_state]
            toState = machine.states[to_state]
        except Exception:
            raise UnknownStateException(f'Unknown State in transition from {from_state} to {to_state}')
        fromState.addTransition(eventname, Transition(to_state,eventname,None))
        if eventname != "automatic":
            machine.events[eventname].addAffectedState(from_state)

    def visitEvent_classifier(self, ctx:StateMachineParser.Event_classifierContext):
        return self.visitChildren(ctx)[0]
    
    def visitAutomatic(self, ctx:StateMachineParser.AutomaticContext):
        return "automatic"
    
    def visitFrom_state(self, ctx:StateMachineParser.From_stateContext):
        if ctx.state_identifier():
            return self.visitState_identifier(ctx.state_identifier())
        else:
            return self.visitSubmachine_port(ctx.submachine_port())

    def visitSubmachine_port(self, ctx:StateMachineParser.Submachine_portContext):
        submachine = self.visitStatemachine_name(ctx.statemachine_name())
        port = self.visitPort_identifier(ctx.port_identifier())
        return submachine + "." + port

    def visitTo_state(self, ctx:StateMachineParser.To_stateContext):
        return self.visitState_identifier(ctx.state_identifier())

    def visitTransition_with_function(self, ctx:StateMachineParser.Transition_with_functionContext):
        eventname = self.visitEvent_classifier(ctx.event_classifier())
        from_state = self.visitFrom_state(ctx.from_state())
        to_state = self.visitTo_state(ctx.to_state())
        function = self.visitFunction_indentifier(ctx.function_indentifier())
        machine = self.currentMachine
        try:
            fromState = machine.states[from_state]
            toState = machine.states[to_state]
        except Exception:
            raise UnknownStateException(f'Unknown State in transition from {from_state} to {to_state}')
        fromState.addTransition(eventname, Transition(to_state,eventname,function))
        if eventname != "automatic":
            machine.events[eventname].addAffectedState(from_state)

    def visitPort_identifier(self, ctx:StateMachineParser.Port_identifierContext):
        return str(ctx.IDENTIFIER())