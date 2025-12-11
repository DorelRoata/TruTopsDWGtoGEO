# -*- coding: utf-8 -*-
"""
Step Recorder - Record and label each action
After each click/keypress, type what the step does (or 'x' to ignore)
Press ESC when done recording.
"""

import time
from datetime import datetime
from pynput import mouse, keyboard
import threading

LOG_FILE = "labeled_steps.txt"

actions = []
running = True
start_time = None
current_action = None
waiting_for_label = False


def get_elapsed():
    if start_time:
        return round(time.time() - start_time, 2)
    return 0


def prompt_for_label():
    """Ask user to label the action."""
    global current_action, waiting_for_label

    if current_action:
        waiting_for_label = True

        if current_action["type"] == "click":
            print("\n  >> CLICK at ({}, {})".format(
                current_action["x"], current_action["y"]))
        else:
            print("\n  >> KEY: {}".format(current_action["key"]))

        label = input("  Label (or 'x' to skip): ").strip()

        if label.lower() != 'x' and label != '':
            current_action["label"] = label
            actions.append(current_action)
            print("  Saved: {}".format(label))
        else:
            print("  Skipped")

        current_action = None
        waiting_for_label = False


def on_click(x, y, button, pressed):
    global current_action, running

    if not running or waiting_for_label:
        return

    if pressed and button == mouse.Button.left:
        current_action = {
            "time": get_elapsed(),
            "type": "click",
            "x": x,
            "y": y
        }
        # Prompt in main thread
        threading.Thread(target=prompt_for_label, daemon=True).start()


def on_key(key):
    global current_action, running

    if key == keyboard.Key.esc:
        running = False
        return False

    if not running or waiting_for_label:
        return

    try:
        key_name = key.char
    except AttributeError:
        key_name = str(key).replace("Key.", "")

    # Skip modifier keys alone
    if key_name in ['shift', 'ctrl', 'alt', 'shift_r', 'ctrl_r', 'alt_r']:
        return

    current_action = {
        "time": get_elapsed(),
        "type": "key",
        "key": key_name
    }
    threading.Thread(target=prompt_for_label, daemon=True).start()


def save_results():
    with open(LOG_FILE, 'w') as f:
        f.write("# Step Recording - {}\n".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        f.write("# {} labeled steps\n".format(len(actions)))
        f.write("#" + "=" * 60 + "\n\n")

        f.write("WORKFLOW STEPS:\n")
        f.write("-" * 40 + "\n")

        for i, action in enumerate(actions, 1):
            if action["type"] == "click":
                f.write("{}. {} \n".format(i, action["label"]))
                f.write("   -> CLICK ({}, {})\n\n".format(
                    action["x"], action["y"]))
            else:
                f.write("{}. {}\n".format(i, action["label"]))
                f.write("   -> KEY: {}\n\n".format(action["key"]))

        f.write("\n" + "#" + "=" * 60 + "\n")
        f.write("# CONFIG FORMAT (copy to config.json):\n")
        f.write("#" + "=" * 60 + "\n\n")

        f.write('"click_locations": {\n')
        for action in actions:
            if action["type"] == "click":
                # Convert label to config key format
                key = action["label"].lower().replace(" ", "_").replace("'", "")
                f.write('    "{}": [{}, {}],\n'.format(
                    key, action["x"], action["y"]))
        f.write('},\n')

    print("\nResults saved to: {}".format(LOG_FILE))


def main():
    global start_time, running

    print("=" * 50)
    print("       STEP RECORDER")
    print("=" * 50)
    print()
    print("Instructions:")
    print("  1. Switch to TrueTops")
    print("  2. Perform each action")
    print("  3. Come back here and type what the action does")
    print("  4. Type 'x' to skip/ignore an action")
    print("  5. Press ESC when done")
    print()
    print("Recording starts in 3 seconds...")
    print()

    time.sleep(3)

    print("=" * 50)
    print("RECORDING - Press ESC to finish")
    print("=" * 50)

    start_time = time.time()

    mouse_listener = mouse.Listener(on_click=on_click)
    key_listener = keyboard.Listener(on_press=on_key)

    mouse_listener.start()
    key_listener.start()

    key_listener.join()

    running = False
    mouse_listener.stop()

    print("\n" + "=" * 50)
    print("RECORDING COMPLETE")
    print("=" * 50)

    save_results()

    print("\n{} steps recorded.".format(len(actions)))
    print("Review: {}".format(LOG_FILE))


if __name__ == "__main__":
    main()
