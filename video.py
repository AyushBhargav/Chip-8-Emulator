import pygame

cell_size = 10

keys = {
    pygame.K_0: 0,
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_q: 4,
    pygame.K_w: 5,
    pygame.K_e: 6,
    pygame.K_r: 7,
    pygame.K_a: 8,
    pygame.K_s: 9,
    pygame.K_d: 10,
    pygame.K_f: 11,
    pygame.K_z: 12,
    pygame.K_x: 13,
    pygame.K_c: 14,
    pygame.K_v: 15
}

def start_loop(chip8):
    pygame.init()

    size = width, height = 64 * cell_size, 32 * cell_size
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    emulation_complete = False

    while not emulation_complete:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                emulation_complete = True
            get_input_event(event, chip8.input)

        pygame.display.flip()
        screen.fill((0, 0, 0)) # Clears screen
        draw(screen, chip8.graphics)
        clock.tick(60)


def draw(screen, graphics):
    for i in range(0, 64 * 32):
        if not graphics[i]:
            continue
        x = int(i % 64)
        y = int(i / 64)
        pygame.draw.rect(screen, (255, 255, 255), 
            pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))

def get_input_event(event, input_keys):
    try:
        if event.type == pygame.KEYUP:
            input_keys[keys[event.key]] = False
        elif event.type == pygame.KEYDOWN:
            input_keys[keys[event.key]] = True
    except KeyError:
        pass
    