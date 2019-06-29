
pub struct VirtualMachine {
    // RAM for CPU (4K bytes of memory)
    pub memory: [u8; 4096],
    // Registers from V0 to VF. VF will hold the carry flags for computations.
    pub registers: [u8; 16],
    // Index register
    pub index_register: u16,
    // Program counter
    pub program_counter: u16,
    // Graphics for (64 * 32) pixels
    pub video: [bool; 64 * 32],
    // Keypad for 16 buttons
    pub keypad: [bool; 16],
    // Timer registers
    pub delay_timer: u8,
    pub sound_timer: u8, // Sounds a buzzer like sound whenver it reaches zero.
    // Program stack. Chip-8 can only go upto 16 level deep.
    pub stack: [u16; 16],
    pub stack_top: i8
}

fn fetch_instruction(memory: [u8; 4096], program_counter: u16) -> u16{
    // Each opcode consists of two bytes. Second operand is casted as u16 as u16 | u8 is noit permissible. :(
    let opcode: u16 = ((memory[program_counter as usize] as u16) << 8) | (memory[(program_counter + 1) as usize] as u16);
    opcode
}

impl VirtualMachine {

    fn execute_op(&mut self, opcode: u16) {
        match opcode {
            // Jump statement.
            0x1000 ... 0x1FFF => self.program_counter = (opcode & 0xFFF),
            // Call the subroutine statement.
            0x2000 ... 0x2FFF => {
                self.stack[self.stack_top as usize] = self.program_counter;
                self.stack_top += 1;
                self.program_counter = opcode * 0xFFF;
            },
            // Skip next instruction if given register equals the operand.
            0x3000 ... 0x3FFF => {
                let x: u8 = ((opcode & 0xF00) as u8) >> 8;
                let vx: u8 = self.registers[x as usize];
                if vx == (opcode & 0xFF) as u8 {
                    self.program_counter += 4; // Skip 4 bytes.
                }
            },
            // Skip next instruction if given register doesn't equal the operand.
            0x4000 ... 0x4FFF => {
                let x: u8 = ((opcode & 0xF00) as u8) >> 8;
                let vx: u8 = self.registers[x as usize];
                if vx != (opcode & 0xFF) as u8 {
                    self.program_counter += 4; // Skip 4 bytes.
                }
            },
            // Skip next instruction if given registers aren't equal.
            0x5000 ... 0x5FFF => {
                let x: u8 = ((opcode & 0xF00) as u8) >> 8;
                let vx: u8 = self.registers[x as usize];
                let y: u8 = (opcode & 0xFF) as u8;
                let vy: u8 = self.registers[y as usize];
                if vx == vy {
                    self.program_counter += 4; // Skip 4 bytes.
                }
            },
            // Set given operand to specified register.
            0x6000 ... 0x6FFF => {
                let x: u8 = ((opcode & 0xF00) as u8) >> 8;
                self.registers[x as usize] = (opcode & 0xFF) as u8;
                self.program_counter += 2;
            },
            // Add given operand to specified register.
            0x7000 ... 0x7FFF => {
                let x: u8 = ((opcode & 0xF00) as u8) >> 8;
                self.registers[x as usize] += (opcode & 0xFF) as u8;
                self.program_counter += 2;
            },
            // TODO: Continue from here.
        }
    }

    // Single CPU cycle
    #[no_mangle]
    pub fn tick(&mut self) {
        let opcode = fetch_instruction(self.memory, self.program_counter);
        self.execute_op(opcode);
    }
}

// Static objects which will be interfaced with Javascript.
static mut CHIP8: VirtualMachine = VirtualMachine {
    memory: [0; 4096],
    registers: [0; 16],
    index_register: 0,
    // Programs start at memory location of 0x200.
    program_counter: 0x200,
    // Blank screen at the start.
    video: [false; 64 * 32],
    keypad: [false; 16],
    delay_timer: 0,
    sound_timer: 0,
    // Empty Stack.
    stack: [0; 16],
    stack_top: -1
};

#[no_mangle]
pub fn cpu_cycle() {
    unsafe {
        CHIP8.tick();
    }
}

#[no_mangle]
pub fn get_graphics() -> &'static [bool; 64 * 32] {
    unsafe {
        &CHIP8.video
    }
}

#[no_mangle]
pub fn get_memory() -> &'static [u8; 4096] {
    unsafe {
        &CHIP8.memory
    }
}

fn main() {
    println!("Hello, world!");
}
