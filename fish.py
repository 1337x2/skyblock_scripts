import sys
import time
from pathlib import Path
from minescript import entities, player_press_use, echo, player_press_backward
import random

RUN_FILE = Path(__file__).with_suffix(".running")
times_reeled_in = 0

def cast_rod():
	global times_reeled_in
	times_reeled_in += 1
	player_press_use(True)
	player_press_use(False)

def armor_stand_exists():
	for entity in entities(nbt=True):
		nbt = getattr(entity, 'nbt', '')
		if isinstance(nbt, str) and (
			'CustomName' in nbt and '!!!' in nbt and
			'Marker:1b' in nbt and
			'Invisible:1b' in nbt
		):
			return True
	return False

def start_loop() -> None:
	global times_reeled_in
	RUN_FILE.write_text("running", encoding="utf-8")
	echo("Fishing started")
	times_reeled_in = 0
	player_press_backward(True)


	try:
		cast_repeat_delay = random.gauss(0.2, 0.2)
		if cast_repeat_delay < 0.1:
				cast_repeat_delay = cast_repeat_delay * -1
		while RUN_FILE.exists():
			if armor_stand_exists():
				cast_rod()
				time.sleep(cast_repeat_delay)
				cast_rod()
			time.sleep(0.5)
	finally:
		if RUN_FILE.exists():
			RUN_FILE.unlink()
		echo(f"Fishing stopped. Total reeled in: {times_reeled_in}")

def stop_loop() -> None:
	if RUN_FILE.exists():
		RUN_FILE.unlink()
	echo("Stop")
	player_press_backward(False)
	global times_reeled_in
	times_reeled_in = 0

def main() -> None:
	action = sys.argv[1].lower() if len(sys.argv) > 1 else ""

	if action == "start":
		if RUN_FILE.exists():
			echo("Fishing already running")
			return
		start_loop()
		return

	if action == "stop":
		stop_loop()
		return

	echo("Usage: \\main start | \\main stop")

main()
