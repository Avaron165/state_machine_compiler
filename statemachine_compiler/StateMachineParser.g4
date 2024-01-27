parser grammar StateMachineParser;
options { tokenVocab=StateMachineLexer; }

file : (include_statement | event_declaration_block | statemachine)+ ;

event_declaration_block : EVENT event_name ( CURLY_OPEN member* CURLY_CLOSE )? SEMICOLON ;

member :  typename membername SEMICOLON ; 

include_statement : INCLUDE FILE SEMICOLON ;

statemachine : STATEMACHINE statemachine_name CURLY_OPEN statemachine_body CURLY_CLOSE SEMICOLON ;

statemachine_name : IDENTIFIER ;

statemachine_body : event_usage_body? port_definition_body? states_definition_body transitions_definition_body data_definition_body?;

data_definition_body : DATA COLON (member)* ;

event_usage_body : EVENTS COLON event_use+ ;

event_use : USES event_name SEMICOLON ;

event_name : UPPERCASE_IDENTIFIER ;

typename : IDENTIFIER ;

membername : IDENTIFIER ;

port_definition_body : PORTS COLON port_in_block? port_out_block? ;

port_in_block : IN COLON in_port_list ;

port_out_block : OUT COLON out_port_list ;

in_port_list : ( in_port SEMICOLON)+ ;

in_port : in_port_identifier | history | deephistory ;

in_port_identifier : IDENTIFIER ;

history : HISTORY ;

deephistory : DEEPHISTORY ;

out_port_list : (out_port_identifier SEMICOLON)+ ;

out_port_identifier : IDENTIFIER ;

state_identifier : IDENTIFIER ;

states_definition_body : STATES COLON state_definition+ ;

state_definition : (state_qualifier)? state_identifier CURLY_OPEN state_body CURLY_CLOSE SEMICOLON ;

state_qualifier : join | split ;

join : JOIN ;

split : SPLIT ;

state_body : state_statement*; 

state_statement : state_function | sub_statemachine ;

sub_statemachine : STATEMACHINE statemachine_name (AS statemachine_alias_name)? SEMICOLON ;

statemachine_alias_name : statemachine_name ;

state_function : state_event COLON function_indentifier SEMICOLON ;

function_indentifier : IDENTIFIER BRACE_OPEN BRACE_CLOSE ;

state_event : entry | exit | event_name ;

entry : ENTRY ;

exit : EXIT ;

transitions_definition_body : TRANSITIONS COLON transition+ ;

transition : event_classifier COLON from_state ARROW to_state (COLON function_indentifier)? SEMICOLON ;

from_state : state_identifier | (statemachine_name DOT port_identifier) ;

port_identifier : IDENTIFIER ;

to_state : state_identifier | (statemachine_name DOT in_port) ;

event_classifier : event_name | automatic ;

automatic : AUTOMATIC ;