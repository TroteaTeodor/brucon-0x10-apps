import time
import rgb
import buttons
import math

WIDTH, HEIGHT = 32, 19
image_buffer = [0] * (WIDTH * HEIGHT)

# Player state
px, py = 2.0, 2.0
pa = 0

# Game state
score = 0
total_enemies = 2

# Simple world map
world_map = [
    [1,1,1,1,1,1],
    [1,0,0,0,0,1],
    [1,0,1,0,0,1],
    [1,0,0,0,0,1],
    [1,0,0,0,0,1],
    [1,1,1,1,1,1]
]

# Enemy system with random spawning
import random
enemies = []
max_enemies = 2
enemy_spawn_timer = 0

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

def draw_digit(x, y, digit, color):
    """Draw a single digit at position x,y"""
    # Simple 3x5 pixel font for digits 0-9
    patterns = {
        0: [
            [1,1,1],
            [1,0,1],
            [1,0,1],
            [1,0,1],
            [1,1,1]
        ],
        1: [
            [0,1,0],
            [1,1,0],
            [0,1,0],
            [0,1,0],
            [1,1,1]
        ],
        2: [
            [1,1,1],
            [0,0,1],
            [1,1,1],
            [1,0,0],
            [1,1,1]
        ],
        3: [
            [1,1,1],
            [0,0,1],
            [1,1,1],
            [0,0,1],
            [1,1,1]
        ],
        4: [
            [1,0,1],
            [1,0,1],
            [1,1,1],
            [0,0,1],
            [0,0,1]
        ],
        5: [
            [1,1,1],
            [1,0,0],
            [1,1,1],
            [0,0,1],
            [1,1,1]
        ],
        6: [
            [1,1,1],
            [1,0,0],
            [1,1,1],
            [1,0,1],
            [1,1,1]
        ],
        7: [
            [1,1,1],
            [0,0,1],
            [0,0,1],
            [0,0,1],
            [0,0,1]
        ],
        8: [
            [1,1,1],
            [1,0,1],
            [1,1,1],
            [1,0,1],
            [1,1,1]
        ],
        9: [
            [1,1,1],
            [1,0,1],
            [1,1,1],
            [0,0,1],
            [1,1,1]
        ]
    }

    if digit in patterns:
        pattern = patterns[digit]
        for row in range(5):
            for col in range(3):
                if pattern[row][col]:
                    set_pixel(x + col, y + row, color)

def draw_number(x, y, number, color):
    """Draw a number at position x,y"""
    if number == 0:
        draw_digit(x, y, 0, color)
        return

    digits = []
    temp = number
    while temp > 0:
        digits.append(temp % 10)
        temp //= 10

    # Draw digits from right to left
    current_x = x
    for i in range(len(digits)-1, -1, -1):
        draw_digit(current_x, y, digits[i], color)
        current_x += 4  # Space between digits

def spawn_enemy():
    """Spawn an enemy at a random valid position"""
    # Try to find a good spawn position
    for attempt in range(20):
        x = random.uniform(1.2, 4.8)
        y = random.uniform(1.2, 4.8)

        # Make sure it's not in a wall
        mx, my = int(x), int(y)
        if 0 <= mx < 6 and 0 <= my < 6 and world_map[my][mx] == 0:
            # Make sure it's not too close to player
            dist_to_player = math.sqrt((x - px)**2 + (y - py)**2)
            if dist_to_player > 1.0:
                # Make sure it's not too close to other enemies
                too_close = False
                for enemy in enemies:
                    if enemy['alive']:
                        dist = math.sqrt((x - enemy['x'])**2 + (y - enemy['y'])**2)
                        if dist < 0.8:
                            too_close = True
                            break
                if not too_close:
                    return {'x': x, 'y': y, 'alive': True}
    return None

def update_enemies():
    """Update enemy spawning system"""
    global enemy_spawn_timer

    # Remove dead enemies
    enemies[:] = [e for e in enemies if e['alive']]

    # Spawn new enemies if needed
    alive_count = len(enemies)
    if alive_count < max_enemies:
        enemy_spawn_timer += 1
        if enemy_spawn_timer > 60:  # Spawn every 6 seconds
            new_enemy = spawn_enemy()
            if new_enemy:
                enemies.append(new_enemy)
                enemy_spawn_timer = 0

def init_enemies():
    """Initialize starting enemies"""
    global enemies
    enemies.clear()
    for _ in range(max_enemies):
        enemy = spawn_enemy()
        if enemy:
            enemies.append(enemy)

