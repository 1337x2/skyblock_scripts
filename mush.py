import sys
import time
import math
import random
from pathlib import Path

from minescript import (
	echo,
	player_press_attack,
	player,
	player_press_forward,
	player_press_backward,
	player_press_sneak,
)

RUN_FILE = Path(__file__).with_suffix(".running")
STRAFE_STABLE_MIN = 1
STRAFE_STABLE_MAX = 1.1

def sneak():
	player_press_sneak(True)
	time.sleep(0.1)
	player_press_sneak(False)

def start_loop() -> None:
	RUN_FILE.write_text("running", encoding="utf-8")
	echo("Start mushroom harvesting")

	# Movement state: always hold forward, alternate left/right strafing
	strafing_left = True
	player_press_forward(False)
	player_press_backward(True)
	player_press_attack(True)

	# Z-block tracking for strafing switch
	last_z_block = None
	last_z_stable_time = time.time()
	next_stable_threshold = random.uniform(STRAFE_STABLE_MIN, STRAFE_STABLE_MAX)

	try:
		while RUN_FILE.exists():
			now = time.time()
			# ---- Movement handling ----
			try:
				p = player()
				z = float(p.position[2])
			except Exception:
				z = None

			if z is not None:
				z_block = math.floor(z)
				if last_z_block is None or z_block != last_z_block:
					last_z_block = z_block
					last_z_stable_time = now
					# pick a new threshold for the next stable period
					next_stable_threshold = random.uniform(STRAFE_STABLE_MIN, STRAFE_STABLE_MAX)
				else:
					# still in same z-block
					if (now - last_z_stable_time) >= next_stable_threshold:
						# switch strafing side
						if strafing_left:
							player_press_forward(False)
							player_press_backward(True)
							strafing_left = False
							sneak()
						else:
							player_press_backward(False)
							player_press_forward(True)
							strafing_left = True

						# reset stable timer and pick next threshold
						last_z_stable_time = now
						next_stable_threshold = random.uniform(STRAFE_STABLE_MIN, STRAFE_STABLE_MAX)	
									
			time.sleep(0.01)
			
	finally:
		# cleanup: release keys
		player_press_attack(False)
		player_press_forward(False)
		player_press_backward(False)
		if RUN_FILE.exists():
			RUN_FILE.unlink()


def stop_loop() -> None:
	if RUN_FILE.exists():
		RUN_FILE.unlink()
	player_press_attack(False)
	echo("Stop mushroom harvesting")


def main() -> None:
	action = sys.argv[1].lower() if len(sys.argv) > 1 else ""

	if action == "start":
		if RUN_FILE.exists():
			echo("Mushroom harvesting is already running")
			return
		start_loop()
		return

	if action == "stop":
		stop_loop()
		return

	echo("Usage: \\mush start | \\mush stop")


main()