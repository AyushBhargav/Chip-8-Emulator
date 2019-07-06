window.Module = {};
fetch("./chip8.wasm")
    .then(response => response.arrayBuffer())
    .then(bytes => WebAssembly.instantiate(bytes))
    .then(Module => {
        let exports = Module.instance.exports;
        init(exports.memory, exports.get_chip8_fontset, exports.get_memory, exports.get_graphics
            , exports.get_registers, exports.get_ic, exports.get_pc, exports.get_inputs, exports.decrement_counter, exports.play_sound, exports.cpu_cycle);
    });

// When wasm has been loaded then initialize the program.
let init = function(sharedMemory, get_chip8_fontset, get_memory, get_graphics, get_registers, get_ic, get_pc, get_inputs, decrement_counter, play_sound, cpu_cycle) {
    // Set Panic hook for rust for debugging.
    // set_panic_hook();
    let memory = new Uint8Array(sharedMemory.buffer, get_memory(), 4096);
    let fontset = new Uint8Array(sharedMemory.buffer, get_chip8_fontset(), 80);
    let graphics = new Uint8Array(sharedMemory.buffer, get_graphics(), 64 * 32);
    let registers = new Uint8Array(sharedMemory.buffer, get_registers(), 16);
    let inputs = new Uint8Array(sharedMemory.buffer, get_inputs(), 16);

    // Setting up canvas to draw.
    let canvas = document.getElementById('canvas');
    let ctx = canvas.getContext('2d');

    for (let i = 0; i < 80; i++) {
        memory[i] = fontset[i];
    }

    // Init UI for debugging.
    initRegisterUI();

    // Init for input.
    initInput(inputs);

    console.log(memory);
    // Game Loop
    let loop = function() {
        for(let i = 0; i < 10; i++) {
            clearFrame(ctx);
            renderFrame(ctx, graphics);
            showRegisters(registers, get_ic(), get_pc());
            if(play_sound()) {
                console.log("Beep");
            }
            cpu_cycle();
        }
        decrement_counter();
        window.requestAnimationFrame(loop);
    }

    // TODO: Support for all roms.
    let romPath = `./roms/Maze.ch8`;
    fetch(romPath)
    .then(response => response.arrayBuffer())
    .then(buffer => {
        // Load program code in RAM.
        const rom = new DataView(buffer, 0, buffer.byteLength);
        for(let i = 0; i < rom.byteLength; i++) 
            memory[0x200 + i] = rom.getUint8(i);
        // Start the game loop.
        loop();
    });
};

let initRegisterUI = function() {
    let registerTable = document.getElementById('register_table');
    for(let i = 0; i < 16; i++) {
        let content = `<tr><td>V${i}</td><td id='V${i}'></td></tr>`;
        registerTable.innerHTML += content;
    }
}

let initInput = function(inputs) {
    let keyDict = {
        '1' : 0, '2' : 1, '3' : 2, '4' : 3,
        'q' : 4, 'w': 5, 'e': 6, 'r': 7,
        'a': 8, 's': 9, 'd': 10, 'f': 11,
        'z': 12, 'x': 13, 'c': 14, 'v': 15
    }

    document.onkeydown = function(e) {
        e = e || window.event;
        let key = String.fromCharCode(e.keyCode);
        inputs[keyDict[key]] = 1;
    };

    document.onkeyup = function(e) {
        let key = String.fromCharCode(e.keyCode);
        inputs[keyDict[key]] = 0;
    };
}

let showRegisters = function(registers, index_counter, program_counter) {
    for(let i = 0; i < 16; i++) {
        let v = document.getElementById(`V${i}`);
        v.innerText = registers[i];
    }
    let ic = document.getElementById("ic");
    ic.innerHTML = index_counter;
    let pc = document.getElementById("pc");
    pc.innerHTML = program_counter;
}   

let clearFrame = function(ctx) {
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, 320, 160);
};

let renderFrame = function(ctx, graphics) {
    ctx.fillStyle = 'yellow';

    let index = 0;
    for(let i = 0; i < 32; i++) {
        for(let j = 0; j < 64; j++) {
            if(graphics[index])
                ctx.fillRect(j * 5, i * 5, 5, 5);
            index++;
        }
    }
};