def shoot():
    """Simple shooting - check center ray for enemy"""
    global score
    center_ray = cast_ray(pa)
    if len(center_ray) == 2:
        distance, hit_type = center_ray
        if hit_type == "enemy" and distance < 3.0:
            # Find and kill the enemy
            angle_rad = pa * 3.14159 / 180
            dx = math.cos(angle_rad) * 0.1
            dy = math.sin(angle_rad) * 0.1
            x, y = px, py

            for _ in range(int(distance / 0.1)):
                x += dx
                y += dy
                for enemy in enemies:
                    if enemy['alive']:
                        enemy_dist = math.sqrt((x - enemy['x'])**2 + (y - enemy['y'])**2)
                        if enemy_dist < 0.2:
                            enemy['alive'] = False
                            score += 1
                            print(f"Enemy killed! Score: {score}")
                            return True
    return False

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

        # Check if we hit an enemy first
        for enemy in enemies:
            if enemy['alive']:
                enemy_dist = math.sqrt((x - enemy['x'])**2 + (y - enemy['y'])**2)
                if enemy_dist < 0.2:  # Enemy hit radius
                    return distance, "enemy"

        # Check walls
        mx, my = int(x), int(y)
        if mx < 0 or mx >= 6 or my < 0 or my >= 6 or world_map[my][mx] == 1:
            return distance, "wall"

    return 6.0, "wall"

def render_doom():
    global pa
    reset_buffer()

    # Cast rays for each column
    fov = 60
    for col in range(WIDTH):
        ray_angle = pa - fov//2 + (col * fov) // WIDTH
        ray_result = cast_ray(ray_angle)

        # Handle both old and new return formats
        if isinstance(ray_result, tuple) and len(ray_result) == 2:
            distance, hit_type = ray_result
        else:
            distance = ray_result
            hit_type = "wall"

        if distance < 0.1:
            wall_height = HEIGHT
        else:
            wall_height = min(HEIGHT, int(HEIGHT * 2 // distance))

        wall_top = max(0, (HEIGHT - wall_height) // 2)
        wall_bottom = min(HEIGHT - 1, wall_top + wall_height)

        # Better distance-based brightness
        brightness = max(20, min(255, int(300 / (1 + distance * 0.5))))

        # Choose color based on what we hit
        if hit_type == "enemy":
            wall_color = (brightness // 4, brightness, brightness // 4)  # Green for enemies
        else:
            wall_color = (brightness, brightness // 3, brightness // 8)  # Orange for walls

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

    # Enhanced crosshair - red when aiming at enemy
    cx, cy = WIDTH//2, HEIGHT//2
    center_ray = cast_ray(pa)
    if isinstance(center_ray, tuple) and len(center_ray) == 2 and center_ray[1] == "enemy":
        crosshair_color = (255, 0, 0)  # Red when aiming at enemy
    else:
        crosshair_color = (255, 255, 255)  # White normally

    set_pixel(cx, cy, crosshair_color)
    set_pixel(cx-1, cy, crosshair_color)
    set_pixel(cx+1, cy, crosshair_color)
    set_pixel(cx, cy-1, crosshair_color)
    set_pixel(cx, cy+1, crosshair_color)

    # Draw score in top right corner
    draw_number(WIDTH-8, 1, score, (255, 255, 0))  # Yellow score only

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
        shoot()

def on_b(pressed):
    if pressed:
        shoot()

def main():
    print("DOOM Badge - Starting with enemy spawning...")

    # Initialize enemies
    init_enemies()

    buttons.register(buttons.BTN_UP, on_up)
    buttons.register(buttons.BTN_DOWN, on_down)
    buttons.register(buttons.BTN_LEFT, on_left)
    buttons.register(buttons.BTN_RIGHT, on_right)
    buttons.register(buttons.BTN_A, on_a)
    # Don't register BTN_B - let it use the default system reboot/exit behavior

    frame = 0
    while True:
        move_player(move_forward)
        rotate_player(turn_dir)

        # Update enemy spawning
        update_enemies()

        render_doom()

        rgb.clear()
        render_buffer()

        frame += 1
        if frame % 60 == 0:
            alive_count = len([e for e in enemies if e['alive']])
            print(f"Frame {frame}, Score: {score}, Enemies: {alive_count}")

        time.sleep(0.1)

main()