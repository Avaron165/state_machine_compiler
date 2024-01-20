import sys
from antlr4 import *
from StateMachineLexer import StateMachineLexer
from StateMachineParser import StateMachineParser
import sys
import logging
import json

from ASTtoJSONVisitor import ASTtoJSONVisitor, StatemachineParserException


def main(argv):
    input = FileStream(argv[1])
    lexer = StateMachineLexer(input)
    stream = CommonTokenStream(lexer)
    parser = StateMachineParser(stream)
    tree = parser.file_()
    
    statemachine_visitor= ASTtoJSONVisitor(argv[1])
    try: 
        print(json.dumps(statemachine_visitor.visitFile(tree)))
    except StatemachineParserException as e:
        logging.error(e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv)