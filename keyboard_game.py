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
#Cols:0    1    2    3    4    5 (Pins: 7, 11, 13, 15, 19, 21)
    ['A', 'B', 'C', 'D', 'E', 'F'],   # Row 0 (Pin 8)
    ['G', 'H', 'I', 'J', 'K', 'L'],   # Row 1 (Pin 10)
    ['M', 'N', 'O', 'P', 'Q', 'R'],   # Row 2 (Pin 12)
    ['S', 'T', 'U', 'V', 'W', 'X'],   # Row 3 (Pin 16)
    ['Y', 'Z', '1', '2', '3', '4']    # Row 4 (Pin 18)
]

ALPHABET = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z") 


questions = {
    "Avion": "A", "Banane": "B", "Bateau": "B", "Biscuit": "B", "Bleu": "B", "Bougie": "B",
    "Fleur": "F", "Fourchette": "F", "Girafe": "G", "Grenouille": "G", "Grimace": "G", "Hibou": "H",
    "Homard": "H", "Jardin": "J", "Lapin": "L", "Lion": "L", "Lune": "L", "Lunette": "L",
    "Maison": "M", "Orange": "O", "Oreiller": "O", "Papillon": "P", "Parapluie": "P", "Pingouin": "P",
    "Presque": "P", "Quille": "Q", "Robot": "R", "Ronflement": "R", "Saumon": "S", "Scorpion": "S",
    "Serpent": "S", "Serviette": "S", "Souris": "S", "Symbole": "S", "Table": "T", "Tortue": "T",
    "Trampoline": "T", "Uniforme": "U", "Vache": "V", "Ventilateur": "V", "Zebre": "Z", "Yaourt": "Y"
}

questions_dur = {
    "alimentation": "A", "anniversaire": "A", "Anticipation": "A", "Aspirateur": "A", "Boulanger": "B", "Bienvenue": "B",
    "calculatrice": "C", "Carnivore": "C", "Cartouche": "C", "Catastrophe": "C", "Champignon": "C", "Chaussettes": "C",
    "chauvesouris": "C", "Chocolat": "C", "Compote": "C", "Crevette": "C", "Crocodile": "C", "Description": "D",
    "cinosaure": "D", "Dromadaire": "D", "Elephant": "E", "Escargot": "E", "Gaufrette": "G", "Hippopotame": "H",
    "imagination": "I", "Lamibulo": "L", "Majuscule": "M", "Motivation": "M", "Moustiques": "M", "Navigation": "N",
    "noyau": "N", "Orientation": "O", "Population": "P", "Publication": "P", "Radiateur": "R", "Salamandre": "S",
    "squelette": "S", "sympathie": "S", "Tournevis": "T", "Trottinette": "T", "Vocabulaire": "V", "Xylophone": "X"
}


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
        
    print("GPIO setup complete.")

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
    time.sleep(0.05)
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

def play_letter(letter, neutral=False):
    if letter.upper() in ALPHABET:
        if neutral:
            play_audio(letter.lower())
        else:
            play_audio(letter.lower() + str(random.randint(0, 3)))
    else:
        print(f"Warning: Letter {letter} invalid.")
        
def play_ou_est_lettre(letter) : 
    if letter.upper() in ALPHABET:
        play_audio("ou_est_la_lettre_" + letter.lower())
    else:
        print(f"Warning: Letter {letter} invalid.")
        
    
def play_peux_tu_trouver_la_lettre(letter) : 
    if letter.upper() in ALPHABET:
        play_audio("peux_tu_trouver_la_lettre_" + letter.lower())
    else:
        print(f"Warning: Letter {letter} invalid.")
        


# --- Game Levels ---

