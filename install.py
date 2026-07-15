#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import re
import argparse
from datetime import datetime

CONFIG_DIR = os.path.expanduser("~/.config/labwc")
CONFIG_FILE = os.path.join(CONFIG_DIR, "rc.xml")
SYSTEM_CONFIG = "/etc/xdg/labwc/rc.xml"
HWDB_FILE = "/etc/udev/hwdb.d/99-logitech-marble.hwdb"
QUIRKS_FILE = "/etc/libinput/local-overrides.quirks"

QUIRKS_CONTENT = """# BEGIN LOGITECH MARBLE LABWC OVERRIDE
[Logitech Trackman Marble Middle Click Override]
MatchUdevType=mouse
MatchBus=usb
MatchVendor=0x046D
MatchProduct=0xC408
AttrEventCode=+BTN_MIDDLE;
# END LOGITECH MARBLE LABWC OVERRIDE
"""

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

BINDINGS_BOTH = """
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
"""

BINDINGS_LEFT = """
      <!-- Small left button -->
      <mousebind button="Back" action="Press"><action name="EnableScrollWheelEmulation" /></mousebind>
      <mousebind button="Back" action="Release"><action name="DisableScrollWheelEmulation" /></mousebind>
      <mousebind button="Side" action="Press"><action name="EnableScrollWheelEmulation" /></mousebind>
      <mousebind button="Side" action="Release"><action name="DisableScrollWheelEmulation" /></mousebind>
"""

BINDINGS_RIGHT = """
      <!-- Small right button -->
      <mousebind button="Forward" action="Press"><action name="EnableScrollWheelEmulation" /></mousebind>
      <mousebind button="Forward" action="Release"><action name="DisableScrollWheelEmulation" /></mousebind>
      <mousebind button="Extra" action="Press"><action name="EnableScrollWheelEmulation" /></mousebind>
      <mousebind button="Extra" action="Release"><action name="DisableScrollWheelEmulation" /></mousebind>
"""

BINDINGS_MAP = {
    "1": BINDINGS_BOTH,
    "2": BINDINGS_LEFT,
    "3": BINDINGS_RIGHT
}

XML_MAP = {
    "1": SCROLL_BOTH_XML,
    "2": SCROLL_LEFT_XML,
    "3": SCROLL_RIGHT_XML
}

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


def check_device_connected():
    """Checks if the Logitech Trackman Marble is connected by searching /proc/bus/input/devices."""
    device_file = "/proc/bus/input/devices"
    if not os.path.exists(device_file):
        return None  # Can't verify (e.g. non-Linux system or file missing)
    try:
        with open(device_file, "r") as f:
            content = f.read()
        # Look for Vendor=046d Product=c408 (case-insensitive search)
        pattern = re.compile(r'Vendor=0*46d\s+Product=0*c408', re.IGNORECASE)
        return bool(pattern.search(content))
    except Exception:
        return None


def backup_config_file():
    """Creates a timestamped backup of the rc.xml configuration file."""
    if not os.path.exists(CONFIG_FILE):
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{CONFIG_FILE}.bak.{timestamp}"
    
    try:
        shutil.copy(CONFIG_FILE, backup_path)
        print(f"Backed up current configuration to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"⚠️  Warning: Failed to create backup at {backup_path}: {e}")
        # Try fallback to standard backup
        fallback_path = CONFIG_FILE + ".bak"
        try:
            shutil.copy(CONFIG_FILE, fallback_path)
            print(f"Backed up to fallback path: {fallback_path}")
            return fallback_path
        except Exception:
            print("❌ Critical: Could not create any backup of config file.")
            raise


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


def read_system_file(path):
    """Reads a file, using sudo if permission is denied."""
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "r") as f:
            return f.read()
    except PermissionError:
        proc = subprocess.run(["sudo", "cat", path], capture_output=True, text=True)
        if proc.returncode == 0:
            return proc.stdout
        return ""


