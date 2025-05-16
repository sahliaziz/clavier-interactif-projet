import RPi.GPIO as GPIO
import time
import pygame
import os # To check for file existence
import random

# GPIO Pin Configuration (Adjust to your wiring!)

DEBOUNCE = 0.05

ROW_PINS = [8, 10, 12, 16, 18]
COL_PINS = [7, 11, 13, 15, 19, 21]

# Key Map (Example for 6x5 matrix - A to Z + None)
# Adjust this map to match your physical keyboard layout
KEY_MAP = [
#   Cols: 0   1   2   3   4   (Pins: 3, 5, 7, 11, 13, 15)
    ['A', 'B', 'C', 'D', 'E', 'F'],   # Row 0 (Pin 8)
    ['G', 'H', 'I', 'J', 'K', 'L'],   # Row 1 (Pin 10)
    ['M', 'N', 'O', 'P', 'Q', 'R'],   # Row 2 (Pin 12)
    ['S', 'T', 'U', 'V', 'W', 'X'],   # Row 3 (Pin 16)
    ['Y', 'Z', '1', '2', '3', '4'] # Row 5 (Pin 18)
]

# Debounce time (in seconds)
DEBOUNCE_TIME = 0.02 # 20ms

# --- Audio Setup ---
AUDIO_DIR = "audio/"
EXPECTED_AUDIO_EXT = ".mp3"

try:
    pygame.mixer.init()
    print("Pygame mixer initialized for audio playback.")
except Exception as e:
    print(f"Error initializing pygame mixer: {e}")
    print("Audio playback will not be available.")
    pygame = None # Disable pygame functions if init fails

