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
  cout<<"Program Code loaded: "<<code;
}

bool VM::hasNext() {
  return false;
}

void VM::tick() {
}

bool* VM::getGraphics() {
  return graphics;
}

uint8_t* VM::getRegisters() {
  return reg;
}

uint16_t VM::getIRegister() {
  return i_reg;
}

uint16_t VM::getPCRegister() {
  return pc_reg;
}
