import minescript as m


m.echo("Chat-Listener aktiv: 'sending to server' stoppt autosun")

with m.EventQueue() as events:
	events.register_chat_listener()
	while True:
		event = events.get()
		if event.type == m.EventType.CHAT and event.message.strip().lower() == "sending to server":
			m.execute("\autosun stop")
			m.echo("autosun stop ausgeführt")