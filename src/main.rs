
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
    let opcode: u16 = ((memory[program_counter as usize]) as u16 << 8) | (memory[(program_counter + 1) as usize] as u16);
    program_counter += 2;
    opcode
}

impl VirtualMachine {

    fn execute_op(&mut self, opcode: u16) {
    }

    // Single CPU cycle
    #[no_mangle]
    pub fn tick(&mut self) {
        let opcode = fetch_instruction(self.memory, self.program_counter);
        self.execute_op(opcode);
    }
}

static mut Chip: VirtualMachine = VirtualMachine {
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

fn main() {
    println!("Hello, world!");
}
