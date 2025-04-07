import RPi.GPIO as GPIO
import time
import random
import pygame

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Define GPIO pins for the keyboard matrix
ROW_PINS = [5, 6, 13, 19]  # Example row pins
COL_PINS = [12, 16, 20, 21]  # Example column pins

# Map keys to letters
KEY_MAP = {
    (0, 0): 'A', (0, 1): 'B', (0, 2): 'C', (0, 3): 'D',
    (1, 0): 'E', (1, 1): 'F', (1, 2): 'G', (1, 3): 'H',
    (2, 0): 'I', (2, 1): 'J', (2, 2): 'K', (2, 3): 'L',
    (3, 0): 'M', (3, 1): 'N', (3, 2): 'O', (3, 3): 'P',
}

# Setup GPIO
GPIO.setmode(GPIO.BCM)
for pin in ROW_PINS + COL_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def play_audio(file_name):
    """Play an audio file."""
    pygame.mixer.music.load(file_name)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def detect_keypress():
    """Detect which key is pressed in the matrix."""
    for row_idx, row_pin in enumerate(ROW_PINS):
        GPIO.setup(row_pin, GPIO.OUT)
        GPIO.output(row_pin, GPIO.HIGH)
        for col_idx, col_pin in enumerate(COL_PINS):
            if GPIO.input(col_pin) == GPIO.HIGH:
                GPIO.setup(row_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                return row_idx, col_idx
        GPIO.setup(row_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    return None

def niveau_1():
    """Level 1# filepath: c:\Users\azizs\OneDrive\Documents\Python projects\clavier-interactif-projet\keyboard_game.py

import RPi.GPIO as GPIO
import time
import random
import pygame

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Define GPIO pins for the keyboard matrix
ROW_PINS = [5, 6, 13, 19]  # Example row pins
COL_PINS = [12, 16, 20, 21]  # Example column pins

# Map keys to letters
KEY_MAP = {
    (0, 0): 'A', (0, 1): 'B', (0, 2): 'C', (0, 3): 'D',
    (1, 0): 'E', (1, 1): 'F', (1, 2): 'G', (1, 3): 'H',
    (2, 0): 'I', (2, 1): 'J', (2, 2): 'K', (2, 3): 'L',
    (3, 0): 'M', (3, 1): 'N', (3, 2): 'O', (3, 3): 'P',
}

# Setup GPIO
GPIO.setmode(GPIO.BCM)
for pin in ROW_PINS + COL_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def play_audio(file_name):
    """Play an audio file."""
    pygame.mixer.music.load(file_name)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def detect_keypress():
    """Detect which key is pressed in the matrix."""
    for row_idx, row_pin in enumerate(ROW_PINS):
        GPIO.setup(row_pin, GPIO.OUT)
        GPIO.output(row_pin, GPIO.HIGH)
        for col_idx, col_pin in enumerate(COL_PINS):
            if GPIO.input(col_pin) == GPIO.HIGH:
                GPIO.setup(row_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                return row_idx, col_idx
        GPIO.setup(row_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    return None

def niveau_1():
    """Level 1