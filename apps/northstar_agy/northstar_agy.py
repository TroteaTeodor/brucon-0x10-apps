try:
    from .display_helper import WIDTH, HEIGHT
except ImportError:
    WIDTH, HEIGHT = 32, 19

import time
import rgb

# Simple star pattern - just coordinates
star_coords = [
    (16, 6),   # top
    (18, 8),   # top-right
    (20, 9),   # right
    (18, 11),  # bottom-right
    (16, 13),  # bottom
    (14, 11),  # bottom-left
    (12, 9),   # left
    (14, 8),   # top-left
]

# Animation counter
frame = 0

def draw_star():
    """Draw a simple pulsing star"""
    global frame

    # Simple brightness pulse
    brightness = 150 + int(50 * (frame % 20) / 10)
    if frame % 20 > 10:
        brightness = 200 - int(50 * ((frame % 20) - 10) / 10)

    # Center of star
    rgb.pixel((brightness, brightness // 2, 0, 255), (16, 9))

    # Star points
    for x, y in star_coords:
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            rgb.pixel((brightness, brightness // 2, 0, 255), (x, y))

def draw_ns2():
    """Draw NS2 text"""
    # Simple NS2 pattern
    ns2_pixels = [
        (10, 2), (11, 2),    # N
        (10, 3), (12, 3),
        (10, 4), (11, 4), (12, 4),
        (10, 5), (12, 5),
        (10, 6), (12, 6),

        (15, 2), (16, 2), (17, 2),  # S
        (15, 3),
        (15, 4), (16, 4), (17, 4),
        (17, 5),
        (15, 6), (16, 6), (17, 6),

        (20, 2), (21, 2),    # 2
        (22, 3),
        (20, 4), (21, 4), (22, 4),
        (20, 5),
        (20, 6), (21, 6), (22, 6),
    ]

    for x, y in ns2_pixels:
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            rgb.pixel((255, 255, 255, 255), (x, y))

def draw_north_star():
    """Draw NORTH STAR text"""
    # Simple NORTH text
    north_pixels = [
        (2, 15), (3, 15),    # N
        (2, 16), (4, 16),
        (2, 17), (3, 17), (4, 17),

        (6, 15), (7, 15),    # S (for STAR)
        (6, 16),
        (6, 17), (7, 17),
    ]

    for x, y in north_pixels:
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            rgb.pixel((0, 150, 255, 255), (x, y))

def main():
    """Main function - keep it super simple"""
    global frame

    # Clear screen once
    rgb.clear()

    # Main loop
    while True:
        # Clear screen
        rgb.clear()

        # Draw star
        draw_star()

        # Alternate text every 100 frames
        if (frame // 100) % 2 == 0:
            draw_ns2()
        else:
            draw_north_star()

        # Update frame
        frame += 1
        if frame > 1000:
            frame = 0

        # Wait
        time.sleep(0.1)

main()