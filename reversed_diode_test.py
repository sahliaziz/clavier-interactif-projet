#!/usr/bin/env python3
"""
Reversed Diode Matrix Keyboard Test
----------------------------------
This script tests a keyboard matrix with diodes using a reversed approach:
1. All rows start LOW
2. Each row is set HIGH one at a time
3. Column pins are checked for HIGH signals (indicating key presses)

This approach may work better for some diode matrix configurations.

Usage:
1. Adjust ROW_PINS and COL_PINS to match your actual wiring
2. Run with: sudo python3 reversed_diode_test.py
3. Press keys on your matrix keyboard to see output

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
    """Set up the GPIO pins for matrix scanning with diodes - reversed approach"""
    GPIO.setmode(GPIO.BCM)  # Use BCM numbering
    GPIO.setwarnings(False)
    
    # For our reversed approach:
    # 1. Set all rows as outputs (initially LOW)
    # 2. Set all columns as inputs with pull-down resistors
    
    # Set rows as outputs (initially LOW)
    for pin in ROW_PINS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    
    # Set columns as inputs with pull-down resistors
    for pin in COL_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    print(f"GPIO setup complete for reversed diode matrix approach.")
    print(f"Row pins (outputs, initially LOW): {ROW_PINS}")
    print(f"Column pins (inputs with pull-down): {COL_PINS}")
    print(f"Using BCM pin numbering.")

def scan_matrix_reversed():
    """Scan the matrix for key presses using the reversed approach"""
    print("\nPress keys on your matrix keyboard. Press Ctrl+C to exit.")
    print("REVERSED APPROACH: All rows LOW, then each row HIGH one at a time.")
    print("-" * 60)
    
    last_key = None
    last_key_time = 0
    
    try:
        while True:
            # Set all rows LOW initially
            for r_pin in ROW_PINS:
                GPIO.output(r_pin, GPIO.LOW)
            
            # Scan each row by setting it HIGH and checking columns
            for r_index, r_pin in enumerate(ROW_PINS):
                # Set this row HIGH (current can flow from this row through diodes)
                GPIO.output(r_pin, GPIO.HIGH)
                time.sleep(0.001)  # Short delay for signal propagation
                
                # Check all columns
                for c_index, c_pin in enumerate(COL_PINS):
                    # With this reversed approach, when key is pressed:
                    # - Current row is HIGH
                    # - Current flows through key and diode to column
                    # - Column reads HIGH
                    
                    if GPIO.input(c_pin) == GPIO.HIGH:
                        # Debounce
                        time.sleep(DEBOUNCE_TIME/2)
                        if GPIO.input(c_pin) == GPIO.HIGH:
                            # A key press is detected
                            key_position = (r_index, c_index)
                            
                            current_time = time.time()
                            if (key_position != last_key or 
                                    current_time - last_key_time > 0.3):
                                
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
                
                # Reset the current row to LOW before checking the next one
                GPIO.output(r_pin, GPIO.LOW)
            
            # Small delay between full matrix scans
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up. Test complete.")

def test_all_rows_high():
    """Test the matrix by setting ALL rows high simultaneously"""
    print("\nALL ROWS HIGH Test")
    print("-----------------")
    print("This test sets ALL row pins HIGH simultaneously.")
    print("Press keys and we'll check if any column registers HIGH.")
    print("This can help determine if your matrix works with a simplified approach.")
    
    # Set rows as outputs (ALL HIGH)
    for pin in ROW_PINS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
    
    # Set columns as inputs with pull-down resistors
    for pin in COL_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    print(f"\nAll row pins set HIGH: {ROW_PINS}")
    print("Press any key on your keyboard...")
    print("(Press Ctrl+C to exit this test)")
    
    try:
        while True:
            found = False
            for c_index, c_pin in enumerate(COL_PINS):
                if GPIO.input(c_pin) == GPIO.HIGH:
                    print(f"Column {c_index} (pin {c_pin}) detected HIGH - Key press detected!")
                    found = True
            
            if found:
                # Brief pause after reporting key presses
                time.sleep(0.5)
            else:
                # Shorter pause during continuous scanning
                time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\nTest stopped by user.")

if __name__ == "__main__":
    print("Reversed Diode Matrix Keyboard Test")
    print("==================================")
    
    try:
        setup_gpio()
        
        print("\nChoose a test option:")
        print("1) Scan matrix using reversed approach (all rows LOW, then each HIGH)")
        print("2) Test with ALL rows HIGH simultaneously")
        
        choice = input("Enter option (1 or 2): ")
        
        if choice == "1":
            scan_matrix_reversed()
        elif choice == "2":
            test_all_rows_high()
        else:
            print("Invalid option. Exiting.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()
        print("Test complete.") 