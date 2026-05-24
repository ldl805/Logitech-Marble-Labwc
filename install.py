#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import re

CONFIG_DIR = os.path.expanduser("~/.config/labwc")
CONFIG_FILE = os.path.join(CONFIG_DIR, "rc.xml")
SYSTEM_CONFIG = "/etc/xdg/labwc/rc.xml"
HWDB_FILE = "/etc/udev/hwdb.d/99-logitech-marble.hwdb"

SCROLL_BOTH_XML = """
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

SCROLL_LEFT_XML = """
  <mouse>
    <default />
    <context name="All">
      <!-- Small left button -->
      <mousebind button="Back" action="Press"><action name="EnableScrollWheelEmulation" /></mousebind>
      <mousebind button="Back" action="Release"><action name="DisableScrollWheelEmulation" /></mousebind>
      <mousebind button="Side" action="Press"><action name="EnableScrollWheelEmulation" /></mousebind>
      <mousebind button="Side" action="Release"><action name="DisableScrollWheelEmulation" /></mousebind>
    </context>
  </mouse>
"""

SCROLL_RIGHT_XML = """
  <mouse>
    <default />
    <context name="All">
      <!-- Small right button -->
      <mousebind button="Forward" action="Press"><action name="EnableScrollWheelEmulation" /></mousebind>
      <mousebind button="Forward" action="Release"><action name="DisableScrollWheelEmulation" /></mousebind>
      <mousebind button="Extra" action="Press"><action name="EnableScrollWheelEmulation" /></mousebind>
      <mousebind button="Extra" action="Release"><action name="DisableScrollWheelEmulation" /></mousebind>
    </context>
  </mouse>
"""

HWDB_RIGHT_MIDDLE = """# Logitech Trackman Marble (T-BC21) Button Remapping
# Right small button (scancode 90005) -> middle click
evdev:input:b0003v046DpC408*
 KEYBOARD_KEY_90005=btn_middle
"""

HWDB_LEFT_MIDDLE = """# Logitech Trackman Marble (T-BC21) Button Remapping
# Left small button (scancode 90004) -> middle click
evdev:input:b0003v046DpC408*
 KEYBOARD_KEY_90004=btn_middle
