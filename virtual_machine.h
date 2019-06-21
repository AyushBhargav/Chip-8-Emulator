#ifndef VIRTUAL_MACHINE_H
#define VIRTUAL_MACHINE_H
#pragma once

#include <iostream>
#include <stack>

class VM {
    
public:
    /* Memory */
    uint8_t memory[4096];
    uint8_t reg[16];
    uint16_t i_reg, pc_reg;
    stack<uint8_t> vm_stack;

    /* Graphics */
    bool graphics[2048];

    /* Timers */
    uint8_t delay_timer, sound_timer;

    /* Inputs */
    bool input[16];

    VM() {
        std::fill(memory, memory + 4096, 0);
        std::fill(reg, reg + 16, 0);
        i_reg = pc_reg = 0;
        std::fill(graphics, graphics + 2048, false);
        delay_timer = sound_timer = 0;
        std::fill(input, input + 16, false);
    }

};

#endif 