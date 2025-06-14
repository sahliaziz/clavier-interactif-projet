#!/usr/bin/env python3
"""
Minimal 5x6 matrix-keyboard demo for a Raspberry Pi
- physical pin numbers are used (GPIO.BOARD mode)
- rows are outputs (driven HIGH one-at-a-time)
- columns are inputs with pull-downs
"""

import RPi.GPIO as GPIO
import time
from keyboard_game import KEY_MAP, ROW_PINS, COL_PINS, DEBOUNCE


# ── GPIO setup ───────────────────────────────────────────────────────────────
def setup_gpio() -> None:
    GPIO.setmode(GPIO.BOARD)            # we are using physical numbers
    GPIO.setwarnings(False)

    for r in ROW_PINS:                  # rows start LOW
        GPIO.setup(r, GPIO.OUT, initial=GPIO.LOW)

    for c in COL_PINS:                  # columns pulled LOW internally
        GPIO.setup(c, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# ── Key-scan routine ─────────────────────────────────────────────────────────
def scan_keys() -> str | None:
    """Return first key detected, or None.  Never blocks for long."""
    # make sure every row is LOW
    for r in ROW_PINS:
        GPIO.output(r, GPIO.LOW)

    for r_idx, r_pin in enumerate(ROW_PINS):
        GPIO.output(r_pin, GPIO.HIGH)       # probe this row
        time.sleep(0.0008)                  # ≈800 µs settle

        for c_idx, c_pin in enumerate(COL_PINS):
            if GPIO.input(c_pin):           # column went HIGH
                time.sleep(DEBOUNCE)        # debounce check
                if GPIO.input(c_pin):       # still HIGH → accept
                    key = KEY_MAP[r_idx][c_idx]

                    GPIO.output(r_pin, GPIO.LOW)   # **drop row now**

                    # wait (non-blocking) until key released
                    t_start = time.time()
                    while GPIO.input(c_pin):
                        time.sleep(0.001)
                        # safety timeout (2 s)
                        if time.time() - t_start > 2:
                            break

                    return key
        GPIO.output(r_pin, GPIO.LOW)        # next row

    return None



# ── Demo loop ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        setup_gpio()
        print("Press keys… (Ctrl-C to quit)")
        while True:
            char = scan_keys()
            if char is not None:
                print(f"Key pressed: {char}")

    except KeyboardInterrupt:
        print("\nExiting…")

    finally:
        GPIO.cleanup()
