from enum import Enum
from collections import deque



class PortDirection(Enum):
    IN = 1
    OUT = 2

    def __str__(self):
        return self.name
    

class Indent:
    def __init__(self,indent):
        self.indent_str = ""
        for idx in range(indent):
            self.indent_str += " "

    def __str__(self):
        return self.indent_str

def print_with_indent(indent,string):
    print(f'{str(Indent(indent))}{string}')
    
class DuplicatedEventMemberException(Exception):
    pass

class DuplicatedEventFunctionException(Exception):
    pass

class DuplicatedSubMachineNameException(Exception):
    pass

class DuplicateEventTransitionException(Exception):
    pass

class AutomaticTransitionMismatchException(Exception):
    pass

class DuplicatedStateAffectionInEventException(Exception):
    pass

class Transition:
    def __init__(self, toState, event, function):
        self.toState = toState
        self.event = event
        self.function = function

    def print_with_indent(self,indent):
        if self.function:
            print_with_indent(indent,f'{self.event} : -> {self.toState} : {self.function}')
        else:
            print_with_indent(indent,f'{self.event} : -> {self.toState}')

class State:
    def __init__(self,name):
        self.name = name
        self.functions = {}
        self.statemachines = {}
        self.hasAutoTransition = False
        self.transitions = {}

    def addTransition(self,event,transition):
        if self.hasAutoTransition:
            raise AutomaticTransitionMismatchException(event, f'from State {self.name}')
        if event == "automatic":
            if self.transitions:
                raise AutomaticTransitionMismatchException("automatic transition but event triggered transition present", f'from State {self.name}')
            self.hasAutoTransition = True
        if event in self.transitions:
            raise DuplicateEventTransitionException(event, f'from State {self.name}')
        self.transitions[event] = transition


    def addEventFunction(self,eventname,functionToCall):
        if eventname in self.functions:
            raise DuplicatedEventFunctionException(eventname, f'in state {self.name}')
        self.functions[eventname] = functionToCall

    def addStateMachine(self,smName,statemachine):
        if smName in self.statemachines:
            raise DuplicatedSubMachineNameException(smName, f'in state {self.name}')
        self.statemachines[smName] = statemachine

    def print_with_indent(self,indent):
        print_with_indent(indent,f'State {self.name}')
        for (event, function) in self.functions.items():
            print_with_indent(indent+2,f'{event}: {function}()')
        for (smName, sm) in self.statemachines.items():
            sm.print_with_indent(indent+2)
        print_with_indent(indent+2,"Transitions:")
        for transition in self.transitions.values():
            transition.print_with_indent(indent+4)

class StartState(State):
    def __init__(self):
        super().__init__("start")

class EndState(State):
    def __init__(self):
        super().__init__("end")

class SubmachinePort(State):
    def __init__(self,name,direction):
        super().__init__(name)
        self.direction = direction

class PortState(State):
    def __init__(self,name,direction):
        super().__init__(name)
        self.direction = direction

    def print_with_indent(self,indent):
        print_with_indent(indent,f'{self.direction} Port State {self.name}')

class HistoryState(PortState):
    def __init__(self):
        super().__init__("history",PortDirection.IN)
    
class DeepHistoryState(PortState):
    def __init__(self):
        super().__init__("deephistory",PortDirection.IN)

class Event:
    def __init__(self,name):
        self.name = name
        self.members = {}
        self.affected_states = []

    def __str__(self):
        return self.name

    def print_with_indent(self,indent):
        print_with_indent(indent,f'Event {self}')
        print_with_indent(indent+2,f'Members:')
        for member in self.members.keys():
            print_with_indent(indent+4,f'{self.members[member]} {member}')    

    def addAffectedState(self, state):
        if state in self.affected_states:
            raise DuplicatedStateAffectionInEventException(state, f'in event {self.name}')
        self.affected_states.append(state)

    def addMember(self, member, typename):
        if member in self.members:
            raise DuplicatedEventMemberException(member, f'in event {self.name}')
        self.members[member] = typename


class DuplicatedEventUseException(Exception):
    pass 


class DuplicatedStateNameException(Exception):
    pass

class DuplicatedMachineMemberException(Exception):
    pass

class StateMachineObject:
    def __init__(self, name):
        self.name = name
        self.events = {}
        self.states = {}
        self.members = {}

    def addState(self, state):
        if state.name in self.states:
            raise DuplicatedStateNameException(state.name, f'in machine {self.name}')
        self.states[state.name] = state

    def addEvent(self, event):
        if event.name in self.events:
            raise DuplicatedEventUseException(event.name, f'in machine {self.name}')
        self.events[event.name] = event

    def __str__(self):
        return self.name
    
    def addDataMember(self, membername, typename):
        if membername in self.members:
            raise DuplicatedMachineMemberException(membername, f'in machine {self.name}')
        self.members[membername] = typename

    def print_with_indent(self,indent):
        print_with_indent(indent,f'Statemachine {self}')
        print_with_indent(indent+2,"Events:")
        for event in self.events.values():
            event.print_with_indent(indent+4)
        print_with_indent(indent+2,"States:")
        for state in self.states.values():
            state.print_with_indent(indent+4)
        print_with_indent(indent+2,"Data:")
        for (member, type) in self.members.items():
            print_with_indent(indent+4,f'{type} {member}')