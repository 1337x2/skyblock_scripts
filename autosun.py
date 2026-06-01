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
	chat,
	player_press_right,
    player_press_left,
)
from failsafe import start_failsafe

RUN_FILE = Path(__file__).with_suffix(".running")
STRAFE_STABLE_MIN = 1
STRAFE_STABLE_MAX = 1.1

# Warp target coordinates and trigger radius (in blocks)
WARP_TARGET = (-234, 67, 143)
WARP_RADIUS = 2
WARP_COMMAND = "/warp garden"

def distance_to_target(pos) -> float:
	#Return the 3D Euclidean distance from pos to WARP_TARGET.
	dx = pos[0] - WARP_TARGET[0]
	dy = pos[1] - WARP_TARGET[1]
	dz = pos[2] - WARP_TARGET[2]
	return math.sqrt(dx * dx + dy * dy + dz * dz)


def stop_movement():
	#Release all held keys.
	player_press_attack(False)
	player_press_forward(False)
	player_press_backward(False)
	player_press_right(False)
	player_press_left(False)


def start_loop() -> None:
	start_failsafe()
	RUN_FILE.write_text("running", encoding="utf-8")
	echo("Start sunflower/moonflower harvesting")
	echo(f"Will warp to '{WARP_COMMAND}' when within {WARP_RADIUS} blocks of {WARP_TARGET}")

	strafing_left = True
	player_press_right(False)
	player_press_left(True)
	player_press_attack(True)
	player_press_forward(True)

	last_z_block = None
	last_z_stable_time = time.time()
	next_stable_threshold = random.uniform(STRAFE_STABLE_MIN, STRAFE_STABLE_MAX)

	try:
		while RUN_FILE.exists():
			now = time.time()
			try:
				p = player()
				pos = p.position  # (x, y, z)
				x, y, z = float(pos[0]), float(pos[1]), float(pos[2])
			except Exception:
				x = y = z = None

			if x is not None:
				# ---- Warp trigger check ----
				if distance_to_target((x, y, z)) <= WARP_RADIUS:
					echo(f"Reached warp target {WARP_TARGET} — executing '{WARP_COMMAND}'")
					chat(WARP_COMMAND)
					time.sleep(5)  # Wait for warp to complete before resuming movement 		

				# ---- Movement / strafing logic ----
				z_block = math.floor(z)
				if last_z_block is None or z_block != last_z_block:
					last_z_block = z_block
					last_z_stable_time = now
					next_stable_threshold = random.uniform(STRAFE_STABLE_MIN, STRAFE_STABLE_MAX)
				else:
					if (now - last_z_stable_time) >= next_stable_threshold:
						if strafing_left:
							player_press_right(False)
							player_press_left(True)
							strafing_left = False
						else:
							player_press_left(False)
							player_press_right(True)
							strafing_left = True

						last_z_stable_time = now
						next_stable_threshold = random.uniform(STRAFE_STABLE_MIN, STRAFE_STABLE_MAX)

			time.sleep(0.01)

	finally:
		stop_movement()
		if RUN_FILE.exists():
			RUN_FILE.unlink()


def stop_loop() -> None:
	if RUN_FILE.exists():
		RUN_FILE.unlink()
	player_press_attack(False)
	echo("Stop sunflower/moonflower harvesting")


def main() -> None:
	action = sys.argv[1].lower() if len(sys.argv) > 1 else ""

	if action == "start":
		if RUN_FILE.exists():
			echo("Sunflower/Moonflower harvesting is already running")
			return
		start_loop()
		return

	if action == "stop":
		stop_loop()
		return

	echo("Usage: \\autosun start | \\autosun stop")


main()