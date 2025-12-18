#pragma once

#include <stdint.h>
#include <stdbool.h>

struct cht_last_key_info {
    uint32_t keycode;
    int64_t timestamp;
    bool valid;
};

struct cht_last_key_info cht_get_last_key_info(void);
void cht_record_last_key(uint32_t keycode, int64_t timestamp);
