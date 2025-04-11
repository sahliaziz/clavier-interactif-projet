import  keyboard_game
from time import sleep

keyboard_game.setup_gpio()

while True:
	key = keyboard_game.scan_keys()
	if key is not None:
		print(key)
	#sleep(0.02)

