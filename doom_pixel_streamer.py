#!/usr/bin/env python3
"""
DOOM Pixel Streamer - Render DOOM with Pygame, convert to badge pixels
"""

import pygame
import math
import time
import subprocess
import sys
from PIL import Image
import numpy as np

# Badge settings
BADGE_WIDTH = 32
BADGE_HEIGHT = 19
BADGE_PORT = "/dev/tty.usbmodem313371"

# Pygame window (we'll downscale this to badge resolution)
RENDER_WIDTH = 320
RENDER_HEIGHT = 240

class SimpleDOOM:
    def __init__(self, screen):
        self.screen = screen

        # Player state
        self.player_x = 1.5
        self.player_y = 1.5
        self.player_angle = 0.0

        # Simple 8x8 world
        self.world_map = [
            [1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,0,0,1,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,0,1,1,0,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,0,0,1,0,1],
            [1,1,1,1,1,1,1,1]
        ]

    def cast_ray(self, angle):
        """Simple raycasting"""
        dx = math.cos(angle) * 0.1
        dy = math.sin(angle) * 0.1

        x, y = self.player_x, self.player_y
        distance = 0

        for _ in range(80):  # Max distance
            x += dx
            y += dy
            distance += 0.1

            # Check bounds and walls
            mx, my = int(x), int(y)
            if mx < 0 or mx >= 8 or my < 0 or my >= 8 or self.world_map[my][mx] == 1:
                return distance

        return 8.0

    def render_frame(self):
        """Render DOOM frame using Pygame"""
        self.screen.fill((50, 50, 100))  # Sky color

        # Raycasting for each column
        fov = math.pi / 3  # 60 degrees
        num_rays = RENDER_WIDTH

        for i in range(num_rays):
            # Calculate ray angle
            ray_angle = self.player_angle - fov/2 + (i / num_rays) * fov

            # Cast ray
            distance = self.cast_ray(ray_angle)

            # Calculate wall height
            if distance <= 0.1:
                wall_height = RENDER_HEIGHT
            else:
                wall_height = min(RENDER_HEIGHT, int(RENDER_HEIGHT * 2 / distance))

            # Wall bounds
            wall_top = max(0, (RENDER_HEIGHT - wall_height) // 2)
            wall_bottom = min(RENDER_HEIGHT - 1, wall_top + wall_height)

            # Wall color based on distance
            brightness = max(50, min(255, int(255 / (1 + distance * 0.3))))
            wall_color = (brightness, brightness // 2, 0)  # Orange

            # Draw vertical line
            if wall_top < wall_bottom:
                pygame.draw.line(self.screen, wall_color,
                               (i, wall_top), (i, wall_bottom), 1)

            # Floor
            if wall_bottom < RENDER_HEIGHT - 1:
                pygame.draw.line(self.screen, (0, 60, 0),
                               (i, wall_bottom + 1), (i, RENDER_HEIGHT - 1), 1)

        # Crosshair
        center_x, center_y = RENDER_WIDTH // 2, RENDER_HEIGHT // 2
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), 2)

    def move_forward(self):
        speed = 0.1
        dx = math.cos(self.player_angle) * speed
        dy = math.sin(self.player_angle) * speed

        new_x = self.player_x + dx
        new_y = self.player_y + dy

        # Simple collision
        if (0 < new_x < 8 and 0 < new_y < 8 and
            self.world_map[int(new_y)][int(new_x)] == 0):
            self.player_x = new_x
            self.player_y = new_y

    def move_backward(self):
        speed = 0.1
        dx = math.cos(self.player_angle) * speed
        dy = math.sin(self.player_angle) * speed

        new_x = self.player_x - dx
        new_y = self.player_y - dy

        if (0 < new_x < 8 and 0 < new_y < 8 and
            self.world_map[int(new_y)][int(new_x)] == 0):
            self.player_x = new_x
            self.player_y = new_y

    def turn_left(self):
        self.player_angle -= 0.1

    def turn_right(self):
        self.player_angle += 0.1

def pygame_surface_to_badge_pixels(surface):
    """Convert pygame surface to badge pixel array"""
    # Convert pygame surface to PIL Image
    pygame_array = pygame.surfarray.array3d(surface)
    pygame_array = np.transpose(pygame_array, (1, 0, 2))  # Fix orientation

    # Convert to PIL Image and resize to badge resolution
    img = Image.fromarray(pygame_array.astype('uint8'))
    img_resized = img.resize((BADGE_WIDTH, BADGE_HEIGHT), Image.Resampling.NEAREST)

    # Convert to badge format
    pixels = list(img_resized.getdata())

    # Convert to badge hex format
    badge_buffer = []
    for r, g, b in pixels:
        hex_color = (r << 24) | (g << 16) | (b << 8) | 0
        badge_buffer.append(hex_color)

    return badge_buffer

def send_pixels_to_badge(pixel_buffer):
    """Send pixel buffer to badge"""
    try:
        # Create MicroPython code to display pixels
        code = f"""
import rgb
buffer = {pixel_buffer}
rgb.clear()
rgb.image(buffer, pos=(0, 0), size=({BADGE_WIDTH}, {BADGE_HEIGHT}))
"""

        # Send to badge
        result = subprocess.run([
            "python3", "-m", "mpremote",
            "connect", f"port:{BADGE_PORT}",
            "exec", code
        ], capture_output=True, text=True, timeout=0.5)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        return False
    except Exception as e:
        print(f"Badge error: {e}")
        return False

def main():
    print("🎮 DOOM Pixel Streamer")
    print("Rendering DOOM with Pygame, streaming pixels to badge")

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((RENDER_WIDTH, RENDER_HEIGHT))
    pygame.display.set_caption("DOOM -> Badge Stream")
    clock = pygame.time.Clock()

    # Initialize DOOM
    doom = SimpleDOOM(screen)

    frame_count = 0
    running = True

    print(f"📡 Streaming to badge at {BADGE_PORT}")
    print("🎯 Controls: WASD = move, Arrow keys = turn, ESC = quit")

    while running:
        # Handle input
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            doom.move_forward()
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            doom.move_backward()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            doom.turn_left()
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            doom.turn_right()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        # Render DOOM frame
        doom.render_frame()

        # Convert to badge pixels
        badge_pixels = pygame_surface_to_badge_pixels(screen)

        # Send to badge
        success = send_pixels_to_badge(badge_pixels)

        # Update display
        pygame.display.flip()

        frame_count += 1
        if frame_count % 30 == 0:
            print(f"📊 Frame {frame_count}, Badge: {'✅' if success else '❌'}, "
                  f"Pos: ({doom.player_x:.1f}, {doom.player_y:.1f})")

        # Target 15 FPS (badge can't handle more)
        clock.tick(15)

    pygame.quit()
    print("🛑 DOOM Pixel Streamer stopped")

if __name__ == "__main__":
    # Check requirements
    try:
        import pygame
        import PIL
        import numpy
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Install with: pip3 install pygame pillow numpy")
        sys.exit(1)

    main()