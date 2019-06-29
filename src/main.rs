
pub struct Stack {
    // Chip-8 can only go upto 16 level deep.
    pub data: [u16; 16],
    pub top: u8
}

pub struct CPU {
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
    // Timer registers
    pub delay_timer: u8,
    pub sound_timer: u8, // Sounds a buzzer like sound whenver it reaches zero.
    // Program stack
    pub stack: Stack
}

fn main() {
    println!("Hello, world!");
}
