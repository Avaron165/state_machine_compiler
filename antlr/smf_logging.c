#include "smf_logging.h"
#include <stdio.h>

void smf__log_transition(const char* str)
{
    printf("TRANSITION: %s\n",str);
}

void smf__log_state_function(const char* str)
{
    printf("STATE FUNCTION: %s\n",str);
}

void smf__log_event(const char* str)
{
    printf("TRANSITION: %s\n",str);
}
