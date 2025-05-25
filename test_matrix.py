import RPi.GPIO as GPIO
import time
from keyboard_game import ROW_PINS, COL_PINS


def setup_gpio():
    """Sets up the GPIO pins for testing."""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    
    # Set rows as outputs (initially LOW)
    for r_pin in ROW_PINS:
        GPIO.setup(r_pin, GPIO.OUT)
        GPIO.output(r_pin, GPIO.LOW)
    
    # Set columns as inputs with pull-down resistors
    for c_pin in COL_PINS:
        GPIO.setup(c_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    print("GPIO setup complete for testing.")

def test_single_position(row_idx, col_idx):
    """Test a single position in the matrix."""
    r_pin = ROW_PINS[row_idx]
    c_pin = COL_PINS[col_idx]
    
    # Set the row HIGH
    GPIO.output(r_pin, GPIO.HIGH)
    time.sleep(0.01)  # Small delay for stability
    
    # Read the column
    value = GPIO.input(c_pin)
    
    # Set the row back to LOW
    GPIO.output(r_pin, GPIO.LOW)
    
    return value

def test_matrix():
    """Test every position in the matrix and report results."""
    print("\nStarting matrix test...")
    print("Testing each position (1 = HIGH, 0 = LOW):")
    print("\nRow/Col: ", end="")
    for col in range(len(COL_PINS)):
        print(f"{col:4}", end="")
    print("\n")
    
    for row in range(len(ROW_PINS)):
        print(f"Row {row:2}: ", end="")
        for col in range(len(COL_PINS)):
            value = test_single_position(row, col)
            print(f"{value:4}", end="")
        print()  # New line after each row
    
    print("\nLegend:")
    print("1 = Button press detected (HIGH)")
    print("0 = No button press (LOW)")

def main():
    try:
        setup_gpio()
        print("Matrix Test Program")
        print("Press Ctrl+C to exit")
        
        while True:
            test_matrix()
            print("\nPress Enter to test again, or Ctrl+C to exit...")
            input()
            
    except KeyboardInterrupt:
        print("\nTest terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete")

if __name__ == "__main__":
    main() 