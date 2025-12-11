# -*- coding: utf-8 -*-
"""
Action Recorder
Records mouse clicks and keyboard presses to a log file for later review.
Press ESC to stop recording.
"""

import time
from datetime import datetime
from pynput import mouse, keyboard

# Output file
LOG_FILE = "recorded_actions.txt"

# Track state
start_time = None
actions = []
running = True


def get_elapsed():
    """Get elapsed time since recording started."""
    if start_time:
        return round(time.time() - start_time, 2)
    return 0


def on_click(x, y, button, pressed):
    """Handle mouse clicks."""
    if not running:
        return False

    if pressed:
        action = {
            "time": get_elapsed(),
            "type": "mouse_click",
            "x": x,
            "y": y,
            "button": str(button)
        }
        actions.append(action)
        print("[{}s] Mouse click at ({}, {}) - {}".format(action["time"], x, y, button))


def on_key_press(key):
    """Handle key presses."""
    global running

    # ESC to stop
    if key == keyboard.Key.esc:
        running = False
        return False

    try:
        key_name = key.char
    except AttributeError:
        key_name = str(key)

    action = {
        "time": get_elapsed(),
        "type": "key_press",
        "key": key_name
    }
    actions.append(action)
    print("[{}s] Key press: {}".format(action["time"], key_name))


def save_actions():
    """Save recorded actions to file."""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("# Action Recording - {}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        f.write("# Total duration: {} seconds\n".format(get_elapsed()))
        f.write("# Total actions: {}\n".format(len(actions)))
        f.write("#" + "=" * 60 + "\n\n")

        for i, action in enumerate(actions, 1):
            if action["type"] == "mouse_click":
                f.write("{}. [{}s] CLICK at ({}, {}) - {}\n".format(
                    i, action["time"], action["x"], action["y"], action["button"]))
            elif action["type"] == "key_press":
                f.write("{}. [{}s] KEY: {}\n".format(i, action["time"], action["key"]))

        f.write("\n" + "#" + "=" * 60 + "\n")
        f.write("# Suggested pyautogui code:\n")
        f.write("#" + "=" * 60 + "\n\n")

        prev_time = 0
        for action in actions:
            delay = round(action["time"] - prev_time, 2)
            if delay > 0.1:
                f.write("time.sleep({})\n".format(delay))

            if action["type"] == "mouse_click":
                f.write("pyautogui.click({}, {})  # {}\n".format(
                    action["x"], action["y"], action["button"]))
            elif action["type"] == "key_press":
                key = action["key"]
                if key.startswith("Key."):
                    key = key.replace("Key.", "")
                    f.write("pyautogui.press('{}')\n".format(key))
                elif len(key) == 1:
                    f.write("pyautogui.press('{}')\n".format(key))
                else:
                    f.write("pyautogui.hotkey({})  # May need adjustment\n".format(key))

            prev_time = action["time"]

    print("\nActions saved to: {}".format(LOG_FILE))


def main():
    global start_time, running

    print("=" * 50)
    print("       ACTION RECORDER")
    print("=" * 50)
    print()
    print("Recording will start in 3 seconds...")
    print("Press ESC to stop recording.")
    print()

    time.sleep(3)

    print("RECORDING STARTED!")
    print("-" * 50)

    start_time = time.time()

    # Start listeners
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_key_press)

    mouse_listener.start()
    keyboard_listener.start()

    # Wait for ESC
    keyboard_listener.join()

    running = False
    mouse_listener.stop()

    print("-" * 50)
    print("RECORDING STOPPED!")
    print()

    save_actions()

    print("\nRecorded {} actions in {} seconds.".format(len(actions), get_elapsed()))
    print("Review the file: {}".format(LOG_FILE))


if __name__ == "__main__":
    main()
