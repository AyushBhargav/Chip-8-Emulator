window.Module = {};
fetch("./chip8.wasm")
    .then(response => response.arrayBuffer())
    .then(bytes => WebAssembly.instantiate(bytes))
    .then(Module => {
        let exports = Module.instance.exports;
        init(exports.memory, exports.get_chip8_fontset, exports.get_memory, exports.get_graphics, exports.get_registers, exports.cpu_cycle);
    });

// When wasm has been loaded then initialize the program.
let init = function(sharedMemory, get_chip8_fontset, get_memory, get_graphics, get_registers, cpu_cycle) {
    let memory = new Uint8Array(sharedMemory.buffer, get_memory(), 4096);
    let fontset = new Uint8Array(sharedMemory.buffer, get_chip8_fontset(), 80);
    let graphics = new Uint8Array(sharedMemory.buffer, get_graphics(), 64 * 32);
    let registers = new Uint8Array(sharedMemory.buffer, get_registers(), 16);

    graphics[6] = true;
    // Setting up canvas to draw.
    let canvas = document.getElementById('canvas');
    let ctx = canvas.getContext('2d');

    for (let i = 0; i < 80; i++) {
        memory[i] = fontset[i];
    }

    // Init UI for debugging.
    initRegisterUI();

    // Game Loop
    let loop = function() {
        clearFrame(ctx);
        renderFrame(ctx, graphics);
        showRegisters(registers);
        window.requestAnimationFrame(loop);
    }

    loop();
};

let initRegisterUI = function() {
    let registerTable = document.getElementById('register_table');
    for(let i = 0; i < 16; i++) {
        let content = `<tr><td>V${i}</td><td id='V${i}'></td></tr>`;
        registerTable.innerHTML += content;
    }
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