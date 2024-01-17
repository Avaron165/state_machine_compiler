from StateMachineObject import State, StartState, EndState, PortState, HistoryState, DeepHistoryState, PortDirection, SubmachinePort

class PlantUmlWriter:
    def __init__(self, file):
        self.file = file
        self.state_writers = {}
        self.state_writers[State] = self.plainStateWriter
        self.state_writers[StartState] = self.silentStateWriter
        self.state_writers[EndState] = self.silentStateWriter
        self.state_writers[PortState] = self.portStateWriter
        self.state_writers[HistoryState] = self.silentStateWriter
        self.state_writers[DeepHistoryState] = self.silentStateWriter
        self.state_writers[SubmachinePort] = self.silentStateWriter

    def output(self,indent,string):
        indent_string = ""
        for idx in range(indent):
            indent_string += " ";
        print(f'{indent_string}{string}', file=self.file)

    def writeStatemachine(self, statemachine):
        self.output(0, "@startuml")
        self.writeStatemachineBody(2,statemachine,"")
        self.output(0, "@enduml")

    def writeStatemachineBody(self, indent, statemachine, owner):
        self.output(indent,f'state {owner}{statemachine.name} #LightBlue {{')
        for (statename, state) in statemachine.states.items():
            self.writeState(indent+2,state,f'{owner}{statemachine.name}.')
        for state in statemachine.states.values():
            self.writeStateTransitions(indent+2, state, f'{owner}{statemachine.name}.') 
        self.output(indent, f'}}')

    def writeStateTransitions(self, indent, state, owner):
        if (state.name == "start") or (state.name == "end" ): 
            statename = f'[*]'
        else:
            statename = f'{owner}{state.name}'
        for transition in state.transitions.values():
            event_function_string = ""
            if transition.event != "automatic":
                event_function_string = f'{transition.event}'
            if transition.function:
                event_function_string += f' [{transition.function}()]'
            if event_function_string != "":
                event_function_string = " : " + event_function_string
            self.output(indent, f'{statename} --> {owner}{transition.toState}{event_function_string}')

    def writeState(self, indent, state, owner):
        self.state_writers[type(state)](indent, state, owner)

    def plainStateWriter(self, indent, state, owner):
        self.output(indent,f'state {owner}{state.name} #Lime {{')
        for (event, function) in state.functions.items():
            self.output(indent+2,f'{state.name}: {event}: {function}()')
        submachine_count = len(state.statemachines)    
        for (statemachine_name, statemachine) in state.statemachines.items():
            self.writeStatemachineBody(indent+2,statemachine,f'{owner}{state.name}.')
            submachine_count -= 1
            if submachine_count > 0:
                self.output(indent+2,"---")

        self.output(indent,f'}}')

    def portStateWriter(self, indent, state, owner):
        if state.direction == PortDirection.IN:
            self.output(indent,f'state {owner}{state.name} <<inputPin>>')
        else:
            self.output(indent,f'state {owner}{state.name} <<outputPin>>')

    def silentStateWriter(self, indent, state, owner):
        pass
