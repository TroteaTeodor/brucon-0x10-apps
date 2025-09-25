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

# Enemy system
import random
enemies = []
max_enemies = 2
enemy_respawn_timer = 0

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True

    def get_distance_to_player(self):
        dx = self.x - px
        dy = self.y - py
        return math.sqrt(dx*dx + dy*dy)

def spawn_enemy():
    """Spawn an enemy at a random empty location"""
    for attempt in range(50):  # Try 50 times to find a good spot
        x = random.uniform(1.5, 6.5)
        y = random.uniform(1.5, 6.5)
        # Make sure it's not in a wall and not too close to player
        mx, my = int(x), int(y)
        if (0 <= mx < 8 and 0 <= my < 8 and world_map[my][mx] == 0 and
            abs(x - px) > 1.5 and abs(y - py) > 1.5):
            # Also check it's not too close to existing enemies
            too_close = False
            for existing in enemies:
                if existing.alive and abs(x - existing.x) < 0.8 and abs(y - existing.y) < 0.8:
                    too_close = True
                    break
            if not too_close:
                print(f"Spawn attempt {attempt+1}: Success at ({x:.1f}, {y:.1f})")
                return Enemy(x, y)
        if attempt < 10:  # Only print first 10 attempts
            print(f"Spawn attempt {attempt+1}: Failed at ({x:.1f}, {y:.1f}) - wall={world_map[my][mx] if 0<=mx<8 and 0<=my<8 else 'OOB'}, dist_to_player={abs(x-px)+abs(y-py):.1f}")
    print("All spawn attempts failed!")
    return None

def update_enemies():
    """Update enemy system"""
    global enemy_respawn_timer

    # Remove dead enemies
    enemies[:] = [e for e in enemies if e.alive]

    # Respawn enemies if needed
    enemy_respawn_timer += 1
    if len(enemies) < max_enemies and enemy_respawn_timer > 120:  # Respawn every 120 frames (12 seconds)
        new_enemy = spawn_enemy()
        if new_enemy:
            enemies.append(new_enemy)
            enemy_respawn_timer = 0

def init_enemies():
    """Spawn initial enemies"""
    print("Initializing enemies...")
    for i in range(max_enemies):
        enemy = spawn_enemy()
        if enemy:
            enemies.append(enemy)
            print(f"Enemy {i+1} spawned at ({enemy.x:.1f}, {enemy.y:.1f})")
        else:
            print(f"Failed to spawn enemy {i+1}")
    print(f"Total enemies spawned: {len(enemies)}")

def cast_ray(angle_deg):
    """Cast a single ray and return distance to wall or enemy"""
    angle_rad = math.radians(angle_deg)
    dx = math.cos(angle_rad) * 0.05
    dy = math.sin(angle_rad) * 0.05

    x, y = px, py
    distance = 0

    # Step along ray until we hit a wall or enemy
    for _ in range(120):  # max distance = 6
        x += dx
        y += dy
        distance += 0.05

        # Check if we hit an enemy first
        for enemy in enemies:
            if enemy.alive:
                enemy_dist = math.sqrt((x - enemy.x)**2 + (y - enemy.y)**2)
                if enemy_dist < 0.3:  # Enemy hit radius
                    return distance, "enemy"

        # Check if we hit a wall
        mx, my = int(x), int(y)
        if mx < 0 or mx >= 8 or my < 0 or my >= 8 or world_map[my][mx] == 1:
            return distance, "wall"

    return 6.0, "wall"  # max distance

def shoot():
    """Check if crosshair is on an enemy and shoot it"""
    center_angle = pa  # Player's facing direction
    ray_result = cast_ray(center_angle)

    if len(ray_result) == 2:
        distance, hit_type = ray_result
        if hit_type == "enemy" and distance < 4.0:  # Max shooting range
            # Find which enemy was hit
            angle_rad = math.radians(center_angle)
            dx = math.cos(angle_rad) * 0.05
            dy = math.sin(angle_rad) * 0.05

            x, y = px, py
            for step in range(int(distance / 0.05)):
                x += dx
                y += dy
                for enemy in enemies:
                    if enemy.alive:
                        enemy_dist = math.sqrt((x - enemy.x)**2 + (y - enemy.y)**2)
                        if enemy_dist < 0.3:
                            enemy.alive = False
                            return True
    return False

def render_3d():
    """Render 3D view using raycasting"""
    reset_buffer()

    # Cast rays for each column of screen
    fov = 60  # field of view in degrees
    for col in range(WIDTH):
        # Calculate ray angle
        ray_angle = pa - fov//2 + (col * fov) // WIDTH

        # Cast the ray
        ray_result = cast_ray(ray_angle)

        # Handle new return format
        if len(ray_result) == 2:
            distance, hit_type = ray_result
        else:
            distance, hit_type = ray_result, "wall"

        # Calculate object height on screen
        if distance < 0.1:
            obj_height = HEIGHT
        else:
            obj_height = min(HEIGHT, int(HEIGHT / distance))

        # Calculate top and bottom of object
        obj_top = max(0, (HEIGHT - obj_height) // 2)
        obj_bottom = min(HEIGHT - 1, obj_top + obj_height)

        # Choose color based on what we hit
        brightness = max(50, min(255, int(255 / (1 + distance/2))))
        if hit_type == "enemy":
            # Green enemies
            obj_color = (brightness // 4, brightness, brightness // 4)
        else:
            # Orange walls
            obj_color = (brightness, brightness // 2, 0)

        # Draw vertical line
        for row in range(HEIGHT):
            if row < obj_top:
                # Ceiling
                set_pixel(col, row, (20, 20, 50))  # Dark blue
            elif row <= obj_bottom:
                # Wall or enemy
                set_pixel(col, row, obj_color)
            else:
                # Floor
                set_pixel(col, row, (30, 60, 30))  # Dark green

    # Add crosshair - make it red if aiming at an enemy
    crosshair_color = (255, 255, 255)  # Default white
    center_ray = cast_ray(pa)
    if len(center_ray) == 2 and center_ray[1] == "enemy" and center_ray[0] < 4.0:
        crosshair_color = (255, 0, 0)  # Red when aiming at enemy

    set_pixel(WIDTH//2, HEIGHT//2, crosshair_color)

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
        shoot()

def on_b(pressed):
    # Reset player position
    if pressed:
        global px, py, pa
        px, py, pa = 2.0, 2.0, 0

def main():
    print("Simple DOOM - Starting...")

    # Initialize enemies
    init_enemies()

    # Register controls
    buttons.register(buttons.BTN_UP, on_up)
    buttons.register(buttons.BTN_DOWN, on_down)
    buttons.register(buttons.BTN_LEFT, on_left)
    buttons.register(buttons.BTN_RIGHT, on_right)
    buttons.register(buttons.BTN_A, on_a)
    # Don't register BTN_B - let it use the default system reboot/exit behavior

    frame = 0
    while True:
        # Update player
        move_player(move_forward)
        rotate_player(turn_dir)

        # Update enemies
        update_enemies()

        # Render
        render_3d()

        frame += 1
        if frame % 100 == 0:  # Every 10 seconds
            alive_enemies = sum(1 for e in enemies if e.alive)
            print(f"Frame {frame}: {alive_enemies} alive enemies")

        rgb.clear()
        time.sleep(0.1)  # 10 FPS

if __name__ == "__main__":
    main()