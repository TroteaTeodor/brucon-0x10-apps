#!/usr/bin/env python3
"""
DOOM Streamer - Run DOOM locally and stream to BruCON badge
Renders DOOM engine on computer, streams display to badge via USB
"""

import time
import math
import subprocess
import sys
import threading
from queue import Queue

# Badge communication
BADGE_PORT = "/dev/tty.usbmodem313371"
DISPLAY_WIDTH = 32
DISPLAY_HEIGHT = 19

class DOOMEngine:
    def __init__(self):
        # Game state
        self.player_x = 1.5
        self.player_y = 1.5
        self.player_angle = 0.0  # radians
        self.fov = math.pi / 3  # 60 degrees

        # Simple map
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

        self.map_width = 8
        self.map_height = 8

    def cast_ray(self, ray_angle):
        """Cast a ray using DDA algorithm"""
        dx = math.cos(ray_angle)
        dy = math.sin(ray_angle)

        x, y = self.player_x, self.player_y

        # DDA setup
        map_x = int(x)
        map_y = int(y)

        if dx == 0:
            delta_dist_x = 1e30
        else:
            delta_dist_x = abs(1 / dx)

        if dy == 0:
            delta_dist_y = 1e30
        else:
            delta_dist_y = abs(1 / dy)

        if dx < 0:
            step_x = -1
            side_dist_x = (x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - x) * delta_dist_x

        if dy < 0:
            step_y = -1
            side_dist_y = (y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - y) * delta_dist_y

        # DDA
        hit = False
        side = 0

        while not hit:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            if (map_x < 0 or map_x >= self.map_width or
                map_y < 0 or map_y >= self.map_height or
                self.world_map[map_y][map_x] > 0):
                hit = True

        # Calculate distance
        if side == 0:
            perp_wall_dist = (side_dist_x - delta_dist_x)
        else:
            perp_wall_dist = (side_dist_y - delta_dist_y)

        return max(0.1, perp_wall_dist), side

    def render_frame(self):
        """Render a frame and return RGB data for badge"""
        frame_data = []

        for x in range(DISPLAY_WIDTH):
            # Calculate ray angle
            camera_x = 2 * x / DISPLAY_WIDTH - 1
            ray_angle = self.player_angle + math.atan(camera_x * math.tan(self.fov / 2))

            # Cast ray
            distance, side = self.cast_ray(ray_angle)

            # Calculate wall height
            line_height = int(DISPLAY_HEIGHT / distance) if distance > 0 else DISPLAY_HEIGHT
            line_height = min(line_height, DISPLAY_HEIGHT)

            # Calculate draw bounds
            draw_start = max(0, (DISPLAY_HEIGHT - line_height) // 2)
            draw_end = min(DISPLAY_HEIGHT - 1, draw_start + line_height)

            # Wall color based on side and distance
            brightness = max(100, min(255, int(255 / (1 + distance * 0.3))))
            if side == 1:
                brightness = brightness // 2  # Darker for y-side walls

            wall_color = (brightness, brightness // 2, 0)  # Orange walls

            # Create column data
            column = []
            for y in range(DISPLAY_HEIGHT):
                if y < draw_start:
                    # Sky
                    column.append((50, 50, 100))
                elif y <= draw_end:
                    # Wall
                    column.append(wall_color)
                else:
                    # Floor
                    column.append((0, 60, 0))

            frame_data.append(column)

        # Add crosshair
        center_x, center_y = DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2
        if 0 <= center_x < DISPLAY_WIDTH and 0 <= center_y < DISPLAY_HEIGHT:
            frame_data[center_x][center_y] = (255, 255, 255)

        return frame_data

    def move_forward(self, speed=0.1):
        dx = math.cos(self.player_angle) * speed
        dy = math.sin(self.player_angle) * speed

        new_x = self.player_x + dx
        new_y = self.player_y + dy

        # Collision detection
        if (0 < new_x < self.map_width and
            0 < int(self.player_y) < self.map_height and
            self.world_map[int(self.player_y)][int(new_x)] == 0):
            self.player_x = new_x

        if (0 < new_y < self.map_height and
            0 < int(self.player_x) < self.map_width and
            self.world_map[int(new_y)][int(self.player_x)] == 0):
            self.player_y = new_y

    def move_backward(self, speed=0.1):
        self.move_forward(-speed)

    def turn_left(self, speed=0.1):
        self.player_angle -= speed

    def turn_right(self, speed=0.1):
        self.player_angle += speed

class BadgeStreamer:
    def __init__(self, port):
        self.port = port
        self.input_queue = Queue()

    def rgba_to_hex(self, r, g, b, a=0):
        """Convert RGBA to badge hex format"""
        return (r << 24) | (g << 16) | (b << 8) | a

    def send_frame(self, frame_data):
        """Send frame data to badge"""
        try:
            # Convert frame to badge format
            mpremote_cmd = [
                "python3", "-m", "mpremote",
                "connect", f"port:{self.port}",
                "exec", self.generate_display_code(frame_data)
            ]

            subprocess.run(mpremote_cmd, capture_output=True, timeout=0.1)

        except subprocess.TimeoutExpired:
            pass  # Continue if badge is busy
        except Exception as e:
            print(f"Badge communication error: {e}")

    def generate_display_code(self, frame_data):
        """Generate MicroPython code to display frame"""
        # Convert frame to hex values
        buffer_data = []
        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                r, g, b = frame_data[x][y]
                hex_color = self.rgba_to_hex(r, g, b)
                buffer_data.append(hex_color)

        # Generate MicroPython code
        code = f"""
import rgb
buffer = {buffer_data}
rgb.clear()
rgb.image(buffer, pos=(0, 0), size=({DISPLAY_WIDTH}, {DISPLAY_HEIGHT}))
"""
        return code

    def read_input(self):
        """Read input from badge (placeholder)"""
        # For now, simulate input from keyboard
        pass

def main():
    print("🎮 DOOM Badge Streamer - Starting...")
    print("This runs DOOM locally and streams to your badge!")

    # Initialize systems
    doom = DOOMEngine()
    streamer = BadgeStreamer(BADGE_PORT)

    print(f"📡 Connecting to badge at {BADGE_PORT}")
    print("🎯 Controls: WASD keys (simulated)")
    print("🖥️  Rendering at 32x19 resolution")
    print("🚀 Starting DOOM stream...")

    frame_count = 0
    last_time = time.time()

    try:
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # Simulate input (replace with actual badge input reading)
            # For demo: auto-rotate
            doom.turn_right(0.02)
            if frame_count % 200 == 0:
                doom.move_forward()

            # Render frame
            frame_data = doom.render_frame()

            # Stream to badge
            streamer.send_frame(frame_data)

            frame_count += 1

            if frame_count % 30 == 0:
                fps = 30 / (time.time() - current_time + dt * 30)
                print(f"📊 Frame {frame_count}, FPS: {fps:.1f}, Pos: ({doom.player_x:.1f}, {doom.player_y:.1f})")

            # Target 20 FPS
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n🛑 DOOM Streamer stopped")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    main()