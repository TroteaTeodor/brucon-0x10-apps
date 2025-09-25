### DOOM Badge - Copy TwinkleFox Pattern Exactly
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

def buffer_doom_scene():
    """Buffer DOOM scene like TwinkleFox buffers twinkles"""
    reset_buffer()

    # Draw simple DOOM corridor
    for x in range(WIDTH):
        center_dist = abs(x - WIDTH//2)

        # Wall height - taller in center
        wall_height = HEIGHT//2 + (WIDTH//2 - center_dist)//3
        wall_height = max(6, min(HEIGHT-2, wall_height))

        wall_top = (HEIGHT - wall_height)//2
        wall_bottom = wall_top + wall_height

        for y in range(HEIGHT):
            if y < wall_top:
                # Sky
                prepare_pixel_global((x, y), (30, 30, 80))
            elif y <= wall_bottom:
                # Wall with simple texture
                brightness = 200 - center_dist * 4
                if (x + y) % 3 == 0:
                    brightness = brightness // 2
                prepare_pixel_global((x, y), (brightness, brightness//2, 0))
            else:
                # Floor
                floor_brightness = max(30, 80 - (y - wall_bottom) * 3)
                prepare_pixel_global((x, y), (0, floor_brightness, 0))

    # Crosshair
    prepare_pixel_global((WIDTH//2, HEIGHT//2), (255, 255, 255))

def main():
    print("DOOM - TwinkleFox Pattern")

    frame = 0
    while True:
        # Update scene
        buffer_doom_scene()

        # EXACT same timing and order as TwinkleFox
        time.sleep(0.03)
        rgb.clear()
        render_image_buffer()

        frame += 1
        if frame % 100 == 0:
            print(f"DOOM frame: {frame}")

main()