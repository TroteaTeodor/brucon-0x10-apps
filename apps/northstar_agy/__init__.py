### North Star AGY - Professional 4-pointed star with Flappy Bird
import random
import time
import rgb
import buttons

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

# Star animation variables
frame = 0

# Flappy Bird game variables
flappy_active = False
bird_y = HEIGHT // 2
bird_velocity = 0
obstacles = []
score = 0
game_over = False

# Battery indicator - try multiple methods
battery_method = None
battery_value = 0
try:
    import battery
    battery_method = "battery"
    print("Using battery module")
except ImportError:
    try:
        import machine
        battery_method = "machine"
        print("Using machine module")
    except ImportError:
        try:
            from machine import ADC, Pin
            battery_method = "adc"
            print("Using ADC for battery")
        except ImportError:
            battery_method = None
            print("No battery method available")

def draw_four_pointed_star(size, color_cycle):
    """Draw a classic 4-pointed North Star with empty center"""
    center_x, center_y = WIDTH - 8, HEIGHT // 2 - 1  # Right side

    # Color cycling through different hues
    brightness = 120 + size * 20
    if color_cycle == 0:  # Gold
        star_color = (brightness, int(brightness * 0.8), 0)
    elif color_cycle == 1:  # Blue
        star_color = (0, int(brightness * 0.6), brightness)
    elif color_cycle == 2:  # Purple
        star_color = (brightness, 0, int(brightness * 0.8))
    elif color_cycle == 3:  # Green
        star_color = (0, brightness, int(brightness * 0.4))
    else:  # White
        star_color = (brightness, brightness, brightness)

    # NO CENTER POINT - keep it empty/hollow

    # Main cross arms (vertical and horizontal)
    for i in range(1, size + 1):
        # North point (up)
        if center_y - i >= 0:
            prepare_pixel_global((center_x, center_y - i), star_color)

        # South point (down) - go all the way down but avoid NS2 text area
        if center_y + i < HEIGHT - 5 or (center_y + i < HEIGHT and center_x > 20):
            prepare_pixel_global((center_x, center_y + i), star_color)

        # East point (right)
        if center_x + i < WIDTH:
            prepare_pixel_global((center_x + i, center_y), star_color)

        # West point (left)
        if center_x - i >= 0:
            prepare_pixel_global((center_x - i, center_y), star_color)

    # Add hollow diamond outline for bigger stars (no center fill)
    if size >= 3:
        # Only draw the diamond outline, not the center
        diamond_outline = [
            (center_x - 1, center_y - 1),  # top-left
            (center_x + 1, center_y - 1),  # top-right
            (center_x - 1, center_y + 1),  # bottom-left
            (center_x + 1, center_y + 1)   # bottom-right
        ]
        for x, y in diamond_outline:
            if 0 <= x < WIDTH and (y < HEIGHT - 5 or (y < HEIGHT and x > 20)):
                prepare_pixel_global((x, y), star_color)

    # Add star tips for bigger stars
    if size >= 4:
        # Sharp points at the end of each arm
        tip_brightness = int(brightness * 1.2)
        if tip_brightness > 255:
            tip_brightness = 255
        tip_color = (tip_brightness, int(tip_brightness * 0.8), 0)

        # North tip
        if center_y - size - 1 >= 0:
            prepare_pixel_global((center_x, center_y - size - 1), tip_color)

        # South tip - can extend further down on right side
        if center_y + size + 1 < HEIGHT - 5 or (center_y + size + 1 < HEIGHT and center_x > 20):
            prepare_pixel_global((center_x, center_y + size + 1), tip_color)

        # East tip
        if center_x + size + 1 < WIDTH:
            prepare_pixel_global((center_x + size + 1, center_y), tip_color)

        # West tip
        if center_x - size - 1 >= 0:
            prepare_pixel_global((center_x - size - 1, center_y), tip_color)

def draw_ns2_text():
    """Draw NS2 text on left side with more space"""
    # N (4x5 pixels) - bigger and clearer
    n_pixels = [
        (2, HEIGHT-5), (2, HEIGHT-4), (2, HEIGHT-3), (2, HEIGHT-2), (2, HEIGHT-1),  # left column
        (3, HEIGHT-4), (4, HEIGHT-3),                                                # diagonal
        (5, HEIGHT-5), (5, HEIGHT-4), (5, HEIGHT-3), (5, HEIGHT-2), (5, HEIGHT-1),  # right column
    ]

    # S (4x5 pixels) - bigger and clearer
    s_pixels = [
        (8, HEIGHT-5), (9, HEIGHT-5), (10, HEIGHT-5), (11, HEIGHT-5),  # top row
        (8, HEIGHT-4),                                                   # left side top
        (8, HEIGHT-3), (9, HEIGHT-3), (10, HEIGHT-3),                  # middle row
        (11, HEIGHT-2),                                                  # right side bottom
        (8, HEIGHT-1), (9, HEIGHT-1), (10, HEIGHT-1), (11, HEIGHT-1),  # bottom row
    ]

    # 2 (4x5 pixels) - bigger and clearer
    two_pixels = [
        (14, HEIGHT-5), (15, HEIGHT-5), (16, HEIGHT-5), (17, HEIGHT-5),  # top row
        (17, HEIGHT-4),                                                    # right side
        (14, HEIGHT-3), (15, HEIGHT-3), (16, HEIGHT-3), (17, HEIGHT-3),  # middle row
        (14, HEIGHT-2),                                                    # left side
        (14, HEIGHT-1), (15, HEIGHT-1), (16, HEIGHT-1), (17, HEIGHT-1),  # bottom row
    ]

    # Draw all letters in white
    all_pixels = n_pixels + s_pixels + two_pixels
    for x, y in all_pixels:
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            prepare_pixel_global((x, y), (255, 255, 255))

