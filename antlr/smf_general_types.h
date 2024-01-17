#pragma once

typedef enum smf_return_e {
    SMF_RETURN_OK = 0,
    SMF_RETURN_STATEMACHINE_FINISHED = 1,
    SMF_RETURN_INTERNAL_ERROR = 10,
} smf_return_t;