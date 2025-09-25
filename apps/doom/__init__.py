### Simple DOOM Test for BruCON 2024 Badge
import random
import time
import rgb

WIDTH, HEIGHT = 32, 19
image_buffer = [0] * (WIDTH * HEIGHT)

def rgb_to_hex(color):
    (r, g, b) = color
    return rgba_to_hex((r, g, b, 0))

def rgba_to_hex(color):
    (r, g, b, alpha) = color
    color_value = (r << 24) | (g << 16) | (b << 8) | alpha
    return color_value

def reset_buffer():
    global image_buffer
    for i in range(len(image_buffer)):
        image_buffer[i] = 0

def prepare_pixel_global(pos, color):
    global image_buffer
    (posx, posy) = pos
    hex_color = rgb_to_hex(color)
    i = posy * WIDTH + posx
    image_buffer[i] = hex_color

def render_image_buffer():
    rgb.image(image_buffer, pos=(0, 0), size=(WIDTH, HEIGHT))

def draw_doom_pattern():
    """Draw a simple DOOM-like pattern"""
    reset_buffer()

    # Simple 3D-like effect
    for x in range(WIDTH):
        # Create a simple perspective effect
        wall_height = 8 + int(4 * abs(x - WIDTH//2) / (WIDTH//2))

        # Sky/ceiling
        for y in range((HEIGHT - wall_height) // 2):
            prepare_pixel_global((x, y), (50, 50, 100))  # Dark blue sky

        # Wall
        wall_start = (HEIGHT - wall_height) // 2
        wall_end = wall_start + wall_height

        for y in range(wall_start, wall_end):
            # Orange walls with some variation
            brightness = 200 + random.randint(-50, 50)
            prepare_pixel_global((x, y), (brightness, brightness//2, 0))

        # Floor
        for y in range(wall_end, HEIGHT):
            prepare_pixel_global((x, y), (30, 60, 30))  # Green floor

    render_image_buffer()

def main():
    print("DOOM Test - Starting...")

    frame = 0
    while True:
        draw_doom_pattern()

        frame += 1
        if frame % 20 == 0:
            print(f"DOOM Frame: {frame}")

        time.sleep(0.1)
        rgb.clear()

main()