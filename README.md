# Logitech-Marble-Labwc

A configuration utility to enable scroll wheel emulation and custom button remapping for the Logitech Trackman Marble (T-BC21) trackball in the **labwc** Wayland compositor.

## Features
- **Interactive Configuration**: Choose from 3 button mapping profiles.
- **Scroll Emulation**: Hold the designated small button and spin the trackball to scroll vertically or horizontally.
- **Middle Click Mapping**: Map the other small button to a dedicated Middle Click (simulating a scroll wheel click) for easy tab opening and pasting.
- **Auto Configuration**: Automatically detects and updates your `~/.config/labwc/rc.xml` file, backing up your existing configuration beforehand.
- **System-wide integration**: Automates the setup of necessary hardware database (`udev` `hwdb`) rules for middle-click emulation.

## Button Profiles
1. **Double Scroll (Default)**: Both small buttons act as scroll emulation triggers (original behavior).
2. **Scroll / Middle Click**: The left small button enables scrolling; the right small button acts as a dedicated Middle Click.
3. **Middle Click / Scroll**: The left small button acts as a dedicated Middle Click; the right small button enables scrolling.

## Installation

### Option 1: Debian Package (Pi/Ubuntu/Debian)

Download the latest `.deb` file from the [Releases](https://github.com/ldl805/Logitech-Marble-Labwc/releases) page and install it:

```bash
sudo apt update
sudo apt install ./logitech-marble-labwc_1.1.2_all.deb
```

Once installed, run the configuration utility:
```bash
logitech-marble-labwc
```

*Note: If you select a middle-click option (Option 2 or 3), the utility will request root (`sudo`) permissions to configure the hardware button mapping.*

### Option 2: Run directly

1. Clone the repository:
   ```bash
   git clone https://github.com/ldl805/Logitech-Marble-Labwc.git
   cd Logitech-Marble-Labwc
   ```
2. Run the installer:
   ```bash
   python3 install.py
   ```

## License
MIT License
