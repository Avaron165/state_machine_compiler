import sys
from antlr4 import *
from StateMachineLexer import StateMachineLexer
from StateMachineParser import StateMachineParser
from StateMachineObjectVisitor import StateMachineObjectVisitor
from PlantUmlWriter import PlantUmlWriter
import sys

from CCodeWriter import CCodeWriter

def main(argv):
    print(argv[1])
    input = FileStream(argv[1])
    lexer = StateMachineLexer(input)
    stream = CommonTokenStream(lexer)
    parser = StateMachineParser(stream)
    tree = parser.statemachine()
    
    statemachine_visitor= StateMachineObjectVisitor() 
    statemachine_object = statemachine_visitor.visitStatemachine(tree)
#    statemachine_object.print_with_indent(0)
#    puml_writer = PlantUmlWriter(sys.stdout)
#    puml_writer.writeStatemachine(statemachine_object)

    c_header_writer = CCodeWriter()
    c_header_writer.writeStatemachineRecursive(statemachine_object)

if __name__ == '__main__':
    main(sys.argv)