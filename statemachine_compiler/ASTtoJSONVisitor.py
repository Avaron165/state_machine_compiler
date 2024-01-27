from StateMachineParserVisitor import StateMachineParserVisitor
from StateMachineParser import StateMachineParser
import logging

class StatemachineParserException(Exception):
    def __init__(self,errorstring):
        super().__init__(errorstring)

class DuplicatedEventDeclaration(StatemachineParserException):
    def __init__(self, event1, event2):
        error_string =    f'{event1["declared_in"][-1][0]}: line {event1["declared_at"]} -- Duplicated declaration of event {event1["name"]}\n'
        error_string +=   f'   previously declared in {event2["declared_in"][-1][0]}: line {event2["declared_at"]}'      
        super().__init__(error_string)

class DuplicatedStatemachineDeclaration(StatemachineParserException):
    def __init__(self, machine1, machine2):
        error_string =    f'{machine1["declared_in"][-1][0]}: line {machine1["declared_at"]} -- Duplicated declaration of event {machine1["name"]}\n'
        error_string +=   f'   previously declared in {machine2["declared_in"][-1][0]}: line {machine2["declared_at"]}'      
        super().__init__(error_string)

class DuplicatedStateDeclaration(StatemachineParserException):
    def __init__(self, state1, state2):
        error_string =    f'{state1["declared_in"][-1][0]}: line {state1["declared_at"]} -- Duplicated declaration of state {state1["name"]}\n'
        error_string +=   f'   previously declared in {state2["declared_in"][-1][0]}: line {state2["declared_at"]}'      
        super().__init__(error_string)

class UndefinedEventUsage(StatemachineParserException):
    def __init__(self, eventname, location):
        error_string =    f'{location[0][-1]}: line {location[1]} -- undefined event {eventname}\n'
        super().__init__(error_string)

class DuplicatedEventUsage(StatemachineParserException):
    def __init__(self, eventname, location1, location2):
        error_string =    f'{location1[0][-1]}: line {location1[1]} -- duplicated usage of event {eventname}\n'
        error_string +=   f'   previously used in {location2[0][-1]}: line {location2[1]}'      
        super().__init__(error_string)


class EventNotUsed(StatemachineParserException):
    def __init__(self, eventname, location):
        error_string =    f'{location[0][-1]}: line {location[1]} -- tried to use event {eventname} which is not used by current statemachine\n'
        super().__init__(error_string)

class UndefinedStatemachineUsage(StatemachineParserException):
    def __init__(self, statemachine, location):
        error_string =    f'{location[0][-1]}: line {location[1]} -- tried to use unknown statemachine {statemachine}\n'
        super().__init__(error_string)

class DuplicatedStatemachineAlias(StatemachineParserException):
    def __init__(self, alias, state, location):
        error_string =    f'{location[0][-1]}: line {location[1]} -- duplicated statemachine alias name {alias} in state {state["name"]}\n'
        super().__init__(error_string)

class DuplicatedPortDeclaration(StatemachineParserException):
    def __init__(self, port, location):
        error_string =    f'{location[0][-1]}: line {location[1]} -- duplicated declaration of port {port}\n'
        super().__init__(error_string)

class DuplicatedMemberDeclaration(StatemachineParserException):
    def __init__(self, member, location):
        error_string =    f'{location[0][-1]}: line {location[1]} -- duplicated declaration of member {member}\n'
        super().__init__(error_string)

class UndefinedStateUsage(StatemachineParserException):
    def __init__(self, state, location):
        error_string =    f'{location[0][-1]}: line {location[1]} -- tried to use unknown state {state}\n'
        super().__init__(error_string)

class SubmachineAliasNotDefined(StatemachineParserException):
    def __init__(self, alias, location):
        error_string =    f'{location[0][-1]}: line {location[1]} -- submachine alias {alias} is not defined\n'
        super().__init__(error_string)

class SubmachineUndefinedPort(StatemachineParserException):
    def __init__(self, submachine, alias, port, location):
        error_string =    f'{location[0][-1]}: line {location[1]} -- submachine {submachine} alias {alias} has no port {port} \n'
        super().__init__(error_string)

