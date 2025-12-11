# -*- coding: utf-8 -*-
"""
Step Recorder - Record all actions, then label them after
1. Perform your full workflow in TrueTops
2. Press ESC when done
3. Then label each action (or 'x' to skip)
"""

import time
from datetime import datetime
from pynput import mouse, keyboard

LOG_FILE = "labeled_steps.txt"

actions = []
running = True
start_time = None


def get_elapsed():
    if start_time:
        return round(time.time() - start_time, 2)
    return 0


def on_click(x, y, button, pressed):
    global running

    if not running:
        return False

    if pressed and button == mouse.Button.left:
        action = {
            "time": get_elapsed(),
            "type": "click",
            "x": x,
            "y": y,
            "label": ""
        }
        actions.append(action)
        print("  [{}s] CLICK at ({}, {})".format(action["time"], x, y))


def on_key(key):
    global running

    if key == keyboard.Key.esc:
        running = False
        return False

    try:
        key_name = key.char
    except AttributeError:
        key_name = str(key).replace("Key.", "")

    # Skip modifier keys alone
    if key_name in ['shift', 'ctrl', 'alt', 'shift_r', 'ctrl_r', 'alt_r', 'ctrl_l', 'shift_l', 'alt_l']:
        return

    action = {
        "time": get_elapsed(),
        "type": "key",
        "key": key_name,
        "label": ""
    }
    actions.append(action)
    print("  [{}s] KEY: {}".format(action["time"], key_name))


def label_actions():
    """Go through each action and ask for a label."""
    print("\n" + "=" * 50)
    print("LABELING PHASE")
    print("=" * 50)
    print("For each action, type what it does.")
    print("Type 'x' to skip/ignore an action.")
    print()

    labeled = []

    for i, action in enumerate(actions):
        print("-" * 40)
        print("Action {}/{}:".format(i + 1, len(actions)))

        if action["type"] == "click":
            print("  CLICK at ({}, {})".format(action["x"], action["y"]))
        else:
            print("  KEY: {}".format(action["key"]))

        label = input("  What does this do? (x to skip): ").strip()

        if label.lower() != 'x' and label != '':
            action["label"] = label
            labeled.append(action)
            print("  -> Labeled: {}".format(label))
        else:
            print("  -> Skipped")

    return labeled


def save_results(labeled_actions):
    with open(LOG_FILE, 'w') as f:
        f.write("# Step Recording - {}\n".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        f.write("# {} labeled steps\n".format(len(labeled_actions)))
        f.write("#" + "=" * 60 + "\n\n")

        f.write("WORKFLOW STEPS:\n")
        f.write("-" * 40 + "\n")

        for i, action in enumerate(labeled_actions, 1):
            if action["type"] == "click":
                f.write("{}. {}\n".format(i, action["label"]))
                f.write("   -> CLICK ({}, {})\n\n".format(
                    action["x"], action["y"]))
            else:
                f.write("{}. {}\n".format(i, action["label"]))
                f.write("   -> KEY: {}\n\n".format(action["key"]))

        f.write("\n" + "#" + "=" * 60 + "\n")
        f.write("# SUGGESTED CONFIG:\n")
        f.write("#" + "=" * 60 + "\n\n")

        f.write('"click_locations": {\n')
        for action in labeled_actions:
            if action["type"] == "click":
                key = action["label"].lower().replace(" ", "_").replace("'", "").replace("-", "_")
                f.write('    "{}": [{}, {}],\n'.format(key, action["x"], action["y"]))
        f.write('},\n')

        f.write('\n"key_actions": [\n')
        for action in labeled_actions:
            if action["type"] == "key":
                f.write('    # {} -> key: {}\n'.format(action["label"], action["key"]))
        f.write(']\n')

    print("\nResults saved to: {}".format(LOG_FILE))


def main():
    global start_time, running

    print("=" * 50)
    print("       STEP RECORDER")
    print("=" * 50)
    print()
    print("1. Switch to TrueTops")
    print("2. Perform your FULL workflow (all steps)")
    print("3. Press ESC when done")
    print("4. Then come back to label each action")
    print()
    print("Recording starts in 3 seconds...")
    time.sleep(3)

    print()
    print("=" * 50)
    print("RECORDING - Do your workflow, press ESC when done")
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
    print("RECORDING STOPPED - {} actions captured".format(len(actions)))
    print("=" * 50)

    if len(actions) == 0:
        print("No actions recorded.")
        return

    # Now label each action
    labeled = label_actions()

    if labeled:
        save_results(labeled)
        print("\n{} steps labeled and saved.".format(len(labeled)))
    else:
        print("\nNo steps labeled.")


if __name__ == "__main__":
    main()
