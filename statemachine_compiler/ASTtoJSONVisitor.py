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

class UndefinedEventUsage(StatemachineParserException):
    def __init__(self, eventname, location):
        error_string =    f'{location[0][-1]}: line {location[1]} -- undefined event {eventname}\n'
        super().__init__(error_string)

class DuplicatedEventUsage(StatemachineParserException):
    def __init__(self, eventname, location1, location2):
        error_string =    f'{location1[0][-1]}: line {location1[1]} -- duplicated usage of event {eventname}\n'
        error_string +=   f'   previously used in {location2[0][-1]}: line {location2[1]}'      
        super().__init__(error_string)

class ASTtoJSONVisitor(StateMachineParserVisitor):

    def __init__(self, filename):
        self.filename_stack = []
        self.filename_stack.append( (filename, None) )

    # Visit a parse tree produced by StateMachineParser#file.
    def visitFile(self, ctx:StateMachineParser.FileContext):
        json_rep = { "events": {}, "statemachines": {} }
        for event in ctx.event_declaration_block():
            new_event = self.visitEvent_declaration_block(event, json_rep)
            new_event_name = new_event["name"]
            json_rep["events"][new_event_name] = new_event
        for statemachine in ctx.statemachine():
            new_statemachine = self.visitStatemachine(statemachine, json_rep)
            new_statemachine_name = new_statemachine["name"]
            json_rep["statemachines"][new_statemachine_name] = new_statemachine
        return json_rep
    
    # Visit a parse tree produced by StateMachineParser#event_declaration_block.
    def visitEvent_declaration_block(self, ctx:StateMachineParser.Event_declaration_blockContext, json_rep):
        event = {"type": "event"}
        eventname = self.visitEvent_name(ctx.event_name())
        logging.info(f'visiting event declaration {eventname} in line {ctx.start.line}')
        event["name"] = eventname
        event["declared_at"] = ctx.start.line
        event["declared_in"] = self.filename_stack
        if eventname in json_rep["events"]:
            raise DuplicatedEventDeclaration(event, json_rep["events"][eventname])
        members = []
        for member_node in ctx.member():
            members.append(self.visitMember(member_node))
        if members:
            event["members"] = members
        return event

    # Visit a parse tree produced by StateMachineParser#statemachine.
    def visitStatemachine(self, ctx:StateMachineParser.StatemachineContext, json_rep):
        statemachine = {"type": "statemachine"}
        statemachine_name = self.visitStatemachine_name(ctx.statemachine_name())
        logging.info(f'visiting statemachine declaration {statemachine_name} in line {ctx.start.line}')
        statemachine["name"] = statemachine_name
        statemachine["declared_at"] = ctx.start.line
        statemachine["declared_in"] = self.filename_stack
        if statemachine_name in json_rep["statemachines"]:
            raise DuplicatedStatemachineDeclaration(statemachine, json_rep["statemachines"][statemachine_name])
        self.visitStatemachine_body(ctx.statemachine_body(), statemachine, json_rep)
        return statemachine


    # Visit a parse tree produced by StateMachineParser#statemachine_body.
    def visitStatemachine_body(self, ctx:StateMachineParser.Statemachine_bodyContext, statemachine, json_rep):
        if ctx.event_usage_body():
            used_list = self.visitEvent_usage_body(ctx.event_usage_body(), json_rep["events"])
            statemachine["uses_events"] = used_list

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
   