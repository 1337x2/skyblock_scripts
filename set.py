
import sys
import math

from minescript import player_set_orientation, echo


def normalize_yaw(yaw: float) -> float:
	# normalize to (-180, 180]
	y = ((yaw + 180.0) % 360.0) - 180.0
	return y


def clamp_pitch(pitch: float) -> float:
	# Minecraft pitch range is -90..90
	return max(-90.0, min(90.0, pitch))


def main() -> None:
	if len(sys.argv) < 3:
		echo("Verwendung: \\set <yaw> <pitch>")
		return

	try:
		yaw = float(sys.argv[1])
		pitch = float(sys.argv[2])
	except Exception:
		echo("Ungültige Werte. Bitte Zahlen für yaw und pitch angeben.")
		return

	yaw = normalize_yaw(yaw)
	pitch = clamp_pitch(pitch)

	success = player_set_orientation(yaw, pitch)
	if success:
		echo(f"Orientierung gesetzt: yaw={yaw:.2f}, pitch={pitch:.2f}")
	else:
		echo("Fehler beim Setzen der Orientierung.")


if __name__ == "__main__":
	main()

