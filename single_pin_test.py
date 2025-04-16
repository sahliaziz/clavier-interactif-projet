#!/usr/bin/env python3
"""
Single GPIO Pin Test
-------------------
A very simple script to test a single GPIO pin in input mode.
The script continuously reads the state of the specified pin and reports any changes.

Usage:
1. Set the TEST_PIN variable to the GPIO pin number you want to test
2. Set PIN_MODE to either GPIO.BCM or GPIO.BOARD to match your understanding of the pin
3. Run with: sudo python3 single_pin_test.py
4. Connect the pin to GND (or press the button/key if one is connected) to see the state change

Press Ctrl+C to exit
"""

import RPi.GPIO as GPIO
import time

# Choose your numbering system (uncomment/comment as needed)
PIN_MODE = GPIO.BOARD  # Uses physical pin numbers (header pin numbers)
# PIN_MODE = GPIO.BCM   # Uses Broadcom GPIO numbers

# BOARD pin numbers (physical pin numbers on the header)
# e.g., Pin 29 = the actual 29th pin on the header
BOARD_PIN = 29  # Change this to the physical pin number you want to test

# BCM pin numbers (Broadcom GPIO numbers)
# e.g., GPIO5 = the 5th GPIO pin in the Broadcom numbering
BCM_PIN = 5     # Change this to the GPIO number you want to test

# The actual test pin will be set based on the mode
TEST_PIN = BOARD_PIN if PIN_MODE == GPIO.BOARD else BCM_PIN

# Common GND pins in BOARD numbering (physical pins)
# These are the pins you can connect to for testing
GND_PINS_BOARD = [6, 9, 14, 20, 25, 30, 34, 39]

def setup_gpio():
    """Set up the GPIO pin for testing"""
    GPIO.setmode(PIN_MODE)
    GPIO.setwarnings(True)
    
    # Set up the pin as an input with a pull-up resistor
    GPIO.setup(TEST_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    mode_name = "BOARD (Physical Pin)" if PIN_MODE == GPIO.BOARD else "BCM (GPIO Number)"
    pin_info = f"{TEST_PIN} ({mode_name})"
    
    print(f"\nGPIO setup complete using {mode_name} numbering.")
    print(f"Testing pin {pin_info} as INPUT with PULL-UP.")
    
    if PIN_MODE == GPIO.BOARD:
        print(f"For reference, GND pins (in BOARD numbering) are: {GND_PINS_BOARD}")
    else:
        print(f"For reference, GND pins (in BOARD physical numbering) are: {GND_PINS_BOARD}")
    
    print("\nTROUBLESHOOTING TIPS:")
    print("1. If always HIGH - Ensure you're connecting to a proper GND pin")
    print("2. Try using a jumper wire from the test pin directly to a GND pin")
    print("3. Double-check that you're using the correct pin numbering system")
    print("4. Make sure the button or connection is actually connected to this pin")
    
    print("\nThe pin should read HIGH (1) when not connected/pressed.")
    print("The pin should read LOW (0) when connected to GND/pressed.")

def test_pin():
    """Continuously read the pin state and report changes"""
    print("\nMonitoring pin state. Press Ctrl+C to exit.")
    print("-" * 50)
    
    last_state = None
    last_change_time = 0
    
    try:
        while True:
            # Read current pin state
            current_state = GPIO.input(TEST_PIN)
            current_time = time.time()
            
            # Report state changes, or periodic updates every 3 seconds
            if (current_state != last_state or 
                    (last_state is not None and current_time - last_change_time > 3)):
                
                state_str = "HIGH (1)" if current_state else "LOW (0)"
                status = "NOT PRESSED" if current_state else "PRESSED"
                
                print(f"Pin {TEST_PIN} state: {state_str} - {status} - Time: {time.strftime('%H:%M:%S')}")
                
                last_state = current_state
                last_change_time = current_time
            
            # Small delay to prevent high CPU usage
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up. Test complete.")

if __name__ == "__main__":
    print("Single GPIO Pin Test")
    print("===================")
    
    try:
        mode_str = "BOARD (Physical pins)" if PIN_MODE == GPIO.BOARD else "BCM (GPIO numbers)"
        print(f"Using {mode_str} pin numbering.")
        print(f"Testing {'physical pin' if PIN_MODE == GPIO.BOARD else 'GPIO'} {TEST_PIN}")
        
        setup_gpio()
        test_pin()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()
        print("Test complete.") 
