window.Module = {};
fetch("./chip8.wasm")
    .then(response => response.arrayBuffer())
    .then(bytes => WebAssembly.instantiate(bytes))
    .then(Module => {
        console.log("Graphics", Module.instance.exports.get_graphics());
    });
