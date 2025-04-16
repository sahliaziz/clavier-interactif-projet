import  keyboard_game
from time import sleep

keyboard_game.setup_gpio()
print(keyboard_game.ROW_PINS)
print(keyboard_game.COL_PINS)

while True:
	key = keyboard_game.scan_keys()
	if key is not None:
		print(key)
	sleep(0.02)

