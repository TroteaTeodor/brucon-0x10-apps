import time
import rgb
import buttons
import math

WIDTH, HEIGHT = 32, 19
image_buffer = [0] * (WIDTH * HEIGHT)

# Player state
px, py = 2.0, 2.0
pa = 0

# Simple world map
world_map = [
    [1,1,1,1,1,1],
    [1,0,0,0,0,1],
    [1,0,1,0,0,1],
    [1,0,0,0,0,1],
    [1,0,0,0,0,1],
    [1,1,1,1,1,1]
]

def rgb_to_hex(color):
    (r, g, b) = color
    return (r << 24) | (g << 16) | (b << 8)

def reset_buffer():
    global image_buffer
    for i in range(len(image_buffer)):
        image_buffer[i] = 0

def set_pixel(x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        hex_color = rgb_to_hex(color)
        image_buffer[y * WIDTH + x] = hex_color

def render_buffer():
    rgb.image(image_buffer, pos=(0, 0), size=(WIDTH, HEIGHT))

def cast_ray(angle_deg):
    global px, py
    angle_rad = angle_deg * 3.14159 / 180
    dx = math.cos(angle_rad) * 0.1
    dy = math.sin(angle_rad) * 0.1

    x, y = px, py
    distance = 0

    for _ in range(60):
        x += dx
        y += dy
        distance += 0.1

        mx, my = int(x), int(y)
        if mx < 0 or mx >= 6 or my < 0 or my >= 6 or world_map[my][mx] == 1:
            return distance

    return 6.0

def render_doom():
    global pa
    reset_buffer()

    # Cast rays for each column
    fov = 60
    for col in range(WIDTH):
        ray_angle = pa - fov//2 + (col * fov) // WIDTH
        distance = cast_ray(ray_angle)

        if distance < 0.1:
            wall_height = HEIGHT
        else:
            wall_height = min(HEIGHT, int(HEIGHT * 2 // distance))

        wall_top = max(0, (HEIGHT - wall_height) // 2)
        wall_bottom = min(HEIGHT - 1, wall_top + wall_height)

        # Better distance-based brightness
        brightness = max(20, min(255, int(300 / (1 + distance * 0.5))))
        wall_color = (brightness, brightness // 3, brightness // 8)

        for row in range(HEIGHT):
            if row < wall_top:
                # Sky with gradient that changes with distance
                sky_base = max(15, 50 - row * 2)
                sky_dist_fade = max(0.3, 1.0 - distance * 0.1)
                sky_brightness = int(sky_base * sky_dist_fade)
                set_pixel(col, row, (sky_brightness//3, sky_brightness//3, sky_brightness))
            elif row <= wall_bottom:
                set_pixel(col, row, wall_color)
            else:
                # Green floor with distance fog
                floor_dist = (row - wall_bottom) * distance * 0.2
                floor_brightness = max(10, int(80 / (1 + floor_dist)))
                set_pixel(col, row, (floor_brightness//4, floor_brightness, floor_brightness//6))

    # Enhanced crosshair
    cx, cy = WIDTH//2, HEIGHT//2
    set_pixel(cx, cy, (255, 0, 0))
    set_pixel(cx-1, cy, (200, 0, 0))
    set_pixel(cx+1, cy, (200, 0, 0))
    set_pixel(cx, cy-1, (200, 0, 0))
    set_pixel(cx, cy+1, (200, 0, 0))

def move_player(forward):
    global px, py, pa

    speed = 0.2
    angle_rad = pa * 3.14159 / 180
    dx = math.cos(angle_rad) * speed * forward
    dy = math.sin(angle_rad) * speed * forward

    new_x = px + dx
    new_y = py + dy

    if 0 < new_x < 6 and world_map[int(py)][int(new_x)] == 0:
        px = new_x

    if 0 < new_y < 6 and world_map[int(new_y)][int(px)] == 0:
        py = new_y

def rotate_player(direction):
    global pa
    pa = (pa + direction * 10) % 360

# Button handlers
move_forward = 0
turn_dir = 0

def on_up(pressed):
    global move_forward
    move_forward = 1 if pressed else 0

def on_down(pressed):
    global move_forward
    move_forward = -1 if pressed else 0

def on_left(pressed):
    global turn_dir
    turn_dir = -1 if pressed else 0

def on_right(pressed):
    global turn_dir
    turn_dir = 1 if pressed else 0

def on_a(pressed):
    if pressed:
        print("PEW!")

def on_b(pressed):
    if pressed:
        import sys
        sys.exit()

def main():
    print("DOOM Badge - Direct")

    buttons.register(buttons.BTN_UP, on_up)
    buttons.register(buttons.BTN_DOWN, on_down)
    buttons.register(buttons.BTN_LEFT, on_left)
    buttons.register(buttons.BTN_RIGHT, on_right)
    buttons.register(buttons.BTN_A, on_a)
    buttons.register(buttons.BTN_B, on_b)

    frame = 0
    while True:
        move_player(move_forward)
        rotate_player(turn_dir)

        render_doom()

        rgb.clear()
        render_buffer()

        frame += 1
        if frame % 60 == 0:
            print(f"Frame {frame}, Pos: ({px:.1f}, {py:.1f}), Angle: {pa}")

        time.sleep(0.1)

main()