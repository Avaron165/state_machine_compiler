lexer grammar StateMachineLexer;


CURLY_OPEN          : '{' ;
CURLY_CLOSE         : '}' ;
BRACE_OPEN          : '(' ;
BRACE_CLOSE         : ')' ;
COLON               : ':' ;
SEMICOLON           : ';' ;
KOMMA               : ',' ;
EVENT               : 'event' ;
EVENTS              : 'events' ;
PORTS               : 'ports' ;
IN                  : 'in' ;
OUT                 : 'out' ;
STATES              : 'states' ;
ENTRY               : 'entry' ;
EXIT                : 'exit' ;
TRANSITIONS         : 'transitions' ;
AUTOMATIC           : 'automatic' ;
USES                : 'uses' ;
DATA                : 'data' ;
ARROW               : '->' ;
STATEMACHINE        : 'statemachine' ;
HISTORY             : 'history' ;
DEEPHISTORY         : 'deephistory' ;
INCLUDE             : 'include' ;
AS                  : 'as' ;
DOT                 : '.' ;
JOIN                : 'join' ;
SPLIT               : 'split' ;
UPPERCASE_IDENTIFIER : [A-Z_]+ ;
IDENTIFIER : [a-zA-Z_][a-zA-Z_0-9]* ;
FILE                : '<' .*? '>' ;
WS                  : [ \t\r\n] -> skip ;
LINE_COMMENT        : '#' ~[\r\n]* -> skip ;
fragment UPPERCASE_LETTERS : [A-Z] ;
fragment LETTERS    : [a-zA-Z] ;
