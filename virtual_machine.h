#ifndef VIRTUAL_MACHINE_H
#define VIRTUAL_MACHINE_H
#pragma once

#include <iostream>
#include <stack>

using namespace std;

class VM {

 private:
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

 public:
  void init();
  void loadProgram(string);
  bool hasNext();
  void tick();
  bool* getGraphics();
  uint8_t* getRegisters();
  uint16_t getIRegister();
  uint16_t getPCRegister();
};

#endif
