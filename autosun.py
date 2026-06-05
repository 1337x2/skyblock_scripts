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
	getblock,
	player_press_sneak,
)

RUN_FILE = Path(__file__).with_suffix(".running")
STRAFE_STABLE_MIN = 1
STRAFE_STABLE_MAX = 1.1
SUNFLOWER_TIMEOUT = 15  # seconds without sunflowers before warping

# Warp target coordinates and trigger radius (in blocks)
WARP_TARGET = (-234, 67, 143)
WARP_RADIUS = 2
WARP_COMMAND = "/warp garden"
LOBBY_COMMAND = "/lobby"
SKYBLOCK_COMMAND = "/skyblock"

def is_facing_sunflower(x, y, z, yaw, reach: int = 4) -> bool:
	# Minecraft yaw: 0=South(+Z), 90=West(-X), 180=North(-Z), -90=East(+X)
	yaw_rad = math.radians(yaw)
	fdx = -math.sin(yaw_rad)
	fdz = math.cos(yaw_rad)
	for dist in range(1, reach + 1):
		bx = int(math.floor(x + fdx * dist))
		bz = int(math.floor(z + fdz * dist))
		for dy in range(0, 3):  # Sonnenblume ist 2 Blöcke hoch
			by = int(math.floor(y)) + dy
			try:
				block = getblock(bx, by, bz)
				if "sunflower" in block.lower():
					return True
			except Exception:
				pass
	return False


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

def sneak():
	player_press_sneak(True)
	time.sleep(0.1)
	player_press_sneak(False)

def _setup_movement(strafing_left: bool) -> None:
	player_press_attack(True)
	player_press_forward(True)
	if strafing_left:
		player_press_left(True)
		player_press_right(False)
	else:
		player_press_right(True)
		player_press_left(False)
	sneak()


def start_loop() -> None:
	RUN_FILE.write_text("running", encoding="utf-8")
	echo("Start sunflower/moonflower harvesting")
	echo(f"Will warp to '{WARP_COMMAND}' when within {WARP_RADIUS} blocks of {WARP_TARGET}")

	strafing_left = True
	_setup_movement(strafing_left)

	last_z_block = None
	last_z_stable_time = time.time()
	next_stable_threshold = random.uniform(STRAFE_STABLE_MIN, STRAFE_STABLE_MAX)
	last_sunflower_time = time.time()

	try:
		while RUN_FILE.exists():
			now = time.time()
			try:
				p = player()
				pos = p.position  # (x, y, z)
				x, y, z = float(pos[0]), float(pos[1]), float(pos[2])
				yaw = float(p.yaw)
			except Exception:
				x = y = z = yaw = None

			if x is not None and z is not None:
				# ---- Sunflower presence check ----
				if yaw is not None and is_facing_sunflower(x, y, z, yaw):
					last_sunflower_time = now
				elif now - last_sunflower_time >= SUNFLOWER_TIMEOUT:
					echo(f"Keine Sonnenblumen seit {SUNFLOWER_TIMEOUT}s — warpe und starte neu...")
					stop_movement()
					chat(LOBBY_COMMAND)
					time.sleep(10)
					chat(SKYBLOCK_COMMAND)
					time.sleep(10)
					chat(WARP_COMMAND)
					time.sleep(7)
					# Inline reset — alles wie beim ersten Start
					last_sunflower_time = time.time()
					last_z_block = None
					last_z_stable_time = time.time()
					next_stable_threshold = random.uniform(STRAFE_STABLE_MIN, STRAFE_STABLE_MAX)
					strafing_left = True
					_setup_movement(strafing_left)
					echo("Farming neugestartet")
					continue

				# ---- Warp trigger check ----
				if distance_to_target((x, y, z)) <= WARP_RADIUS:
					echo(f"Reached warp target {WARP_TARGET} — executing '{WARP_COMMAND}'")
					chat(WARP_COMMAND)
					time.sleep(5)

				# ---- Movement / strafing logic ----
				z_block = math.floor(z)
				if last_z_block is None or z_block != last_z_block:
					last_z_block = z_block
					last_z_stable_time = now
					next_stable_threshold = random.uniform(STRAFE_STABLE_MIN, STRAFE_STABLE_MAX)
				else:
					if (now - last_z_stable_time) >= next_stable_threshold:
						strafing_left = not strafing_left
						if strafing_left:
							player_press_right(False)
							player_press_left(True)
						else:
							player_press_left(False)
							player_press_right(True)
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
		while start_loop():
			echo("Warp abgeschlossen — starte Script neu...")
			time.sleep(1)
		return

	if action == "stop":
		stop_loop()
		return

	echo("Usage: \\autosun start | \\autosun stop")


main()