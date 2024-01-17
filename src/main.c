#include "smf_calculator.h"
#include <stdbool.h>

int main()
{
    smf_calculator__private_t testinstance;

    smf_calculator_start(&testinstance);

    smf_calculator_event_t event;
    bool event_consumed = false;

    event.id = SMF_EVENT_CALCULATOR_OFF;

    smf_calculator_process_until_next_event(&testinstance, &event, &event_consumed);
}