"""


def setup_udev_hwdb(hwdb_content):
    """Writes the udev hwdb rule and reloads the hwdb database."""
    print("\nConfiguring system-wide button remapping (requires root privileges)...")
    try:
        if os.geteuid() == 0:
            with open(HWDB_FILE, "w") as f:
                f.write(hwdb_content)
        else:
            # Run sudo tee to write to the system directory
            proc = subprocess.Popen(["sudo", "tee", HWDB_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate(input=hwdb_content)
            if proc.returncode != 0:
                print(f"❌ Failed to write udev hwdb file. Error:\n{stderr}")
                return False

        print(f"✅ Successfully wrote hwdb rule to {HWDB_FILE}")
        print("Updating hardware database and triggering udev reload...")
        subprocess.run(["sudo", "systemd-hwdb", "update"], check=True)
        subprocess.run(["sudo", "udevadm", "trigger", "--action=change"], check=True)
        print("✅ udev database reloaded successfully.")
        return True
    except Exception as e:
        print(f"❌ Error updating udev hwdb: {e}")
        return False


def remove_udev_hwdb():
    """Removes the custom udev hwdb rule if it exists."""
    if not os.path.exists(HWDB_FILE):
        return True

    print("\nRemoving custom system-wide button remapping (requires root privileges)...")
    try:
        if os.geteuid() == 0:
            os.remove(HWDB_FILE)
        else:
            subprocess.run(["sudo", "rm", "-f", HWDB_FILE], check=True)

        print("Updating hardware database and triggering udev reload...")
        subprocess.run(["sudo", "systemd-hwdb", "update"], check=True)
        subprocess.run(["sudo", "udevadm", "trigger", "--action=change"], check=True)
        print("✅ Custom udev hwdb rule removed and database reloaded.")
        return True
    except Exception as e:
        print(f"❌ Error removing udev hwdb: {e}")
        return False


def main():
    print("Logitech Trackman Marble (T-BC21) Labwc Scroll & Button Installer")
    print("=================================================================")
    print("Choose your preferred button configuration:")
    print("  1) Both small buttons act as scroll modifiers (Default/Original)")
    print("  2) Left small button scrolls, right small button is Middle Click")
    print("  3) Right small button scrolls, left small button is Middle Click")

    choice = input("Enter choice [1-3] (Default: 1): ").strip()
    if not choice:
        choice = "1"

    if choice == "1":
        scroll_xml = SCROLL_BOTH_XML
        hwdb_content = None
    elif choice == "2":
        scroll_xml = SCROLL_LEFT_XML
        hwdb_content = HWDB_RIGHT_MIDDLE
    elif choice == "3":
        scroll_xml = SCROLL_RIGHT_XML
        hwdb_content = HWDB_LEFT_MIDDLE
    else:
        print("❌ Invalid choice. Exiting.")
        sys.exit(1)

    # Configure rc.xml
    if not os.path.exists(CONFIG_DIR):
        print(f"Creating directory: {CONFIG_DIR}")
        os.makedirs(CONFIG_DIR)

    if not os.path.exists(CONFIG_FILE):
        if os.path.exists(SYSTEM_CONFIG):
            print(f"Copying system default config from {SYSTEM_CONFIG} to {CONFIG_FILE}...")
            shutil.copy(SYSTEM_CONFIG, CONFIG_FILE)
        else:
            print(f"Creating a minimal configuration at {CONFIG_FILE}...")
            with open(CONFIG_FILE, "w") as f:
                f.write('<?xml version="1.0"?>\n<openbox_config xmlns="http://openbox.org/3.4/rc">\n</openbox_config>\n')

    # Read existing content
    with open(CONFIG_FILE, "r") as f:
        content = f.read()

    # Clean up existing Logitech configuration (both new-style and old-style)
    if "EnableScrollWheelEmulation" in content:
        # Simple backup
        backup_path = CONFIG_FILE + ".bak"
        shutil.copy(CONFIG_FILE, backup_path)
        print(f"\nBacked up current configuration to: {backup_path}")

        # Remove our commented block if it exists
        content = re.sub(r'\s*<!-- Logitech-Marble-Labwc-Start -->.*?<!-- Logitech-Marble-Labwc-End -->', '', content, flags=re.DOTALL)
        # Remove old-style injected block if it exists
        content = re.sub(r'\s*<!-- Logitech Trackman Marble.*-->\s*<mouse>.*?</mouse>', '', content, flags=re.DOTALL)
        content = re.sub(r'\s*<mouse>\s*<default\s*/>\s*<context\s*name="All">.*?EnableScrollWheelEmulation.*?</context>\s*</mouse>', '', content, flags=re.DOTALL)

    # Check if a <mouse> block still exists (this would indicate user's custom bindings)
    if "<mouse>" in content:
        print("\n⚠️  A custom <mouse> section already exists in your rc.xml.")
        print("To avoid overwriting your existing mouse bindings, please manually add the following")
        print("to your <mouse><context name=\"All\"> section in ~/.config/labwc/rc.xml:")
        print(scroll_xml)
        if hwdb_content:
            setup_udev_hwdb(hwdb_content)
        else:
            remove_udev_hwdb()
        return

    # Backup the original config if we haven't done it already in this run
    if "EnableScrollWheelEmulation" not in content and not os.path.exists(CONFIG_FILE + ".bak"):
        backup_path = CONFIG_FILE + ".bak"
        shutil.copy(CONFIG_FILE, backup_path)
        print(f"\nBacked up original configuration to: {backup_path}")

    # Wrap the new scroll config in tracking markers
    wrapped_scroll_xml = f"\n  <!-- Logitech-Marble-Labwc-Start -->{scroll_xml}  <!-- Logitech-Marble-Labwc-End -->\n"

    # Inject the scroll XML before </openbox_config>
    if "</openbox_config>" in content:
        content = content.replace("</openbox_config>", wrapped_scroll_xml + "</openbox_config>")
        with open(CONFIG_FILE, "w") as f:
            f.write(content)
        print("\n✅ Successfully updated scroll emulation in rc.xml.")
    else:
        print("\n❌ Error: Could not find </openbox_config> tag in your rc.xml. File might be malformed.")
        sys.exit(1)

    # Configure udev hwdb rule
    if hwdb_content:
        setup_udev_hwdb(hwdb_content)
    else:
        remove_udev_hwdb()

    print("\nReloading labwc compositor...")
    os.system("labwc -r || killall -USR1 labwc >/dev/null 2>&1")
    print("Done! Please test your scroll and middle click behavior.")
    if hwdb_content:
        print("Note: If the middle click button is not immediately working, you may need to unplug and replug the trackball.")


if __name__ == "__main__":
    main()
