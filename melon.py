import sys
import time
import math
import random
from pathlib import Path

from minescript import (
	echo,
	player_get_targeted_block,
	player_press_attack,
	player,
	player_press_forward,
	player_press_left,
	player_press_right,
)

MELON_BLOCK_TYPES = {"minecraft:melon", "minecraft:melon_block"}
RUN_FILE = Path(__file__).with_suffix(".running")
RELEASE_GRACE_SECONDS = 0.12
STRAFE_STABLE_MIN = 0.2
STRAFE_STABLE_MAX = 0.5


def start_loop() -> None:
	RUN_FILE.write_text("running", encoding="utf-8")
	echo("Start")

	# Attack state
	is_attacking = False
	last_melon_seen_time = 0.0

	# Movement state: always hold forward, alternate left/right strafing
	player_press_forward(True)
	strafing_left = True
	player_press_left(True)
	player_press_right(False)

	# Z-block tracking for strafing switch
	last_z_block = None
	last_z_stable_time = time.time()
	next_stable_threshold = random.uniform(STRAFE_STABLE_MIN, STRAFE_STABLE_MAX)

	try:
		while RUN_FILE.exists():
			now = time.time()

			# ---- Melon attack handling ----
			targeted_block = player_get_targeted_block(6)
			looking_at_melon = (
				targeted_block is not None
				and targeted_block.type in MELON_BLOCK_TYPES
			)

			if looking_at_melon:
				last_melon_seen_time = now

			should_attack = looking_at_melon or (
				is_attacking and (now - last_melon_seen_time) <= RELEASE_GRACE_SECONDS
			)

			if should_attack != is_attacking:
				player_press_attack(should_attack)
				is_attacking = should_attack

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
							player_press_left(False)
							player_press_right(True)
							strafing_left = False
						else:
							player_press_right(False)
							player_press_left(True)
							strafing_left = True

						# reset stable timer and pick next threshold
						last_z_stable_time = now
						next_stable_threshold = random.uniform(STRAFE_STABLE_MIN, STRAFE_STABLE_MAX)

			time.sleep(0.01)
	finally:
		# cleanup: release keys
		player_press_attack(False)
		player_press_forward(False)
		player_press_left(False)
		player_press_right(False)
		if RUN_FILE.exists():
			RUN_FILE.unlink()


def stop_loop() -> None:
	if RUN_FILE.exists():
		RUN_FILE.unlink()
	player_press_attack(False)
	echo("Stop")


def main() -> None:
	action = sys.argv[1].lower() if len(sys.argv) > 1 else ""

	if action == "start":
		if RUN_FILE.exists():
			echo("laeuft bereits")
			return
		start_loop()
		return

	if action == "stop":
		stop_loop()
		return

	echo("Benutzung: \\main start | \\main stop")


main()
