import math
import time
import rgb
import buttons

# Badge display setup
WIDTH, HEIGHT = 32, 19
image_buffer = [0] * (WIDTH * HEIGHT)

def rgb_to_hex(color):
    (r, g, b) = color
    return rgba_to_hex((r, g, b, 0))

def rgba_to_hex(color):
    (r, g, b, alpha) = color
    return (r << 24) | (g << 16) | (b << 8) | alpha

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

# Simple 8x8 map
world_map = [
    [1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1],
    [1,0,1,0,0,1,0,1],
    [1,0,0,0,0,0,0,1],
    [1,0,0,1,1,0,0,1],
    [1,0,0,0,0,0,0,1],
    [1,0,1,0,0,1,0,1],
    [1,1,1,1,1,1,1,1]
]

# Player state
px, py = 2.0, 2.0  # position
pa = 0  # angle in degrees

def cast_ray(angle_deg):
    """Cast a single ray and return distance to wall"""
    angle_rad = math.radians(angle_deg)
    dx = math.cos(angle_rad) * 0.05
    dy = math.sin(angle_rad) * 0.05

    x, y = px, py
    distance = 0

    # Step along ray until we hit a wall
    for _ in range(120):  # max distance = 6
        x += dx
        y += dy
        distance += 0.05

        # Check if we hit a wall
        mx, my = int(x), int(y)
        if mx < 0 or mx >= 8 or my < 0 or my >= 8 or world_map[my][mx] == 1:
            return distance

    return 6.0  # max distance

def render_3d():
    """Render 3D view using raycasting"""
    reset_buffer()

    # Cast rays for each column of screen
    fov = 60  # field of view in degrees
    for col in range(WIDTH):
        # Calculate ray angle
        ray_angle = pa - fov//2 + (col * fov) // WIDTH

        # Cast the ray
        distance = cast_ray(ray_angle)

        # Calculate wall height on screen
        if distance < 0.1:
            wall_height = HEIGHT
        else:
            wall_height = min(HEIGHT, int(HEIGHT / distance))

        # Calculate top and bottom of wall
        wall_top = max(0, (HEIGHT - wall_height) // 2)
        wall_bottom = min(HEIGHT - 1, wall_top + wall_height)

        # Choose wall color based on distance
        brightness = max(50, min(255, int(255 / (1 + distance/2))))
        wall_color = (brightness, brightness // 2, 0)  # Orange walls

        # Draw vertical line
        for row in range(HEIGHT):
            if row < wall_top:
                # Ceiling
                set_pixel(col, row, (20, 20, 50))  # Dark blue
            elif row <= wall_bottom:
                # Wall
                set_pixel(col, row, wall_color)
            else:
                # Floor
                set_pixel(col, row, (30, 60, 30))  # Dark green

    # Add crosshair
    set_pixel(WIDTH//2, HEIGHT//2, (255, 255, 255))

    render_buffer()

def move_player(forward):
    """Move player forward/backward"""
    global px, py

    speed = 0.1
    angle_rad = math.radians(pa)
    dx = math.cos(angle_rad) * speed * forward
    dy = math.sin(angle_rad) * speed * forward

    # Check collision before moving
    new_x = px + dx
    new_y = py + dy

    # X movement
    if 0 < new_x < 8 and world_map[int(py)][int(new_x)] == 0:
        px = new_x

    # Y movement
    if 0 < new_y < 8 and world_map[int(new_y)][int(px)] == 0:
        py = new_y

def rotate_player(direction):
    """Rotate player left/right"""
    global pa
    pa = (pa + direction * 5) % 360

# Input handling
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
        print("PEW!")  # Shooting sound

def on_b(pressed):
    # Reset player position
    if pressed:
        global px, py, pa
        px, py, pa = 2.0, 2.0, 0

def main():
    print("Simple DOOM - Starting...")

    # Register controls
    buttons.register(buttons.BTN_UP, on_up)
    buttons.register(buttons.BTN_DOWN, on_down)
    buttons.register(buttons.BTN_LEFT, on_left)
    buttons.register(buttons.BTN_RIGHT, on_right)
    buttons.register(buttons.BTN_A, on_a)
    buttons.register(buttons.BTN_B, on_b)

    frame = 0
    while True:
        # Update player
        move_player(move_forward)
        rotate_player(turn_dir)

        # Render
        render_3d()

        frame += 1
        if frame % 30 == 0:
            print(f"Pos: ({px:.1f}, {py:.1f}), Angle: {pa}")

        rgb.clear()
        time.sleep(0.1)  # 10 FPS

if __name__ == "__main__":
    main()