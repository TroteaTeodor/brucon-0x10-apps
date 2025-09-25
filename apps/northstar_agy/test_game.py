#!/usr/bin/env python3
"""
Test script for North Star AGY game
"""

# Mock the hardware modules for testing
class MockRGB:
    def clear(self):
        print("RGB: Clear display")

    def pixel(self, color, pos):
        r, g, b, a = color
        x, y = pos
        print(f"RGB: Pixel at ({x},{y}) with color RGB({r},{g},{b})")

    def image(self, data, pos, size):
        print(f"RGB: Image at {pos} with size {size}")

class MockButtons:
    BTN_A = "A"
    BTN_B = "B"

    def register(self, button, callback):
        print(f"Button {button} registered")

# Replace the hardware modules with mocks
import sys
sys.modules['rgb'] = MockRGB()
sys.modules['buttons'] = MockButtons()

# Now test the game
try:
    from northstar_agy import main, draw_simple_star, draw_text_ns2, draw_text_northstar, draw_text_agy
    print("✓ All imports successful!")
    print("✓ Game modules loaded correctly")
    print("✓ North Star AGY game is ready!")

    # Test some core functions
    print("\n--- Testing star drawing ---")
    draw_simple_star()

    print("\n--- Testing NS2 text ---")
    draw_text_ns2()

    print("\n--- Testing company name display ---")
    draw_text_northstar()
    draw_text_agy()

    print("\n🌟 North Star AGY animation game ready for badge!")

except Exception as e:
    print(f"❌ Error testing game: {e}")
    import traceback
    traceback.print_exc()