window.Module = {};
fetch("./chip8.wasm")
    .then(response => response.arrayBuffer())
    .then(bytes => WebAssembly.instantiate(bytes))
    .then(Module => {
        let exports = Module.instance.exports;
        init(exports.memory, exports.get_chip8_fontset, exports.get_memory, exports.get_graphics, exports.cpu_cycle);
    });

// When wasm has been loaded then initialize the program.
let init = function(sharedMemory, get_chip8_fontset, get_memory, get_graphics, cpu_cycle) {
    let memory = new Uint8Array(sharedMemory.buffer, get_memory(), 4096);
    let fontset = new Uint8Array(sharedMemory.buffer, get_chip8_fontset(), 80);

    for (let i = 0; i < 80; i++) {
        memory[i] = fontset[i];
    }

    // Game Loop
    let loop = function() {
        window.requestAnimationFrame(loop);
    }

    loop();
}
