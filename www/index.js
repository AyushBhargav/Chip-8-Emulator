Module.onRuntimeInitialized = _ => {
    const runMachine = Module.cwrap('runMachine', null, ['string']);
    const getRegisters = Module.cwrap('getGraphics', 'number', []);
    runMachine("Some good old code.");
    let regs = getRegisters();
    console.log(regs);
}