# niveau default / passif 
def level_0():
    play_audio("appuyez_sur_touche_pour_lettre")
    play_audio("appuyez_sur_4_quitter_jeu")
    while True:
        key = scan_keys()
        if key:
            if selected_level_key == '1':
                level_1()
            elif selected_level_key == '2':
                level_2()   
            elif selected_level_key == '3':
                level_3()
            elif selected_level_key == '4':
                play_audio("au_revoir")
                play_audio("retour_menu_confirmer")
                play_audio("retour_menu") 
                return # Needs "au_revoir.mp3"
             # Exit the main program loop
            else:
                play_letter(key, neutral=False) # Assumes "a.mp3", "b.mp3", etc. exist

        time.sleep(0.02) # Small delay to prevent high CPU usage

    


# def level_1():
#    play_audio("niveau_1")
#    play_audio("appuyez_sur_touche_pour_lettre")
#    play_audio("appuyez_sur_4_quitter_jeu")
#    while True:
#        key = scan_keys()
#        if key:
#            if key == '4': # 4 = exit key
#                play_audio("retour_menu_confirmer")
#                play_audio("retour_menu")  
#                break            else:
#                play_audio(key + str(random.randint(0, 3))) # Assumes "a.mp3", "b.mp3", etc. exist

#        time.sleep(0.02) # Small delay to prevent high CPU usage

def level_1():
    play_audio("niveau_1")
    play_audio("appuyez_sur_touche_pour_lettre")
    play_audio("appuyez_sur_4_quitter_jeu")
    counter = 1
    while True: # Loop for multiple questions
        target_letter = random.choice(ALPHABET)
        choice = random.randint(0,1)
        
        if choice == 0 :
            play_ou_est_lettre(target_letter) 
        elif choice == 1 :
            play_peux_tu_trouver_la_lettre(target_letter)
            
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
                    if choice == 0:
                        play_audio("bravo0") # Needs "bravo.mp3"
                        play_audio("cest_bien_la_lettre") # Needs "cest_bien_la_lettre.mp3"
                        play_audio(target_letter)
                        found = True
                    elif choice == 1:
                        play_audio("bravo1") # Needs "bravo.mp3"
                        play_audio("cest_bien_la_lettre") # Needs "cest_bien_la_lettre.mp3"
                        play_audio(target_letter)
                        found = True
                elif key == '4': # Allow exiting mid-question
                    play_audio("retour_menu_confirmer")
                    play_audio("retour_menu") 
                    return
                else:
                    play_audio("non")
                    play_audio("ca_cest_la_lettre")
                    play_letter(key, neutral=True) 
                    play_audio("essaie_encore")
                    play_ou_est_lettre(target_letter)
            time.sleep(0.02)

        if timed_out:
            play_audio("temps_ecoule")
            play_audio("la_lettre")

        counter=counter+1

        if counter%10 == 1 :
        # Ask if the user wants to continue
            play_audio("veux_tu_continuer")
            play_audio("appuie_sur_1_oui_2_non") 
            while True:
                key = scan_keys()
                if key == '1': # Assuming 'A' is top-left
                    break # Continue level 2 loop
                elif key == '2': # Assuming 'P' is bottom-right
                    play_audio("retour_menu_confirmer")
                    play_audio("retour_menu") 
                    return # Exit level 2 function
                time.sleep(0.02)

def level_2():
    play_audio("niveau_2") # Needs "niveau_3.mp3"
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
                elif key == '4': # Allow exiting mid-question
                    play_audio("retour_menu_confirmer")
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
            elif key == '4':
                play_audio("retour_menu_confirmer")
                play_audio("retour_menu") 
                return # Exit level 3 function
            time.sleep(0.02)

