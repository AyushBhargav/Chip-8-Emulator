#pragma once
#include <iostream>
#include "virtual_machine.h"

using namespace std;

void VM::init() {
    std::fill(memory, memory + 4096, 0);
    std::fill(reg, reg + 16, 0);
    i_reg = pc_reg = 0;
    std::fill(graphics, graphics + 2048, false);
    delay_timer = sound_timer = 0;
    std::fill(input, input + 16, false);
}

void VM::loadProgram(string code) {
    // Do something here.
}

bool VM::hasNext() {
    return false;
}

bool VM