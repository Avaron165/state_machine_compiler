from jinja2 import Environment, FileSystemLoader
env = Environment(
    loader=FileSystemLoader("templates/"),
    trim_blocks = True,
    lstrip_blocks= True
)

type_header_template = env.get_template("statemachine_types_header.j2")
implementation_template = env.get_template("statemachine_implementation.j2")
machine_header_template = env.get_template("statemachine_header.j2")
function_header_template = env.get_template("statemachine_function_header.j2")

class CCodeWriter:
    def __init__(self):
        self.org_data = {}

    def writeStatemachine(self, statemachine):
        self.org_data["module_name"] = statemachine.name + " Statemachine"

        type_header_file_name = f'smf_{ statemachine.name.lower() }_types.h'
        type_header_file = open(type_header_file_name, "w")
        print(type_header_template.render(org_data=self.org_data, statemachine=statemachine), file=type_header_file)

        implementation_file_name = f'smf_{ statemachine.name.lower() }_implementation.c'
        implementation_file = open(implementation_file_name, "w")
        print(implementation_template.render(org_data=self.org_data, statemachine=statemachine), file=implementation_file)

        header_file_name = f'smf_{ statemachine.name.lower() }.h'
        header_file = open(header_file_name, "w")
        print(machine_header_template.render(org_data=self.org_data, statemachine=statemachine), file=header_file)

        function_header_file_name = f'smf_{ statemachine.name.lower() }_functions.h'
        function_header_file = open(function_header_file_name, "w")
        print(function_header_template.render(org_data=self.org_data, statemachine=statemachine), file=function_header_file)



    def writeStatemachineRecursive(self, statemachine):
        self.writeStatemachine(statemachine)
        for (statename, state) in statemachine.states.items():
            for (submachinename,submachine) in state.statemachines.items():
                self.writeStatemachine(submachine)

