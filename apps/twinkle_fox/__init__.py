### Converted TwinkleFox for MicroPython Badge
import rgb

DEBUG = True
import random
import time
from .display_helper import reset_buffer, prepare_pixel_global, prepare_pixel_global_int, render_image_buffer, WIDTH, HEIGHT

# Configuration
NUM_LEDS = WIDTH * HEIGHT
TWINKLE_SPEED = 1
TWINKLE_DENSITY = 1
SECONDS_PER_PALETTE = 30

# Palettes
palettes = [
    [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)],  # Example palette
    [(255, 255, 0), (0, 255, 255), (255, 0, 255), (128, 128, 128)]
]
current_palette_index = 0

# Utility functions
def choose_next_palette():
    global current_palette_index
    current_palette_index = (current_palette_index + 1) % len(palettes)


def get_current_palette():
    return palettes[current_palette_index]


def twinkle_color(clock_offset, salt):
    """Compute the color and brightness for a pixel based on time and randomness."""
    ticks = (int(time.time() * 1000) >> (8 - TWINKLE_SPEED)) + clock_offset
    brightness_wave = abs((ticks % 256) - 128)  # Triangle wave
    brightness = max(0, min(255, brightness_wave * TWINKLE_DENSITY))
    palette = get_current_palette()
    color = random.choice(palette)
    scaled_color = tuple(min(255, c * brightness // 255) for c in color)
    return scaled_color


def buffer_twinkles():
    """Buffer one frame of the twinkle animation."""
    reset_buffer()
    index = 0
    while True:
        if(index >= NUM_LEDS):
            break
        clock_offset = random.randint(0, 1000)
        salt = random.randint(0, 255)
        color = twinkle_color(clock_offset, salt)
        prepare_pixel_global_int(index, color)
        index += random.randint(1, 5)


def main():
    global current_palette_index

    start_time = time.time()

    while True:
        if time.time() - start_time > SECONDS_PER_PALETTE:
            choose_next_palette()
            start_time = time.time()
        buffer_twinkles()
        rgb.clear()
        render_image_buffer()
        time.sleep(0.1)

main()
