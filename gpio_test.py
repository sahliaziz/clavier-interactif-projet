#!/usr/bin/env python3
"""
GPIO Matrix Test Script for Keyboard
-----------------------------------
This script helps test if your GPIO matrix keyboard connections are working correctly.
It scans the matrix continuously and prints which key (row,col) is being pressed.

Usage:
1. Adjust ROW_PINS and COL_PINS to match your actual wiring
2. Run with: sudo python3 gpio_test.py
3. Press keys on your matrix keyboard - you should see output showing row/col positions 
   and the corresponding letter from KEY_MAP

Press Ctrl+C to exit
"""

import RPi.GPIO as GPIO
import time

# Use the same pin configuration as in your main keyboard_game.py
# Adjust these to match your actual wiring!
ROW_PINS = [5, 6, 13, 19, 26, 22]  # 6 rows
COL_PINS = [12, 16, 15, 21, 25]    # 5 columns

# Same KEY_MAP as in your keyboard_game.py for reference
KEY_MAP = [
    ['A', 'B', 'C', 'D', 'E'],  # Row 0
    ['F', 'G', 'H', 'I', 'J'],  # Row 1
    ['K', 'L', 'M', 'N', 'O'],  # Row 2
    ['P', 'Q', 'R', 'S', 'T'],  # Row 3
    ['U', 'V', 'W', 'X', 'Y'],  # Row 4
    ['Z', None, None, None, None]  # Row 5
]

# Debounce time (in seconds)
DEBOUNCE_TIME = 0.05  # 50ms

def setup_gpio():
    """Set up the GPIO pins for matrix scanning"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Set rows as outputs initially high
    for r_pin in ROW_PINS:
        GPIO.setup(r_pin, GPIO.OUT)
        GPIO.output(r_pin, GPIO.HIGH)
    
    # Set columns as inputs with pull-up resistors
    for c_pin in COL_PINS:
        GPIO.setup(c_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    print(f"GPIO setup complete. Testing {len(ROW_PINS)}x{len(COL_PINS)} matrix.")
    print(f"Row pins: {ROW_PINS}")
    print(f"Column pins: {COL_PINS}")

def test_gpio_matrix():
    """Test the GPIO matrix by scanning for key presses"""
    print("\nPress keys on your matrix keyboard. Press Ctrl+C to exit.")
    print("-" * 50)
    
    last_key = None
    last_key_time = 0
    
    try:
        while True:
            # Scan the matrix
            for r_index, r_pin in enumerate(ROW_PINS):
                # Drive the current row low
                GPIO.output(r_pin, GPIO.LOW)
                time.sleep(0.001)  # Short delay for signal propagation
                
                # Check columns for a low signal (key press)
                for c_index, c_pin in enumerate(COL_PINS):
                    if GPIO.input(c_pin) == GPIO.LOW:
                        # Debounce: wait and check again
                        time.sleep(DEBOUNCE_TIME / 2)
                        if GPIO.input(c_pin) == GPIO.LOW:
                            # Calculate key position
                            key_position = (r_index, c_index)
                            
                            # Only print if different from last key and time threshold passed
                            current_time = time.time()
                            if (key_position != last_key or 
                                    current_time - last_key_time > 0.5):
                                # Get the letter from KEY_MAP
                                try:
                                    letter = KEY_MAP[r_index][c_index]
                                    letter_str = letter if letter else "None"
                                except IndexError:
                                    letter_str = "OUT OF BOUNDS"
                                
                                # Print the detected key press
                                print(f"Key pressed at ROW {r_index} (pin {ROW_PINS[r_index]}), "
                                      f"COL {c_index} (pin {COL_PINS[c_index]}) "
                                      f"- Letter: {letter_str}")
                                
                                last_key = key_position
                                last_key_time = current_time
                            
                            # Wait for key release to prevent multiple detections
                            while GPIO.input(c_pin) == GPIO.LOW:
                                time.sleep(0.01)
                            
                            # Add a small delay after key release
                            time.sleep(0.1)
                
                # Reset the current row high before checking the next one
                GPIO.output(r_pin, GPIO.HIGH)
            
            # Small delay between full matrix scans
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up. Test complete.")

def test_individual_pins():
    """Test individual pins one by one"""
    print("\nTesting individual pins:")
    print("-" * 50)
    
    # Test each row pin as an output
    print("Testing ROW pins (outputs):")
    for pin in ROW_PINS:
        GPIO.setup(pin, GPIO.OUT)
        print(f"Setting pin {pin} LOW (should activate a whole row)")
        GPIO.output(pin, GPIO.LOW)
        time.sleep(1)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.5)
    
    # Reset all row pins to HIGH
    for pin in ROW_PINS:
        GPIO.output(pin, GPIO.HIGH)
    
    # Test each column pin's pull-up
    print("\nTesting COLUMN pins (inputs with pull-up):")
    for pin in COL_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        state = GPIO.input(pin)
        print(f"Pin {pin} state: {state} (should be 1/HIGH when not pressed)")
        time.sleep(0.5)
    
    print("\nIndividual pin tests complete.")

if __name__ == "__main__":
    print("GPIO Matrix Keyboard Test")
    print("========================")
    
    try:
        setup_gpio()
        
        # Ask which test to run
        print("\nChoose a test option:")
        print("1) Test full matrix (scan for key presses)")
        print("2) Test individual pins")
        
        choice = input("Enter option (1 or 2): ")
        
        if choice == "1":
            test_gpio_matrix()
        elif choice == "2":
            test_individual_pins()
        else:
            print("Invalid option. Exiting.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()
        print("Test complete.") 
