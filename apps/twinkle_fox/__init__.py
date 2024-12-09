### Converted TwinkleFox for MicroPython Badge
import rgb

DEBUG = True
import random
import time
from .display_helper import reset_buffer, prepare_pixel_global, render_image_buffer, WIDTH, HEIGHT

# Configuration
NUM_LEDS = WIDTH * HEIGHT
TWINKLE_SPEED = 4
TWINKLE_DENSITY = 5
SECONDS_PER_PALETTE = 30

# Palettes
palettes = [
    [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)],  # Example palette
    [(255, 255, 0), (0, 255, 255), (255, 0, 255), (128, 128, 128)]
]
current_palette_index = 0

# Pixel state list
active_pixels = []

# Utility functions
def choose_next_palette():
    global current_palette_index
    current_palette_index = (current_palette_index + 1) % len(palettes)


def get_current_palette():
    return palettes[current_palette_index]


def initialize_active_pixels():
    """Initialize a subset of pixels to be active."""
    global active_pixels
    active_pixels = []
    for _ in range(NUM_LEDS // 4):  # Only 1 in 4 pixels are active
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        state = {
            "x": x,
            "y": y,
            "brightness": random.randint(0, 255),
            "direction": "brightening" if random.choice([True, False]) else "fading",
            "color": random.choice(get_current_palette()),
            "threshold": random.randint(0, 255)
        }
        active_pixels.append(state)


def update_active_pixels():
    """Update the state of each active pixel."""
    global active_pixels
    for pixel in active_pixels:
        if pixel["direction"] == "brightening":
            pixel["brightness"] += TWINKLE_SPEED
            if pixel["brightness"] >= pixel["threshold"]:
                pixel["brightness"] = pixel["threshold"]
                pixel["direction"] = "fading"
        elif pixel["direction"] == "fading":
            pixel["brightness"] -= TWINKLE_SPEED
            if pixel["brightness"] <= 0:
                pixel["brightness"] = 0
                pixel["direction"] = "brightening"
                pixel["color"] = random.choice(get_current_palette())
                pixel["threshold"] = random.randint(0, 255)

                # Assign a new random position
                pixel["x"] = random.randint(0, WIDTH - 1)
                pixel["y"] = random.randint(0, HEIGHT - 1)


def buffer_twinkles():
    """Buffer one frame of the twinkle animation."""
    reset_buffer()
    for pixel in active_pixels:
        color = tuple(c * pixel["brightness"] // 255 for c in pixel["color"])
        prepare_pixel_global((pixel["x"], pixel["y"]), color)



def main():
    global current_palette_index

    start_time = time.time()
    initialize_active_pixels()

    while True:
        if time.time() - start_time > SECONDS_PER_PALETTE:
            choose_next_palette()
            start_time = time.time()

        update_active_pixels()
        buffer_twinkles()
        time.sleep(0.03)
        rgb.clear()
        render_image_buffer()

main()