class DuplicatedTransitionForEvent(StatemachineParserException):
    def __init__(self, event, state, location):
        error_string =    f'{location[0][-1]}: line {location[1]} -- duplicated transition for event {event} in state {state} \n'
        super().__init__(error_string)

class AutoTransitionHasEvent(StatemachineParserException):
    def __init__(self, statename, location):
        error_string =    f'{location[0][-1]}: line {location[1]} --  tried to add automatic transition to state {statename} which already has event based transition\n'
        super().__init__(error_string)

class EventTransitionHasAutomatic(StatemachineParserException):
    def __init__(self, event, statename, location):
        error_string =    f'{location[0][-1]}: line {location[1]} --  tried to add event {event} based transition to state {statename} which already has an automatic transition\n'
        super().__init__(error_string)

class DuplicatedAutoTransition(StatemachineParserException):
    def __init__(self, state, location ):
        error_string =    f'{location[0][-1]}: line {location[1]} --  tried to add automatic transition to state {state} which already has event an auto transition\n'
        super().__init__(error_string)
class ASTtoJSONVisitor(StateMachineParserVisitor):

    def __init__(self, filename):
        self.filename_stack = []
        self.filename_stack.append( (filename, None) )
        self.json_rep = { "events": {}, "statemachines": {} }
        self.transition_dispatcher = {
            "state": {
                "state": self.state_state_transition,
                "joinstate": self.state_join_transition,
                "splitstate": self.state_split_transition,
                "choicestate": self.state_choice_transition,
                "out port": self.state_out_port_transition,
                "submachine in port": self.state_sub_in_port_transition
            },
            "joinstate": {
                "state": self.join_state_transition,
                "joinstate": self.join_join_transition,
                "splistate": self.join_splt_transition,
                "choicestate": self.join_choice_transition,
                "out port": self.join_out_port_transition,
                "submachine in port": self.join_sub_in_port_transition
            },
            "splitstate": {
                "state": self.split_state_transition,
                "joinstate": self.split_join_transition,
                "splistate": self.split_splt_transition,
                "choicestate": self.split_choice_transition,
                "out port": self.split_out_port_transition,
                "submachine in port": self.split_sub_in_port_transition
            },
            "choicestate": {
                "state": self.choice_state_transition,
                "joinstate": self.choice_join_transition,
                "splistate": self.choice_splt_transition,
                "choicestate": self.choice_choice_transition,
                "out port": self.choice_out_port_transition,
                "submachine in port": self.choice_sub_in_port_transition
            },
            "in port": {
                "state": self.state_state_transition,
                "joinstate": self.in_port_join_transition,
                "splistate": self.in_port_splt_transition,
                "choicestate": self.in_port_choice_transition,
                "out port": self.in_port_out_port_transition,
                "submachine in port": self.in_port_sub_in_port_transition
            },
            "submachine out port": {
                "state": self.sub_out_port_state_transition,
                "joinstate": self.sub_out_port_join_transition,
                "splistate": self.sub_out_port_splt_transition,
                "choicestate": self.sub_out_port_choice_transition,
                "out port": self.sub_out_port_out_port_transition,
                "submachine in port": self.sub_out_port_sub_in_port_transition
            }
        }


    def state_state_transition(self, event, from_state,to_state, function, line):
        if event == "automatic":
            if from_state["auto transition"]:
                raise DuplicatedAutoTransition(from_state["name"], (self.filename_stack, line ))
            from_state["auto transition"] = { "type": "state", "state": to_state["name"], "function": function }
        else:
            if event in from_state["event transitions"]:
                raise DuplicatedTransitionForEvent(event, from_state["name"], (self.filename_stack, line))
            from_state["event transitions"][event] = { "type": "state", "state": to_state["name"], "function": function } 

    def state_join_transition(self, event, from_state,to_state, function, line):
        raise NotImplementedError()

    def state_split_transition(self, event, from_state,to_state,function, line):
        raise NotImplementedError()

    def state_choice_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def state_out_port_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def state_sub_in_port_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def join_state_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def join_join_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def join_splt_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def join_choice_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def join_out_port_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def join_sub_in_port_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def split_state_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def split_join_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def split_splt_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def split_choice_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def split_out_port_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def split_sub_in_port_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def choice_state_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def choice_join_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def choice_splt_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def choice_choice_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def choice_out_port_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def choice_sub_in_port_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def in_port_join_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def in_port_splt_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def in_port_choice_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def in_port_out_port_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def in_port_sub_in_port_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def sub_out_port_state_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def sub_out_port_join_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def sub_out_port_splt_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def sub_out_port_choice_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def sub_out_port_out_port_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    def sub_out_port_sub_in_port_transition(self, event,from_state,to_state,function, line):
        raise NotImplementedError()

    # Visit a parse tree produced by StateMachineParser#file(self,from_state,to_state,function):
    def visitFile(self, ctx:StateMachineParser.FileContext):
        self.json_rep = { "events": {}, "statemachines": {} }
        for event in ctx.event_declaration_block():
            new_event = self.visitEvent_declaration_block(event)
            new_event_name = new_event["name"]
            self.json_rep["events"][new_event_name] = new_event
        for statemachine in ctx.statemachine():
            new_statemachine = self.visitStatemachine(statemachine)
            new_statemachine_name = new_statemachine["name"]
            self.json_rep["statemachines"][new_statemachine_name] = new_statemachine
        return self.json_rep
    
    # Visit a parse tree produced by StateMachineParser#event_declaration_block.
    def visitEvent_declaration_block(self, ctx:StateMachineParser.Event_declaration_blockContext):
        event = {"type": "event"}
        eventname = self.visitEvent_name(ctx.event_name())
        logging.info(f'visiting event declaration {eventname} in line {ctx.start.line}')
        event["name"] = eventname
        event["declared_at"] = ctx.start.line
        event["declared_in"] = self.filename_stack
        if eventname in self.json_rep["events"]:
            raise DuplicatedEventDeclaration(event, self.json_rep["events"][eventname])
        members = []
        for member_node in ctx.member():
            new_member = self.visitMember(member_node)
            for check_member in members:
                if check_member["name"] == new_member["name"]:
                    raise DuplicatedMemberDeclaration(new_member["name"],(self.filename_stack,ctx.member().start.line))
            members.append(new_member)
        if members:
            event["members"] = members
        return event

    # Visit a parse tree produced by StateMachineParser#statemachine.
    def visitStatemachine(self, ctx:StateMachineParser.StatemachineContext):
        statemachine = {"type": "statemachine", "in ports": {"start": {"name": "start", "type": "in port", "event transitions": {}, "auto transition": None }}, "out ports": {"end": {"name": "end", "type": "out port"}}}
        statemachine_name = self.visitStatemachine_name(ctx.statemachine_name())
        logging.info(f'visiting statemachine declaration {statemachine_name} in line {ctx.start.line}')
        statemachine["name"] = statemachine_name
        statemachine["declared_at"] = ctx.start.line
        statemachine["declared_in"] = self.filename_stack
        if statemachine_name in self.json_rep["statemachines"]:
            raise DuplicatedStatemachineDeclaration(statemachine, self.json_rep["statemachines"][statemachine_name])
        self.visitStatemachine_body(ctx.statemachine_body(), statemachine )
        return statemachine


    # Visit a parse tree produced by StateMachineParser#statemachine_body.
    def visitStatemachine_body(self, ctx:StateMachineParser.Statemachine_bodyContext, statemachine):
        if ctx.event_usage_body():
            used_list = self.visitEvent_usage_body(ctx.event_usage_body(), self.json_rep["events"])
            statemachine["uses_events"] = used_list
        self.visitStates_definition_body(ctx.states_definition_body(), statemachine, self.json_rep["events"])
        if ctx.port_definition_body():
            self.visitPort_definition_body(ctx.port_definition_body(), statemachine)
        if ctx.data_definition_body():
            data_members = self.visitData_definition_body(ctx.data_definition_body())
            if data_members:
                statemachine["data"] = data_members
        if ctx.transitions_definition_body():
            self.visitTransitions_definition_body(ctx.transitions_definition_body(),statemachine)

    # Visit a parse tree produced by StateMachineParser#transitions_definition_body.
    def visitTransitions_definition_body(self, ctx:StateMachineParser.Transitions_definition_bodyContext, statemachine):
       for transition in ctx.transition():
           self.visitTransition(transition,statemachine)

    # Visit a parse tree produced by StateMachineParser#transition.
    def visitTransition(self, ctx:StateMachineParser.TransitionContext, statemachine):
        event = self.visitEvent_classifier(ctx.event_classifier(),statemachine)
        from_state = self.visitFrom_state(ctx.from_state(),statemachine)
        to_state = self.visitTo_state(ctx.to_state(),statemachine)
        function_identifier = None
        transition = {}
        if ctx.function_indentifier():
            function_identifier = self.visitFunction_indentifier(ctx.function_indentifier())
            transition["function"] = function_identifier
        logging.info(f'visiting Transition from {from_state["name"]} to {to_state["name"]} by event {event} calling {function_identifier}')
        self.transition_dispatcher[from_state["type"]][to_state["type"]](event, from_state, to_state, function_identifier, ctx.start.line )
