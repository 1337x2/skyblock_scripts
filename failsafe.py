"""Fail-safe module to terminate on specific chat messages."""

import os
import sys
import threading
from minescript import EventQueue, echo


def start_failsafe(trigger_message: str = "Sending to server", daemon: bool = True) -> None:
	"""Start monitoring chat for a trigger message that will terminate the program.

	Args:
	    trigger_message: the chat message to watch for (default: "Sending to server")
	    daemon: if True, run listener as daemon thread so it doesn't block script exit
	"""
	def monitor_chat():
		try:
			with EventQueue() as event_queue:
				event_queue.register_chat_listener()
				while True:
					event = event_queue.get()
					if trigger_message in event.message:
						echo(f"FAILSAFE TRIGGERED: '{trigger_message}' detected in chat")
						echo("Terminating program...")
						os._exit(0)
		except Exception as e:
			echo(f"Failsafe error: {e}")

	thread = threading.Thread(target=monitor_chat, daemon=daemon)
	thread.start()