# --- GPIO Setup ---
def setup_gpio():
    """Sets up the GPIO pins for the keyboard matrix with diodes - reversed approach."""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    # For our reversed approach:
    # 1. Set all rows as outputs (initially LOW)
    # 2. Set all columns as inputs with pull-down resistors
    
    # Set rows as outputs (initially LOW)
    for r_pin in ROW_PINS:
        GPIO.setup(r_pin, GPIO.OUT)
        GPIO.output(r_pin, GPIO.LOW)
    
    # Set columns as inputs with pull-down resistors
    for c_pin in COL_PINS:
        GPIO.setup(c_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
    print("GPIO setup complete for diode matrix keyboard (reversed approach).")

# --- Key Scanning ---
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

# --- Audio Playback ---
def play_audio(base_filename):
    """Plays an audio file from the AUDIO_DIR."""
    if not pygame or not pygame.mixer.get_init():
        print(f"Audio Disabled - Would play: {base_filename}")
        return

    # Construct filename (e.g., "a.mp3", "niveau_1.mp3")
    # Use lowercase and replace spaces/symbols if necessary in your actual files
    filename = base_filename.lower() + EXPECTED_AUDIO_EXT
    filepath = os.path.join(AUDIO_DIR, filename)

    if not os.path.exists(filepath):
        print(f"Warning: Audio file not found: {filepath}")
        return

    try:
        print(f"Playing: {filepath}")
        sound = pygame.mixer.Sound(filepath)
        sound.play()
        # Wait for the sound to finish playing
        while pygame.mixer.get_busy():
            time.sleep(0.05) # Short sleep to avoid busy-waiting
    except Exception as e:
        print(f"Error playing audio file {filepath}: {e}")

# --- Game Levels ---
def level_1():
    play_audio("niveau_1")
    play_audio("appuyez_sur_touche_pour_lettre") # Needs "appuyez_sur_touche_pour_lettre.mp3"
    play_audio("appuyez_sur_p_retour_menu") # Needs "appuyez_sur_p_retour_menu.mp3"
    while True: # Loop indefinitely for level 1 (or add exit condition)
        key = scan_keys()
        if key:
            if key == 'P': # Example exit key
                play_audio("retour_menu") # Needs "retour_menu.mp3"
                break
            else:
                play_audio(key) # Assumes "a.mp3", "b.mp3", etc. exist

        time.sleep(0.02) # Small delay to prevent high CPU usage

def level_2():
    play_audio("niveau_2") # Needs "niveau_2.mp3"
    # Flatten the key map to easily pick a random letter available on the keyboard
    available_letters = [letter for row in KEY_MAP for letter in row if letter and letter != 'P'] # Exclude exit key 'P'
    if not available_letters:
        play_audio("aucune_lettre_configuree") # Needs "aucune_lettre_configuree.mp3"
        play_audio("retour_menu")
        return

    while True: # Loop for multiple questions
        target_letter = random.choice(available_letters)
        play_audio("ou_est_la_lettre") # Needs "ou_est_la_lettre.mp3"
        play_audio(target_letter) # Plays the letter sound

        start_time = time.time()
        found = False
        timed_out = False
        while not found and not timed_out:
            if time.time() - start_time > 30: # Give 30 seconds to find
                timed_out = True
                break

            key = scan_keys()
            if key:
                if key == target_letter:
                    play_audio("bravo") # Needs "bravo.mp3"
                    play_audio("cest_bien_la_lettre") # Needs "cest_bien_la_lettre.mp3"
                    play_audio(target_letter)
                    found = True
                elif key == 'P': # Allow exiting mid-question
                    play_audio("retour_menu")
                    return
                else:
                    play_audio("non")
                    play_audio("ca_cest_la_lettre")
                    play_audio(key)
                    play_audio("essaie_encore")
                    # Optionally repeat the question sound
                    # play_audio("ou_est_la_lettre")
                    # play_audio(target_letter)
            time.sleep(0.02)

        if timed_out:
            play_audio("temps_ecoule")
            play_audio("la_lettre")
            play_audio(target_letter)
            play_audio("etait_ici") # Needs "etait_ici.mp3"
            # TODO: Maybe indicate the location? Requires mapping back from letter to row/col.

        # Ask if the user wants to continue
        play_audio("veux_tu_continuer")
        play_audio("appuie_sur_a_oui_p_non") # Needs "appuie_sur_a_oui_p_non.mp3"
        while True:
            key = scan_keys()
            if key == 'A': # Assuming 'A' is top-left
                break # Continue level 2 loop
            elif key == 'P': # Assuming 'P' is bottom-right
                play_audio("retour_menu")
                return # Exit level 2 function
            time.sleep(0.02)

def level_3():
    play_audio("niveau_3") # Needs "niveau_3.mp3"
    questions = {
        # MOTS A CHANGER!!
        # Ensure the target letter (value) exists in your KEY_MAP and is not 'P'
        "Kangourou": "K", "Avion": "A",   "Bateau": "B", "Chat": "C",
        "Maison": "M",    "Orange": "O",  "Lion": "L",   "Girafe": "G",
        "Elephant": "E",  "Nid": "N",     "Iguane": "I", "Jardin": "J",
        "Domino": "D",    "Fleur": "F",   "Hibou": "H",
        # Added examples for new letters (ensure audio files exist, e.g., "zebre.mp3")
        "Quille": "Q",    "Robot": "R",   "Serpent": "S", "Table": "T",
        "Uniforme": "U",  "Vache": "V",   "Wagon": "W",   "Xylophone": "X",
        "Yaourt": "Y",    "Zebre": "Z",
    }
    # Filter questions based on available keys (excluding 'P' and None)
    flat_key_map = {letter for row in KEY_MAP for letter in row if letter and letter != 'P'}
    available_questions = {word: letter for word, letter in questions.items()
                           if letter in flat_key_map}

    if not available_questions:
        play_audio("aucune_question_disponible") # Needs "aucune_question_disponible.mp3"
        play_audio("retour_menu")
        return

    words = list(available_questions.keys())

    while True: # Loop for multiple questions
        if not words:
            play_audio("plus_de_questions") # Needs "plus_de_questions.mp3"
            break # Exit the loop if no more words

        word = random.choice(words)
        target_letter = available_questions[word]
        play_audio("premiere_lettre_de") # Needs "premiere_lettre_de.mp3"
        play_audio(word) # Needs audio files for each word (e.g., "kangourou.mp3")

        start_time = time.time()
        found = False
        timed_out = False
        while not found and not timed_out:
             if time.time() - start_time > 30: # Give 30 seconds
                timed_out = True
                break

             key = scan_keys()
             if key:
                if key == target_letter:
                    play_audio("oui") # Needs "oui.mp3"
                    play_audio(target_letter)
                    play_audio("comme_dans") # Needs "comme_dans.mp3"
                    play_audio(word)
                    play_audio("bravo")
                    found = True
                    # Remove the word so it's not asked again immediately
                    if word in words:
                        words.remove(word)
                elif key == 'P': # Allow exiting mid-question
                    play_audio("retour_menu")
                    return
                else:
                    play_audio("non")
                    play_audio("ca_cest_la_lettre")
                    play_audio(key)
                    play_audio("essaie_encore")
             time.sleep(0.02)

        if timed_out:
            play_audio("temps_ecoule")
            play_audio("premiere_lettre_de")
            play_audio(word)
            play_audio("est") # Needs "est.mp3"
            play_audio(target_letter)
            # Remove the word even if timed out to avoid immediate repeat
            if word in words:
                words.remove(word)

        # Check if there are any words left before asking to continue
        if not words:
            play_audio("toutes_questions_repondues") # Needs "toutes_questions_repondues.mp3"
            break # Exit level 3 loop


        # Ask if the user wants to continue (similar to level 2)
        play_audio("veux_tu_continuer")
        play_audio("appuie_sur_a_oui_p_non")
        while True:
            key = scan_keys()
            if key == 'A':
                break # Continue level 3 loop
            elif key == 'P':
                play_audio("retour_menu")
                return # Exit level 3 function
            time.sleep(0.02)


# --- Main Program ---
if __name__ == "__main__":
    try:
        setup_gpio()
        play_audio("bonjour") # Needs "bonjour.mp3"
        play_audio("bienvenue") # Needs "bienvenue.mp3"

        # Main loop for level selection menu
        while True:
            play_audio("menu_prompt") # Needs "menu_prompt.mp3" for the main menu instruction
            
            level_selected = False
            selected_level_key = None

            # Wait for a valid menu selection
            while not selected_level_key:
                key = scan_keys()
                print(key)
                if key in ['1', '2', '3', '4']: # Check if key is a valid menu option
                    # Verify the key actually exists in the KEY_MAP
                    if any(key in row for row in KEY_MAP):
                         selected_level_key = key
                    else:
                         print(f"Warning: Menu key '{key}' pressed but not found in KEY_MAP.")
                         play_audio("touche")
                         play_audio(key + "0")
                         play_audio("non_configuree")
                         time.sleep(1)
                         play_audio("menu_prompt_court")
                time.sleep(0.02)

            # Execute selected action
            if selected_level_key == '1':
                 level_1()
            elif selected_level_key == '2':
                 level_2()
            elif selected_level_key == '3':
                 level_3()
            elif selected_level_key == '4':
                play_audio("au_revoir") # Needs "au_revoir.mp3"
                break # Exit the main program loop


    except KeyboardInterrupt:
        print("Programme interrompu par l'utilisateur.")
    except Exception as e:
        print(f"Une erreur est survenue: {e}")
        # Potentially log the error here
    finally:
        print("Nettoyage GPIO...")
        # Check if GPIO has been initialized before cleaning up
        # This avoids errors if setup_gpio() failed
        try:
             # Check a pin status or mode to see if setup ran
             # Or use a flag set in setup_gpio()
             if GPIO.getmode() is not None: # Check if mode was set
                 GPIO.cleanup()
                 print("GPIO nettoyé.")
             else:
                 print("GPIO non initialisé, pas de nettoyage nécessaire.")
        except Exception as gpio_e:
             print(f"Erreur lors du nettoyage GPIO: {gpio_e}")

        # Quit pygame mixer
        if pygame and pygame.mixer.get_init():
            pygame.mixer.quit()
            print("Pygame mixer quit.")
        print("Programme terminé.")