#         if from_state["type"] == "state":
#             actual_state = statemachine["states"][from_state["state"]]
#             if to_state["type"] == "state": # State to State
#                 transition["type"] = "transition"
#                 transition["to_state"] = to_state["state"] 
#             elif to_state["type"] == "out port": # State to local out Port
#                 if "machine alias" in to_state:
#                     raise SyntaxError()
#                 transition["type"] = "leave machine"
#                 transition["out_port"] = to_state["port"]
#             elif to_state["type"] == "in port": # State to submachine in Port
#                 if not "macine alias" in to_state:
#                     raise SyntaxError()
#                 transition["type"] = "enter submachine"
#                 transition["machine alias"] = to_state["machine alias"]
#                 transition["machine"] = to_state["machine"]
#                 transition["port"] = to_state["port"]    
#             if event in actual_state["transitions"]:
#                 raise DuplicatedTransitionForEvent(event,actual_state["name"], (self.filename_stack, ctx.start.line ))
#             if (event == "automatic") and (actual_state["transitions"]):
#                 raise AutoTransitionHasEvent(actual_state["name"],(self.filename_stack, ctx.start.line ))
#             if (event != "automatic") and ("automatic" in actual_state["transitions"]):
#                 raise EventTransitionHasAutomatic(event, actual_state["name"],(self.filename_stack, ctx.start.line ))
#             actual_state["transitions"][event] = transition
#         elif from_state["type"] == "in port":
#             if (to_state["type"] == "in port") or (to_state["type"] == "out port"):
#                 raise PortToNonNormalStateTransition(from_state["port"],(self.filename_stack, ctx.start.line ))
#             transition["type"] = "transition"
#             transition["to_state"] = to_state["name"]
#             statemachine["states"][from_state["state"]]


    # Visit a parse tree produced by StateMachineParser#from_state.
    def visitFrom_state(self, ctx:StateMachineParser.From_stateContext,statemachine):
        if ctx.state_identifier():
            state = self.visitState_identifier(ctx.state_identifier())
            if not ((state in statemachine["states"]) or (state in statemachine["in ports"])):
                raise UndefinedStateUsage(state,(self.filename_stack,ctx.start.line))
            if state in statemachine["states"]:
                return statemachine["states"][state]
            else:
                return statemachine["in ports"][state]
        else:
            alias = self.visitStatemachine_name(ctx.statemachine_name())
            try:
                submachine = statemachine["submachines"][alias]
            except KeyError:
                raise SubmachineAliasNotDefined(alias,(self.filename_stack,ctx.start.line))
            port = self.visitPort_identifier(ctx.port_identifier())
            if port not in self.json_rep["statemachines"][submachine]["out ports"]:
                raise SubmachineUndefinedPort(port,(self.filename_stack,ctx.start.line))
            return { "type": "submachine out port", "machine alias": alias, "machine": submachine, "name": port}

    # Visit a parse tree produced by StateMachineParser#to_state.
    def visitTo_state(self, ctx:StateMachineParser.To_stateContext, statemachine):
        if ctx.state_identifier():
            state = self.visitState_identifier(ctx.state_identifier())
            if not ((state in statemachine["states"]) or (state in statemachine["out ports"])):
                raise UndefinedStateUsage(state,(self.filename_stack,ctx.start.line))
            if state in statemachine["states"]:
                return statemachine["states"][state]
            else:
                return statemachine["out ports"][state]
        else:
            alias = self.visitStatemachine_name(ctx.statemachine_name())
            try:
                submachine = statemachine["submachines"][alias]
            except KeyError:
                raise SubmachineAliasNotDefined(alias,(self.filename_stack,ctx.start.line))
            port = self.visitIn_port(ctx.in_port())
            if port not in self.json_rep["statemachines"][submachine]["in ports"]:
                raise SubmachineUndefinedPort(port,(self.filename_stack,ctx.start.line))
            return { "type": "submachine in port", "machine alias": alias, "machine": submachine, "name": port}

    # Visit a parse tree produced by StateMachineParser#event_classifier.
    def visitEvent_classifier(self, ctx:StateMachineParser.Event_classifierContext, statemachine):
        if ctx.automatic():
            return "automatic"
        else:
            event = self.visitEvent_name(ctx.event_name())
            if event not in statemachine["uses_events"]:
                raise EventNotUsed(event,(self.filename_stack,ctx.start.line))
            return event

    # Visit a parse tree produced by StateMachineParser#data_definition_body.
    def visitData_definition_body(self, ctx:StateMachineParser.Data_definition_bodyContext):
        members = []
        for member_node in ctx.member():
            new_member = self.visitMember(member_node)
            for check_member in members:
                if check_member["name"] == new_member["name"]:
                    raise DuplicatedMemberDeclaration(new_member["name"],(self.filename_stack,ctx.member().start.line))
            members.append(new_member)
        if members:
            return members
        else:
            return None

    # Visit a parse tree produced by StateMachineParser#port_definition_body.
    def visitPort_definition_body(self, ctx:StateMachineParser.Port_definition_bodyContext, statemachine):
        if ctx.port_in_block():
            self.visitPort_in_block(ctx.port_in_block(), statemachine )
        if ctx.port_out_block():
            self.visitPort_out_block(ctx.port_out_block(), statemachine )

    # Visit a parse tree produced by StateMachineParser#port_in_block.
    def visitPort_in_block(self, ctx:StateMachineParser.Port_in_blockContext, statemachine):
        portdict = {}
        self.visitIn_port_list(ctx.in_port_list(), portdict)
        statemachine["in ports"] |= portdict

    # Visit a parse tree produced by StateMachineParser#in_port_list.
    def visitIn_port_list(self, ctx:StateMachineParser.In_port_listContext, portdict):
        for inport in ctx.in_port():
            self.visitIn_port(inport, portdict)


    # Visit a parse tree produced by StateMachineParser#in_port.
    def visitIn_port(self, ctx:StateMachineParser.In_portContext, portdict):
        port = None
        portname = ""
        if ctx.history():
            port = { "history": {"type": "history port", "name": "history" }}
            portname = "history"
        elif ctx.deephistory():
            port = { "deephistory": {"type": "deephistory port", "name": "deephistory"}}
            portname = "deephistory"
        else:
            portname = self.visitIn_port_identifier(ctx.in_port_identifier())
            port = { portname: {"type": "in port", "name": portname, "event transitions": {}, "auto transition": None }}
        logging.info(f'visiting port declaration {portname} in line {ctx.start.line}')
        if portname in portdict:
            raise DuplicatedPortDeclaration(portname,(self.filename_stack, ctx.start.line))
        portdict |= port

    # Visit a parse tree produced by StateMachineParser#in_port_identifier.
    def visitIn_port_identifier(self, ctx:StateMachineParser.In_port_identifierContext):
        return str(ctx.IDENTIFIER)

    # Visit a parse tree produced by StateMachineParser#port_out_block.
    def visitPort_out_block(self, ctx:StateMachineParser.Port_out_blockContext, statemachine):
        portdict = {}
        self.visitOut_port_list(ctx.out_port_list, portdict)
        statemachine["out ports"] |= portdict

    # Visit a parse tree produced by StateMachineParser#out_port_list.
    def visitOut_port_list(self, ctx:StateMachineParser.Out_port_listContext, portdict):
        for outport in ctx.out_port_identifier():
            self.visitOut_port_identifier(outport, portdict)

    # Visit a parse tree produced by StateMachineParser#out_port_identifier.
    def visitOut_port_identifier(self, ctx:StateMachineParser.Out_port_identifierContext, portdict):
        portname = str(ctx.IDENTIFIER())
        logging.info(f'visiting port declaration {portname} in line {ctx.start.line}')
        if portname in portdict:
            raise DuplicatedPortDeclaration(portname,(self.filename_stack, ctx.start.line))
        port = { portname: {"type": "out port", "name": portname }}
        portdict |= port
            

    # Visit a parse tree produced by StateMachineParser#states_definition_body.
    def visitStates_definition_body(self, ctx:StateMachineParser.States_definition_bodyContext, statemachine, events):
        states = {}
        for state_ctx in ctx.state_definition():
            state = self.visitState_definition(state_ctx, events, statemachine )
            if state["name"] in states:
                raise DuplicatedStateDeclaration(state, states[state["name"]])
            states[state["name"]] = state
        statemachine["states"] = states

    # Visit a parse tree produced by StateMachineParser#state_definition.
    def visitState_definition(self, ctx:StateMachineParser.State_definitionContext, events, statemachine):
        statename = self.visitState_identifier(ctx.state_identifier())
        logging.info(f'visiting state declaration {statename} in line {ctx.start.line}')
        state = {"name": statename}
        state["declared_at"] = ctx.start.line
        state["declared_in"] = self.filename_stack
        state["functions"] = {}
        state["submachines"] = {}
        state["event transitions"] = {}
        state["auto transition"] = None
        joinstate = False
        splitstate = False
        if ctx.state_qualifier():
            (joinstate, splitstate) = self.visitState_qualifier(ctx.state_qualifier)
        if joinstate:
            state["type"] = "joinstate"
        elif splitstate:
            state["type"] = "splitstate"
        else:
            state["type"] = "state"
        self.visitState_body(ctx.state_body(),state, statemachine)

        return state

    # Visit a parse tree produced by StateMachineParser#state_body.
    def visitState_body(self, ctx:StateMachineParser.State_bodyContext,state, statemachine):
        for statement_ctx in ctx.state_statement():
            self.visitState_statement(statement_ctx, state, statemachine)


    # Visit a parse tree produced by StateMachineParser#state_statement.
    def visitState_statement(self, ctx:StateMachineParser.State_statementContext, state, statemachine):
        if ctx.state_function():
            self.visitState_function(ctx.state_function(), state, statemachine)
        elif ctx.sub_statemachine():
            self.visitSub_statemachine(ctx.sub_statemachine(), state, statemachine)
        else:
            raise SyntaxError
        

    # Visit a parse tree produced by StateMachineParser#sub_statemachine.
    def visitSub_statemachine(self, ctx:StateMachineParser.Sub_statemachineContext, state, statemachine):
        statemachinename = self.visitStatemachine_name(ctx.statemachine_name())
        if statemachinename not in self.json_rep["statemachines"]:
            raise UndefinedStatemachineUsage(statemachinename,(self.filename_stack, ctx.start.line))
        if ctx.statemachine_alias_name():
            alias = self.visitStatemachine_alias_name(ctx.statemachine_alias_name())
        else:
            alias = statemachinename
        if alias in state["submachines"]:
            raise DuplicatedStatemachineAlias(alias,state,(self.filename_stack,ctx.start.line))
        state["submachines"][alias] = statemachinename    

    # Visit a parse tree produced by StateMachineParser#statemachine_alias_name.
    def visitStatemachine_alias_name(self, ctx:StateMachineParser.Statemachine_alias_nameContext):
        return self.visitStatemachine_name(ctx.statemachine_name())

    # Visit a parse tree produced by StateMachineParser#state_function.
    def visitState_function(self, ctx:StateMachineParser.State_functionContext, state, statemachine):
        event = self.visitState_event(ctx.state_event(), statemachine["uses_events"])
        function = self.visitFunction_indentifier(ctx.function_indentifier())
        state["functions"][event] = function


    # Visit a parse tree produced by StateMachineParser#state_event.
    def visitState_event(self, ctx:StateMachineParser.State_eventContext, used_events):
        if ctx.entry():
            return self.visitEntry(ctx.entry())
        elif ctx.exit():
            return self.visitExit(ctx.exit())
        else:
            eventname = self.visitEvent_name(ctx.event_name())
            if eventname not in used_events:
                raise EventNotUsed(eventname, ( self.filename_stack ,ctx.start.line))
            return eventname

    # Visit a parse tree produced by StateMachineParser#state_qualifier.
    def visitState_qualifier(self, ctx:StateMachineParser.State_qualifierContext):
        if ctx.join():
            return (True,False)
        else:
            return (False,True)

    # Visit a parse tree produced by StateMachineParser#event_usage_body.
    def visitEvent_usage_body(self, ctx:StateMachineParser.Event_usage_bodyContext, events):
        used_events = []
        eventreturns = {}
        for event in ctx.event_use():
            (eventname, location) = self.visitEvent_use(event, events)
            if eventname in eventreturns:
                raise DuplicatedEventUsage(eventname, location, eventreturns[eventname][1])
            eventreturns[eventname] = (eventname, location)
            used_events.append(eventname)
        return used_events



    # Visit a parse tree produced by StateMachineParser#event_use.
    def visitEvent_use(self, ctx:StateMachineParser.Event_useContext, events):
        eventname = self.visitEvent_name(ctx.event_name())
        if eventname not in events:
            raise UndefinedEventUsage(eventname, (self.filename_stack, ctx.start.line))
        return (eventname, (self.filename_stack, ctx.start.line))

    # Visit a parse tree produced by StateMachineParser#member.
    def visitMember(self, ctx:StateMachineParser.MemberContext):
        member = {"type": "member"}
        membername = self.visitMembername(ctx.membername())
        logging.info(f'visiting member declaration {membername} in line {ctx.start.line}')
        typename = self.visitTypename(ctx.typename())
        member["name"] = membername
        member["type"] = typename
        return member
    


    # Visit a parse tree produced by StateMachineParser#function_indentifier.
    def visitFunction_indentifier(self, ctx:StateMachineParser.Function_indentifierContext):
        return str(ctx.IDENTIFIER())

     # Visit a parse tree produced by StateMachineParser#event_name.
    def visitEvent_name(self, ctx:StateMachineParser.Event_nameContext):
        return str(ctx.UPPERCASE_IDENTIFIER())


    # Visit a parse tree produced by StateMachineParser#typename.
    def visitTypename(self, ctx:StateMachineParser.TypenameContext):
        return str(ctx.IDENTIFIER())


    # Visit a parse tree produced by StateMachineParser#membername.
    def visitMembername(self, ctx:StateMachineParser.MembernameContext):
        return str(ctx.IDENTIFIER())
    
    # Visit a parse tree produced by StateMachineParser#statemachine_name.
    def visitStatemachine_name(self, ctx:StateMachineParser.Statemachine_nameContext):
        return str(ctx.IDENTIFIER())

    # Visit a parse tree produced by StateMachineParser#state_identifier.
    def visitState_identifier(self, ctx:StateMachineParser.State_identifierContext):
        return str(ctx.IDENTIFIER())


    # Visit a parse tree produced by StateMachineParser#entry.
    def visitEntry(self, ctx:StateMachineParser.EntryContext):
        return "entry"


    # Visit a parse tree produced by StateMachineParser#exit.
    def visitExit(self, ctx:StateMachineParser.ExitContext):
        return "exit"

    # Visit a parse tree produced by StateMachineParser#port_identifier.
    def visitPort_identifier(self, ctx:StateMachineParser.Port_identifierContext):
        return str(ctx.IDENTIFIER())


    def defaultResult(self):
        return []
    
    def aggregateResult(self, aggregate, nextResult):
        aggregate.append(nextResult)
        return aggregate
    
    def visitChildren(self, node):
        result = self.defaultResult()
        n = node.getChildCount()
        for i in range(n):
            if not self.shouldVisitNextChild(node, result):
                return result

            c = node.getChild(i)
            childResult = c.accept(self)
            result = self.aggregateResult(result, childResult)

        return result
   