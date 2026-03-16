#!/usr/bin/env python3
import os
import shutil

CONFIG_DIR = os.path.expanduser("~/.config/labwc")
CONFIG_FILE = os.path.join(CONFIG_DIR, "rc.xml")
SYSTEM_CONFIG = "/etc/xdg/labwc/rc.xml"

SCROLL_XML = """
  <!-- Logitech Trackman Marble (T-BC21) Scroll Emulation -->
  <mouse>
    <default />
    <context name="All">
      <!-- Small left button -->
      <mousebind button="Back" action="Press"><action name="EnableScrollWheelEmulation" /></mousebind>
      <mousebind button="Back" action="Release"><action name="DisableScrollWheelEmulation" /></mousebind>
      <mousebind button="Side" action="Press"><action name="EnableScrollWheelEmulation" /></mousebind>
      <mousebind button="Side" action="Release"><action name="DisableScrollWheelEmulation" /></mousebind>

      <!-- Small right button -->
      <mousebind button="Forward" action="Press"><action name="EnableScrollWheelEmulation" /></mousebind>
      <mousebind button="Forward" action="Release"><action name="DisableScrollWheelEmulation" /></mousebind>
      <mousebind button="Extra" action="Press"><action name="EnableScrollWheelEmulation" /></mousebind>
      <mousebind button="Extra" action="Release"><action name="DisableScrollWheelEmulation" /></mousebind>
    </context>
  </mouse>
"""


def main():
    print("Logitech Trackman Marble (T-BC21) Labwc Scroll Installer")
    print("========================================================")

    if not os.path.exists(CONFIG_DIR):
        print(f"Creating directory: {CONFIG_DIR}")
        os.makedirs(CONFIG_DIR)

    if not os.path.exists(CONFIG_FILE):
        if os.path.exists(SYSTEM_CONFIG):
            print(
                f"Copying system default config from {SYSTEM_CONFIG} to {CONFIG_FILE}...")
            shutil.copy(SYSTEM_CONFIG, CONFIG_FILE)
        else:
            print(f"Creating a minimal configuration at {CONFIG_FILE}...")
            with open(CONFIG_FILE, "w") as f:
                f.write(
                    '<?xml version="1.0"?>\n<openbox_config xmlns="http://openbox.org/3.4/rc">\n</openbox_config>\n')

    with open(CONFIG_FILE, "r") as f:
        content = f.read()

    if "EnableScrollWheelEmulation" in content:
        print("\n✅ Scroll wheel emulation already appears to be configured in your rc.xml.")
        print("No changes made.")
        return

    # Backup the original config
    backup_path = CONFIG_FILE + ".bak"
    shutil.copy(CONFIG_FILE, backup_path)
    print(f"\nBacked up original configuration to: {backup_path}")

    # Check if a <mouse> block already exists
    if "<mouse>" in content:
        print("\n⚠️  A <mouse> section already exists in your rc.xml.")
        print("To avoid overwriting your existing mouse bindings, please manually add the following")
        print("to your <mouse><context name=\"All\"> section in ~/.config/labwc/rc.xml:")
        print(SCROLL_XML)
        return

    # Inject the scroll XML before </openbox_config>
    if "</openbox_config>" in content:
        content = content.replace(
            "</openbox_config>", SCROLL_XML + "</openbox_config>")
        with open(CONFIG_FILE, "w") as f:
            f.write(content)
        print("\n✅ Successfully added scroll emulation to rc.xml.")

        print("Reloading labwc compositor...")
        os.system("labwc -r || killall -USR1 labwc >/dev/null 2>&1")
        print("Done! You can now hold either small button and move the ball to scroll.")
    else:
        print("\n❌ Error: Could not find </openbox_config> tag in your rc.xml. File might be malformed.")


if __name__ == "__main__":
    main()
