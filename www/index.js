window.Module = {};
fetch("./chip8.wasm")
    .then(response => response.arrayBuffer())
    .then(bytes => WebAssembly.instantiate(bytes))
    .then(Module => {
        let exports = Module.instance.exports;
        init(exports.memory, exports.get_chip8_fontset, exports.get_memory, exports.get_graphics, exports.get_registers, exports.get_inputs, exports.cpu_cycle);
    });

// When wasm has been loaded then initialize the program.
let init = function(sharedMemory, get_chip8_fontset, get_memory, get_graphics, get_registers, get_inputs, cpu_cycle) {
    let memory = new Uint8Array(sharedMemory.buffer, get_memory(), 4096);
    let fontset = new Uint8Array(sharedMemory.buffer, get_chip8_fontset(), 80);
    let graphics = new Uint8Array(sharedMemory.buffer, get_graphics(), 64 * 32);
    let registers = new Uint8Array(sharedMemory.buffer, get_registers(), 16);
    let inputs = new Uint8Array(sharedMemory.buffer, get_inputs, 16);

    graphics[6] = true;
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

    // Game Loop
    let loop = function() {
        for(let i = 0; i < 10; i++) {
            clearFrame(ctx);
            renderFrame(ctx, graphics);
            showRegisters(registers);
            cpu_cycle();
        }
        console.log("RAM", memory);
        // window.requestAnimationFrame(loop);
    }

    // TODO: Support for all roms.
    let romPath = `./roms/jason.ch8`;
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

let showRegisters = function(registers) {
    for(let i = 0; i < 16; i++) {
        let v = document.getElementById(`V${i}`);
        v.innerText = registers[i];
    }
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