def setup_libinput_quirk():
    """Ensures the libinput quirk for BTN_MIDDLE is present in local-overrides.quirks."""
    print("\nConfiguring libinput overrides for BTN_MIDDLE (requires root privileges)...")
    try:
        # Create directory if it doesn't exist
        if not os.path.exists("/etc/libinput"):
            if os.geteuid() == 0:
                os.makedirs("/etc/libinput", exist_ok=True)
            else:
                subprocess.run(["sudo", "mkdir", "-p", "/etc/libinput"], check=True)

        content = read_system_file(QUIRKS_FILE)

        # Check if already present
        if "# BEGIN LOGITECH MARBLE LABWC OVERRIDE" in content:
            # Replace existing block
            pattern = re.compile(
                r"# BEGIN LOGITECH MARBLE LABWC OVERRIDE.*?# END LOGITECH MARBLE LABWC OVERRIDE",
                re.DOTALL
            )
            content = pattern.sub(QUIRKS_CONTENT.strip(), content)
        else:
            # Append to file
            if content and not content.endswith("\n"):
                content += "\n"
            content += QUIRKS_CONTENT

        if os.geteuid() == 0:
            with open(QUIRKS_FILE, "w") as f:
                f.write(content)
        else:
            # Run sudo tee to write
            proc = subprocess.Popen(["sudo", "tee", QUIRKS_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate(input=content)
            if proc.returncode != 0:
                print(f"❌ Failed to write libinput quirks file. Error:\n{stderr}")
                return False

        print(f"✅ Successfully updated libinput quirks in {QUIRKS_FILE}")
        return True
    except Exception as e:
        print(f"❌ Error updating libinput quirks: {e}")
        return False


def remove_libinput_quirk():
    """Removes the custom libinput quirk if it exists."""
    if not os.path.exists(QUIRKS_FILE):
        return True

    print("\nRemoving custom libinput overrides for BTN_MIDDLE (requires root privileges)...")
    try:
        content = read_system_file(QUIRKS_FILE)

        if "# BEGIN LOGITECH MARBLE LABWC OVERRIDE" not in content:
            return True

        # Remove the block
        pattern = re.compile(
            r"# BEGIN LOGITECH MARBLE LABWC OVERRIDE.*?# END LOGITECH MARBLE LABWC OVERRIDE\n?",
            re.DOTALL
        )
        content = pattern.sub("", content)

        # If file is empty, we can delete it, otherwise write updated content
        if not content.strip():
            if os.geteuid() == 0:
                os.remove(QUIRKS_FILE)
            else:
                subprocess.run(["sudo", "rm", "-f", QUIRKS_FILE], check=True)
            print(f"✅ Removed empty quirks file {QUIRKS_FILE}")
        else:
            if os.geteuid() == 0:
                with open(QUIRKS_FILE, "w") as f:
                    f.write(content)
            else:
                proc = subprocess.Popen(["sudo", "tee", QUIRKS_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = proc.communicate(input=content)
                if proc.returncode != 0:
                    print(f"❌ Failed to update libinput quirks file. Error:\n{stderr}")
                    return False
            print(f"✅ Removed custom override block from {QUIRKS_FILE}")

        return True
    except Exception as e:
        print(f"❌ Error removing libinput quirks: {e}")
        return False


def get_updated_xml(content, choice, choice_bindings):
    """Updates the XML content string with the new bindings based on choice."""
    # Clean up existing Logitech configuration (both new-style and old-style)
    content = re.sub(
        r'\s*<!-- Logitech-Marble-Labwc-Start -->.*?<!-- Logitech-Marble-Labwc-End -->',
        '',
        content,
        flags=re.DOTALL
    )
    content = re.sub(r'\s*<!-- Logitech Trackman Marble.*-->\s*<mouse>.*?</mouse>', '', content, flags=re.DOTALL)
    content = re.sub(r'\s*<mouse>\s*<default\s*/>\s*<context\s*name="All">.*?EnableScrollWheelEmulation.*?</context>\s*</mouse>', '', content, flags=re.DOTALL)

    wrapped_bindings = f"\n      <!-- Logitech-Marble-Labwc-Start -->{choice_bindings.strip(chr(10))}\n      <!-- Logitech-Marble-Labwc-End -->\n"

    mouse_match = re.search(r'(<mouse\s*>.*?</mouse>)', content, flags=re.DOTALL)
    if mouse_match:
        mouse_block = mouse_match.group(1)
        # Check if context name="All" exists
        context_match = re.search(r'(<context\s+name=["\']All["\']\s*>)', mouse_block)
        if context_match:
            # Insert right inside the context name="All"
            context_start_idx = mouse_block.find(context_match.group(1))
            context_end_idx = mouse_block.find("</context>", context_start_idx)
            if context_end_idx != -1:
                new_mouse_block = (
                    mouse_block[:context_end_idx] +
                    wrapped_bindings +
                    mouse_block[context_end_idx:]
                )
                content = content.replace(mouse_block, new_mouse_block)
            else:
                # Fallback: append inside mouse block
                new_mouse_block = mouse_block.replace("</mouse>", f"    <!-- Logitech-Marble-Labwc-Start -->\n    <context name=\"All\">{choice_bindings}</context>\n    <!-- Logitech-Marble-Labwc-End -->\n</mouse>")
                content = content.replace(mouse_block, new_mouse_block)
        else:
            # Context name="All" does not exist, insert it into <mouse>
            new_mouse_block = mouse_block.replace("</mouse>", f"    <!-- Logitech-Marble-Labwc-Start -->\n    <context name=\"All\">{choice_bindings}</context>\n    <!-- Logitech-Marble-Labwc-End -->\n</mouse>")
            content = content.replace(mouse_block, new_mouse_block)
    else:
        # No <mouse> block exists, we create one and insert it before </openbox_config>
        if "</openbox_config>" in content:
            scroll_xml = XML_MAP[choice]
            # Wrap the new scroll config in tracking markers
            wrapped_scroll_xml = f"\n  <!-- Logitech-Marble-Labwc-Start -->{scroll_xml}  <!-- Logitech-Marble-Labwc-End -->\n"
            content = content.replace("</openbox_config>", wrapped_scroll_xml + "</openbox_config>")
        else:
            raise ValueError("Could not find </openbox_config> tag in your rc.xml. File might be malformed.")

    return content


def print_status():
    """Prints the current status of the Logitech Trackman Marble configuration and connection."""
    print("Logitech Trackman Marble (T-BC21) Status")
    print("========================================")
    
    # 1. Device Connection
    connected = check_device_connected()
    if connected is True:
        print("Device Status: 🟢 Connected (Logitech USB Trackball detected)")
    elif connected is False:
        print("Device Status: 🔴 Not detected (Ensure the trackball is plugged in)")
    else:
        print("Device Status: 🟡 Unknown (Could not read input devices)")

    # 2. Config files
    print("\nConfiguration Files:")
    
    # rc.xml
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                xml_content = f.read()
            if "Logitech-Marble-Labwc-Start" in xml_content:
                print(f"  - {CONFIG_FILE}: 🟢 Installed")
                if "EnableScrollWheelEmulation" in xml_content:
                    # Check which bindings are active
                    if "Forward" in xml_content and "Back" in xml_content:
                        print("    Active Profile: Profile 1 (Double Scroll)")
                    elif "Back" in xml_content:
                        print("    Active Profile: Profile 2 (Scroll Left / Middle Click Right)")
                    elif "Forward" in xml_content:
                        print("    Active Profile: Profile 3 (Middle Click Left / Scroll Right)")
            else:
                print(f"  - {CONFIG_FILE}: ⚪ Not installed")
        except Exception as e:
            print(f"  - {CONFIG_FILE}: ❌ Error reading file: {e}")
    else:
        print(f"  - {CONFIG_FILE}: 🔴 File not found")

    # udev hwdb
    if os.path.exists(HWDB_FILE):
        print(f"  - {HWDB_FILE}: 🟢 Installed")
        content = read_system_file(HWDB_FILE)
        if "KEYBOARD_KEY_90005=btn_middle" in content:
            print("    Rule: Right button -> Middle Click")
        elif "KEYBOARD_KEY_90004=btn_middle" in content:
            print("    Rule: Left button -> Middle Click")
    else:
        print(f"  - {HWDB_FILE}: ⚪ Not installed")

    # libinput override quirks
    if os.path.exists(QUIRKS_FILE):
        quirks_content = read_system_file(QUIRKS_FILE)
        if "LOGITECH MARBLE LABWC OVERRIDE" in quirks_content:
            print(f"  - {QUIRKS_FILE}: 🟢 Installed")
        else:
            print(f"  - {QUIRKS_FILE}: ⚪ Not installed (Override missing)")
    else:
        print(f"  - {QUIRKS_FILE}: ⚪ Not installed")


def uninstall():
    """Uninstalls all configurations, system rules, and restores configurations."""
    print("Uninstalling Logitech Trackman Marble configuration...")
    success = True

    # 1. Restore rc.xml
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                content = f.read()
            
            # Check if block exists
            if "Logitech-Marble-Labwc-Start" in content or "EnableScrollWheelEmulation" in content:
                # Backup before modifying
                backup_config_file()
                
                # Remove blocks
                content = re.sub(
                    r'\s*<!-- Logitech-Marble-Labwc-Start -->.*?<!-- Logitech-Marble-Labwc-End -->',
                    '',
                    content,
                    flags=re.DOTALL
                )
                content = re.sub(r'\s*<!-- Logitech Trackman Marble.*-->\s*<mouse>.*?</mouse>', '', content, flags=re.DOTALL)
                content = re.sub(r'\s*<mouse>\s*<default\s*/>\s*<context\s*name="All">.*?EnableScrollWheelEmulation.*?</context>\s*</mouse>', '', content, flags=re.DOTALL)

                with open(CONFIG_FILE, "w") as f:
                    f.write(content)
                print(f"✅ Removed custom configurations from {CONFIG_FILE}")
            else:
                print(f"ℹ️  No custom configurations found in {CONFIG_FILE}")
        except Exception as e:
            print(f"❌ Error removing configuration from rc.xml: {e}")
            success = False

    # 2. Remove udev hwdb
    if not remove_udev_hwdb():
        success = False

    # 3. Remove libinput quirks
    if not remove_libinput_quirk():
        success = False

    # 4. Reload compositor
    print("\nReloading labwc compositor...")
    try:
        subprocess.run("labwc -r || killall -USR1 labwc", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Compositor reload triggered.")
    except Exception as e:
        print(f"⚠️  Could not reload labwc: {e}")

    if success:
        print("\n🎉 Uninstall completed successfully!")
    else:
        print("\n⚠️  Uninstall completed with some errors. Please check the logs.")
    return success


def main():
    parser = argparse.ArgumentParser(
        description="Logitech Trackman Marble (T-BC21) Labwc Scroll & Button Installer"
    )
    parser.add_argument(
        "-p", "--profile",
        type=int,
        choices=[1, 2, 3],
        help="Select button configuration profile (1: Double Scroll, 2: Scroll/Middle Click, 3: Middle Click/Scroll)"
    )
    parser.add_argument(
        "-u", "--uninstall",
        action="store_true",
        help="Uninstall all configurations, remove udev/libinput rules, and restore rc.xml"
    )
    parser.add_argument(
        "-s", "--status",
        action="store_true",
        help="Check connection and status of configurations"
    )
    parser.add_argument(
        "-n", "--non-interactive",
        action="store_true",
        help="Run in non-interactive mode. If --profile is not specified, defaults to profile 1."
    )
    
    args = parser.parse_args()

    # Handle status action
    if args.status:
        print_status()
        return

    # Handle uninstall action
    if args.uninstall:
        uninstall()
        return

    # Connection check
    connected = check_device_connected()
    if connected is False:
        print("⚠️  Warning: Logitech Trackman Marble (T-BC21) was not detected on this system.")
        print("   Please check that the USB device is plugged in.")
        if not args.non-interactive:
            cont = input("Do you want to proceed with the configuration anyway? [y/N]: ").strip().lower()
            if cont != 'y':
                print("Exiting.")
                sys.exit(0)

    # Determine profile selection
    choice = None
    if args.profile is not None:
        choice = str(args.profile)
    elif args.non-interactive:
        print("Running in non-interactive mode. Defaulting to profile 1.")
        choice = "1"
    else:
        # Interactive selection
        print("Logitech Trackman Marble (T-BC21) Labwc Scroll & Button Installer")
        print("=================================================================")
        print("Choose your preferred button configuration:")
        print("  1) Both small buttons act as scroll modifiers (Default/Original)")
        print("  2) Left small button scrolls, right small button is Middle Click")
        print("  3) Right small button scrolls, left small button is Middle Click")
        print("  4) Restore default configurations (Uninstall custom settings)")
        
        user_input = input("Enter choice [1-4] (Default: 1): ").strip()
        if not user_input:
            choice = "1"
        elif user_input == "4":
            uninstall()
            return
        elif user_input in ["1", "2", "3"]:
            choice = user_input
        else:
            print("❌ Invalid choice. Exiting.")
            sys.exit(1)

    # Configure XML and rules based on choice
    if choice == "1":
        choice_bindings = BINDINGS_BOTH
        hwdb_content = None
    elif choice == "2":
        choice_bindings = BINDINGS_LEFT
        hwdb_content = HWDB_RIGHT_MIDDLE
    elif choice == "3":
        choice_bindings = BINDINGS_RIGHT
        hwdb_content = HWDB_LEFT_MIDDLE
    else:
        print("❌ Invalid profile. Exiting.")
        sys.exit(1)

    # Configure rc.xml
    if not os.path.exists(CONFIG_DIR):
        print(f"Creating directory: {CONFIG_DIR}")
        os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        if os.path.exists(SYSTEM_CONFIG):
            print(f"Copying system default config from {SYSTEM_CONFIG} to {CONFIG_FILE}...")
            shutil.copy(SYSTEM_CONFIG, CONFIG_FILE)
        else:
            print(f"Creating a minimal configuration at {CONFIG_FILE}...")
            with open(CONFIG_FILE, "w") as f:
                f.write('<?xml version="1.0"?>\n<openbox_config xmlns="http://openbox.org/3.4/rc">\n</openbox_config>\n')

    # Read existing content
    try:
        with open(CONFIG_FILE, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {CONFIG_FILE}: {e}")
        sys.exit(1)

    # Backup the original config
    backup_config_file()

    # Update XML content
    try:
        content = get_updated_xml(content, choice, choice_bindings)
        with open(CONFIG_FILE, "w") as f:
            f.write(content)
        print("✅ Successfully updated scroll emulation in rc.xml.")
    except Exception as e:
        print(f"❌ Error updating rc.xml: {e}")
        sys.exit(1)

    # Configure udev hwdb rule and libinput quirk override
    if hwdb_content:
        setup_udev_hwdb(hwdb_content)
        setup_libinput_quirk()
    else:
        remove_udev_hwdb()
        remove_libinput_quirk()

    print("\nReloading labwc compositor...")
    try:
        subprocess.run("labwc -r || killall -USR1 labwc", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Compositor reload triggered.")
    except Exception as e:
        print(f"⚠️  Could not reload labwc: {e}")

    print("Done! Please test your scroll and middle click behavior.")
    if hwdb_content:
        print("Note: Since we configured libinput quirks to enable the middle button, you MUST reboot, restart your graphical session, or unplug and replug the trackball for the changes to take effect.")


if __name__ == "__main__":
    main()
