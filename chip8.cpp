#include <iostream>
#include <vector>
#include <string>
#include "virtual_machine.h"

using namespace std;

VM chip8;

extern "C" {

  void runMachine(string programCode) {
    chip8.init();
    chip8.loadProgram(programCode);
  }

  bool* getGraphics() {
    return chip8.getGraphics();
  }

  uint8_t* getRegisters() {
    return chip8.getRegisters();
  }

}