def get_battery_level():
    """Get battery level using available method"""
    global battery_value

    if battery_method == "battery":
        try:
            import battery
            battery_value = battery.read_batt_percentage()
            return battery_value
        except:
            pass
    elif battery_method == "machine":
        try:
            import machine
            # Try different ADC pins commonly used for battery
            adc = machine.ADC(0)  # Try pin 0
            raw = adc.read_u16()
            # Convert to percentage (this is approximate)
            battery_value = int((raw / 65535) * 100)
            return battery_value
        except:
            try:
                adc = machine.ADC(4)  # Try pin 4
                raw = adc.read_u16()
                battery_value = int((raw / 65535) * 100)
                return battery_value
            except:
                pass
    elif battery_method == "adc":
        try:
            from machine import ADC
            adc = ADC(0)
            raw = adc.read_u16()
            battery_value = int((raw / 65535) * 100)
            return battery_value
        except:
            pass

    # Fallback - simulate battery level based on time for testing
    battery_value = 50 + int(30 * ((frame // 100) % 10) / 10)
    return battery_value

def draw_battery_indicator():
    """Draw battery indicator in top right corner"""
    try:
        battery_percent = get_battery_level()

        # Battery position in top right
        battery_x, battery_y = WIDTH - 5, 0

        # Draw battery outline (4x3 pixels)
        outline_color = (100, 100, 100)

        # Main battery body
        prepare_pixel_global((battery_x, battery_y), outline_color)      # top left
        prepare_pixel_global((battery_x + 1, battery_y), outline_color)  # top middle
        prepare_pixel_global((battery_x + 2, battery_y), outline_color)  # top right
        prepare_pixel_global((battery_x, battery_y + 1), outline_color)  # middle left
        prepare_pixel_global((battery_x + 2, battery_y + 1), outline_color)  # middle right
        prepare_pixel_global((battery_x, battery_y + 2), outline_color)  # bottom left
        prepare_pixel_global((battery_x + 1, battery_y + 2), outline_color)  # bottom middle
        prepare_pixel_global((battery_x + 2, battery_y + 2), outline_color)  # bottom right

        # Battery tip
        prepare_pixel_global((battery_x + 3, battery_y + 1), outline_color)

        # Fill based on battery level with proper colors
        if battery_percent > 60:
            fill_color = (0, 255, 0)  # Green
        elif battery_percent > 30:
            fill_color = (255, 255, 0)  # Yellow
        elif battery_percent > 15:
            fill_color = (255, 165, 0)  # Orange
        else:
            fill_color = (255, 0, 0)  # Red

        # Fill bars based on level
        if battery_percent > 20:
            prepare_pixel_global((battery_x + 1, battery_y + 1), fill_color)
        if battery_percent > 50:
            prepare_pixel_global((battery_x + 1, battery_y + 1), fill_color)
            # Add tip blink for high battery
            if (frame // 15) % 2 == 0:
                prepare_pixel_global((battery_x + 3, battery_y + 1), fill_color)

        # Show battery method in corner for debugging
        if battery_method:
            # Blink different colors based on method
            if battery_method == "battery" and (frame // 10) % 2:
                prepare_pixel_global((WIDTH - 1, HEIGHT - 1), (0, 255, 0))  # green = real battery
            elif battery_method == "machine" and (frame // 10) % 2:
                prepare_pixel_global((WIDTH - 1, HEIGHT - 1), (0, 0, 255))  # blue = machine ADC
            elif battery_method == "adc" and (frame // 10) % 2:
                prepare_pixel_global((WIDTH - 1, HEIGHT - 1), (255, 255, 0))  # yellow = raw ADC
        else:
            # Red blink = no battery method (using simulation)
            if (frame // 10) % 2:
                prepare_pixel_global((WIDTH - 1, HEIGHT - 1), (255, 0, 0))

    except Exception as e:
        # Show error indicator
        prepare_pixel_global((WIDTH - 1, HEIGHT - 1), (255, 0, 255))  # magenta = error

class Obstacle:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(2, HEIGHT - 5)  # Gap position (full height)
        self.gap_size = 4  # Gap size

    def update(self):
        self.x -= 1
        return self.x > -2

    def draw(self):
        # Draw top obstacle
        for y in range(0, self.gap_y):
            if 0 <= self.x < WIDTH and 0 <= y < HEIGHT:
                prepare_pixel_global((self.x, y), (0, 255, 0))

        # Draw bottom obstacle
        for y in range(self.gap_y + self.gap_size, HEIGHT):
            if 0 <= self.x < WIDTH and 0 <= y < HEIGHT:
                prepare_pixel_global((self.x, y), (0, 255, 0))

    def check_collision(self, bird_y):
        if self.x == 2:  # Bird is at x=2
            if bird_y <= self.gap_y or bird_y >= self.gap_y + self.gap_size:
                return True
        return False

def update_flappy_bird():
    """Update flappy bird game state"""
    global bird_y, bird_velocity, obstacles, score, game_over, flappy_active

    if not flappy_active or game_over:
        return

    # Apply gravity (faster falling)
    bird_velocity += 0.25
    bird_y += bird_velocity

    # Check bounds (full screen - top to bottom) - fix crash
    if bird_y <= 0:
        bird_y = 0
        bird_velocity = 0
        game_over = True
        return
    if bird_y >= HEIGHT - 1:
        bird_y = HEIGHT - 1
        bird_velocity = 0
        game_over = True
        return

    # Update obstacles
    obstacles = [obs for obs in obstacles if obs.update()]

    # Add new obstacles (slower)
    if frame % 40 == 0:  # Every 40 frames (slower)
        obstacles.append(Obstacle(WIDTH))

    # Check collisions
    for obs in obstacles:
        if obs.check_collision(bird_y):
            game_over = True
            return

        # Score when passing obstacle
        if obs.x == 1:
            score += 1

def draw_flappy_bird():
    """Draw flappy bird game"""
    if not flappy_active:
        return

    # Draw bird (small yellow square at x=2) - full height allowed
    bird_color = (255, 255, 0)
    safe_bird_y = max(0, min(int(bird_y), HEIGHT - 1))  # Clamp bird position
    prepare_pixel_global((2, safe_bird_y), bird_color)

    # Draw obstacles
    for obs in obstacles:
        obs.draw()

    # Draw score (simple dots in top left)
    for i in range(min(score, 5)):  # Max 5 dots
        prepare_pixel_global((i, 0), (255, 255, 255))

    # Game over message
    if game_over:
        # Draw simple "X" at bird position (safe bounds)
        safe_bird_y = max(0, min(int(bird_y), HEIGHT - 1))
        prepare_pixel_global((2, safe_bird_y), (255, 0, 0))

def handle_button_press(down, button):
    """Handle button presses"""
    global flappy_active, bird_velocity, game_over, bird_y, obstacles, score

    if not down:  # Only on button press, not release
        return

    if button == 'RIGHT':
        if not flappy_active:
            # Start flappy bird game
            flappy_active = True
            bird_y = HEIGHT // 2
            bird_velocity = 0
            obstacles = []
            score = 0
            game_over = False
        elif game_over:
            # Restart game
            bird_y = HEIGHT // 2
            bird_velocity = 0
            obstacles = []
            score = 0
            game_over = False
        else:
            # Flap (jump up) - stronger jump to counteract faster gravity
            bird_velocity = -2.0

    elif button == 'LEFT' and flappy_active:
        # Exit flappy bird game
        flappy_active = False
        game_over = False

def setup_buttons():
    """Setup button handlers"""
    buttons.register(buttons.BTN_RIGHT, lambda down: handle_button_press(down, 'RIGHT'))
    buttons.register(buttons.BTN_LEFT, lambda down: handle_button_press(down, 'LEFT'))
    buttons.register(buttons.BTN_UP, lambda down: handle_button_press(down, 'RIGHT') if flappy_active else None)
    buttons.register(buttons.BTN_A, lambda down: handle_button_press(down, 'RIGHT') if flappy_active else None)

def main():
    global frame

    # Setup button handlers
    setup_buttons()

    while True:
        reset_buffer()

        # Update flappy bird game
        update_flappy_bird()

        # Show animated star when flappy bird is not active
        if not flappy_active:
            # Calculate star size (1 to 6, growing and shrinking) - animated again
            cycle = frame % 80  # 80 frame cycle for smooth animation
            if cycle < 40:
                star_size = 1 + (cycle // 7)  # Grow from 1 to 6
            else:
                star_size = 6 - ((cycle - 40) // 7)  # Shrink from 6 to 1

            # Ensure minimum size of 1
            if star_size < 1:
                star_size = 1

            # Color cycle - changes every full size cycle (160 frames)
            color_cycle = (frame // 160) % 5  # 5 different colors

            draw_four_pointed_star(star_size, color_cycle)

        # Only draw NS2 text when flappy bird is not active (fullscreen mode)
        if not flappy_active:
            draw_ns2_text()

        # Draw flappy bird game on top
        draw_flappy_bird()

        # Always draw battery indicator
        draw_battery_indicator()

        frame += 1
        if frame > 1000:
            frame = 0

        time.sleep(0.06)  # Slower ~16 FPS for more relaxed gameplay
        rgb.clear()
        render_image_buffer()

main()