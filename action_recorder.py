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
        print(f"[{action['time']}s] Mouse click at ({x}, {y}) - {button}")


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
    print(f"[{action['time']}s] Key press: {key_name}")


def save_actions():
    """Save recorded actions to file."""
    with open(LOG_FILE, 'w') as f:
        f.write(f"# Action Recording - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total duration: {get_elapsed()} seconds\n")
        f.write(f"# Total actions: {len(actions)}\n")
        f.write("#" + "=" * 60 + "\n\n")

        for i, action in enumerate(actions, 1):
            if action["type"] == "mouse_click":
                f.write(f"{i}. [{action['time']}s] CLICK at ({action['x']}, {action['y']}) - {action['button']}\n")
            elif action["type"] == "key_press":
                f.write(f"{i}. [{action['time']}s] KEY: {action['key']}\n")

        f.write("\n" + "#" + "=" * 60 + "\n")
        f.write("# Suggested pyautogui code:\n")
        f.write("#" + "=" * 60 + "\n\n")

        prev_time = 0
        for action in actions:
            delay = round(action["time"] - prev_time, 2)
            if delay > 0.1:
                f.write(f"time.sleep({delay})\n")

            if action["type"] == "mouse_click":
                f.write(f"pyautogui.click({action['x']}, {action['y']})  # {action['button']}\n")
            elif action["type"] == "key_press":
                key = action["key"]
                if key.startswith("Key."):
                    key = key.replace("Key.", "")
                    f.write(f"pyautogui.press('{key}')\n")
                elif len(key) == 1:
                    f.write(f"pyautogui.press('{key}')\n")
                else:
                    f.write(f"pyautogui.hotkey({key})  # May need adjustment\n")

            prev_time = action["time"]

    print(f"\nActions saved to: {LOG_FILE}")


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

    print(f"\nRecorded {len(actions)} actions in {get_elapsed()} seconds.")
    print(f"Review the file: {LOG_FILE}")


if __name__ == "__main__":
    main()