def level_3():
    play_audio("niveau_3")
    flat_key_map = {letter for row in KEY_MAP for letter in row if letter and letter != 'P'}

    mots = list(questions.keys())
    random.shuffle(mots)
    mots = mots[:10]
    mots_durs = list(questions_dur.keys())
    random.shuffle(mots_durs)

    # On commence avec les mots simples, puis on passe aux mots durs
    all_words = mots + mots_durs
    word_index = 0
    letter_pos = 0
    compteur = 0
    max_letter = 12  # douzieme_lettre

    while word_index < len(all_words) and letter_pos < max_letter:
        # On prend le bon mot selon l'étape (mots ou mots_durs)
        if word_index < 10:
            current_words = all_words[:10]
        else:
            current_words = all_words[10:]

        # On ne garde que les mots assez longs pour la lettre demandée
        available_words = [w for w in current_words if len(w) > letter_pos]
        if not available_words:
            break

        word = random.choice(available_words)
        target_letter = word[letter_pos].upper()
        if target_letter not in flat_key_map:
            # On retire ce mot pour cette position
            all_words.remove(word)
            continue

        # Choix du bon audio pour la position de la lettre
        if letter_pos == 0:
            play_audio("premiere_lettre")
        elif letter_pos == 1:
            play_audio("deuxieme_lettre")
        elif letter_pos == 2:
            play_audio("troisieme_lettre")
        elif letter_pos == 3:
            play_audio("quatrieme_lettre")
        elif letter_pos == 4:
            play_audio("cinquieme_lettre")
        elif letter_pos == 5:
            play_audio("sixieme_lettre")
        elif letter_pos == 6:
            play_audio("septieme_lettre")
        elif letter_pos == 7:
            play_audio("huitieme_lettre")
        elif letter_pos == 8:
            play_audio("neuvieme_lettre")
        elif letter_pos == 9:
            play_audio("dixieme_lettre")
        elif letter_pos == 10:
            play_audio("onzieme_lettre")
        elif letter_pos == 11:
            play_audio("douzieme_lettre")
        else:
            play_audio("lettre_suivante")

        play_audio(word.lower())

        start_time = time.time()
        found = False
        timed_out = False
        while not found and not timed_out:
            if time.time() - start_time > 30:
                timed_out = True
                break

            key = scan_keys()
            if key:
                if key == target_letter:
                    play_audio("oui")
                    play_audio(target_letter)
                    play_audio("comme_dans") 
                    play_audio(word)
                    play_audio("bravo")
                    found = True
                    compteur += 1
                    all_words.remove(word)
                elif key == '4':
                    play_audio("retour_menu_confirmer")
                    play_audio("retour_menu")
                    return
                else:
                    play_audio("non1")
                    play_audio("ca_cest_la_lettre")
                    play_audio(key)
                    play_audio("essaie_encore")
            time.sleep(0.02)

        if timed_out:
            play_audio("temps_ecoule")
            play_audio(word)
            play_audio("est")
            play_audio(target_letter)
            all_words.remove(word)

        # On passe à la lettre suivante chaque fois que 5 mots sont réussis
        if compteur > 0 and compteur % 5 == 0:
            letter_pos += 1

        # Après 10 mots réussis, on passe aux mots durs
        if compteur == 10:
            play_audio("niveau_questions_difficiles")
            # On continue la boucle, mais current_words sera mots_durs

        # Si plus de mots disponibles pour cette lettre, on passe à la suivante
        if not [w for w in current_words if len(w) > letter_pos]:
            letter_pos += 1

        # Si plus de mots du tout, on termine
        if not all_words:
            play_audio("toutes_questions_repondues")
            play_audio("felicitations")
            break

        # Demande si on continue
        play_audio("veux_tu_continuer")
        play_audio("appuie_sur_1_oui_2_non")
        while True:
            key = scan_keys()
            if key == '1':
                break
            elif key == '2':
                play_audio("retour_menu_confirmer")
                play_audio("retour_menu")
                return
            time.sleep(0.02)
    



# --- Main Program ---
if __name__ == "__main__":
    try:
        setup_gpio()
        play_audio("bienvenue") # Needs "bienvenue.mp3"
        

        # Main loop for level selection menu
        while True:
            
            level_selected = False
            selected_level_key = None

            level_0()

            # Wait for a valid menu selection
            while not selected_level_key:
                key = scan_keys()
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