#!/usr/bin/env python3
"""
Diode Matrix Keyboard Test
-------------------------
This script is specifically designed for testing a keyboard matrix with diodes.
The diodes allow current to flow from rows to columns, so the scanning approach
must be adjusted accordingly.

Usage:
1. Adjust ROW_PINS and COL_PINS to match your actual wiring
2. Run with: sudo python3 diode_matrix_test.py
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
    """Set up the GPIO pins for matrix scanning with diodes"""
    GPIO.setmode(GPIO.BCM)  # Use BCM numbering
    GPIO.setwarnings(False)
    
    # For a matrix with diodes from rows to columns:
    # 1. Set all rows as outputs (initially HIGH)
    # 2. Set all columns as inputs with pull-down resistors
    
    # Set rows as outputs (initially HIGH)
    for pin in ROW_PINS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
    
    # Set columns as inputs with pull-down resistors
    # Pull-down is important since diodes allow current to flow from row to column
    for pin in COL_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    print(f"GPIO setup complete for diode matrix.")
    print(f"Row pins (outputs, initially HIGH): {ROW_PINS}")
    print(f"Column pins (inputs with pull-down): {COL_PINS}")
    print(f"Using BCM pin numbering.")

def scan_matrix():
    """Scan the matrix for key presses, accounting for diodes"""
    print("\nPress keys on your matrix keyboard. Press Ctrl+C to exit.")
    print("With diodes, current flows from ROWS (outputs) to COLUMNS (inputs).")
    print("-" * 60)
    
    last_key = None
    last_key_time = 0
    
    try:
        while True:
            # Set all rows HIGH initially
            for r_pin in ROW_PINS:
                GPIO.output(r_pin, GPIO.HIGH)
            
            # Scan each row by setting it LOW and checking columns
            for r_index, r_pin in enumerate(ROW_PINS):
                # Set this row LOW (current can't flow from this row through diodes)
                GPIO.output(r_pin, GPIO.LOW)
                time.sleep(0.001)  # Short delay for signal propagation
                
                # Check all columns
                for c_index, c_pin in enumerate(COL_PINS):
                    # With diodes row->column, when key is pressed:
                    # - The row is LOW
                    # - The diode blocks current from column to row
                    # - The column is pulled DOWN by the resistor (reads LOW)
                    #
                    # When key is not pressed:
                    # - The column remains LOW due to pull-down
                    
                    # For a key press, we need to check if column is HIGH 
                    # (meaning current flowed from another HIGH row through the key and diode)
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
                
                # Reset the current row to HIGH before checking the next one
                GPIO.output(r_pin, GPIO.HIGH)
            
            # Small delay between full matrix scans
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up. Test complete.")

def test_diode_direction():
    """Test to determine the direction of your diodes"""
    print("\nDiode Direction Test")
    print("-------------------")
    print("This test will help confirm if your diodes allow current from rows to columns.")
    print("We'll set one row HIGH and check if columns detect it when keys are pressed.")
    
    # Set all pins as inputs initially
    for pin in ROW_PINS + COL_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # Test row -> column direction
    print("\nTesting ROW -> COLUMN direction (expected for your setup):")
    
    # Set first row as output HIGH
    test_row = ROW_PINS[0]
    GPIO.setup(test_row, GPIO.OUT)
    GPIO.output(test_row, GPIO.HIGH)
    print(f"Set row pin {test_row} HIGH. Press any key in the first row.")
    
    # Check columns for HIGH
    start_time = time.time()
    found = False
    while time.time() - start_time < 10 and not found:  # 10 second timeout
        for c_idx, c_pin in enumerate(COL_PINS):
            if GPIO.input(c_pin) == GPIO.HIGH:
                print(f"SUCCESS! Column pin {c_pin} detected HIGH when key pressed.")
                print("This confirms your diodes allow current from rows to columns.")
                found = True
                break
        time.sleep(0.1)
    
    if not found:
        print("No column detected HIGH. Try pressing different keys in the first row.")
        print("If still no detection, your diodes might be in the opposite direction.")
    
    # Clean up this test
    GPIO.setup(test_row, GPIO.IN)
    
    # Test column -> row direction (should fail with your diodes)
    print("\nTesting COLUMN -> ROW direction (should fail with your setup):")
    
    # Set first column as output HIGH
    test_col = COL_PINS[0]
    GPIO.setup(test_col, GPIO.OUT)
    GPIO.output(test_col, GPIO.HIGH)
    print(f"Set column pin {test_col} HIGH. Press any key in the first column.")
    
    # Check rows for HIGH
    start_time = time.time()
    found = False
    while time.time() - start_time < 10 and not found:  # 10 second timeout
        for r_idx, r_pin in enumerate(ROW_PINS):
            if GPIO.input(r_pin) == GPIO.HIGH:
                print(f"WARNING: Row pin {r_pin} detected HIGH when key pressed.")
                print("This suggests current is flowing from columns to rows,")
                print("which shouldn't happen with your diode configuration.")
                found = True
                break
        time.sleep(0.1)
    
    if not found:
        print("No row detected HIGH. This is expected with diodes from rows to columns.")
    
    print("\nDiode direction test complete.")

if __name__ == "__main__":
    print("Diode Matrix Keyboard Test")
    print("=========================")
    
    try:
        setup_gpio()
        
        print("\nChoose a test option:")
        print("1) Scan matrix for key presses")
        print("2) Test diode direction")
        
        choice = input("Enter option (1 or 2): ")
        
        if choice == "1":
            scan_matrix()
        elif choice == "2":
            test_diode_direction()
        else:
            print("Invalid option. Exiting.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()
        print("Test complete.") 