import minescript as m

HOTKEY = 296  # G-Taste (GLFW keycode)

m.echo("Hotkey-Listener aktiv (F7 = toggle)")

with m.EventQueue() as events:
    events.register_key_listener()
    while True:
        event = events.get()
        if event.type == m.EventType.KEY and event.key == HOTKEY and event.action == 1:
            from pathlib import Path
            run_file = Path(__file__).parent / "sugarcane.running"
            if run_file.exists():
                m.execute("\\sugarcane stop")
            else:
                m.execute("\\sugarcane start")