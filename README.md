# Logitech-Marble-Labwc

A simple Python script to enable scroll wheel emulation for the Logitech Trackman Marble (T-BC21) trackball in the **labwc** Wayland compositor.

## Features
- Automatically detects and updates your `~/.config/labwc/rc.xml` file.
- Backs up your existing configuration.
- Supports both small buttons (Back/Forward) as scroll modifiers.

## Installation (Recommended)

### Option 1: Debian Package (Pi/Ubuntu/Debian)

Download the latest `.deb` file from the [Releases](https://github.com/ldl805/Logitech-Marble-Labwc/releases) page and install it using:

```bash
sudo apt update
sudo apt install ./logitech-marble-labwc_1.0_all.deb
```

Once installed, run the configuration utility:
```bash
logitech-marble-labwc
```

### Option 2: Run directly

1.  Clone the repository:
    ```bash
    git clone https://github.com/ldl805/Logitech-Marble-Labwc.git
    cd Logitech-Marble-Labwc
    ```
2.  Run the installer:
    ```bash
    python3 install.py
    ```

## Usage
Once configured, hold down either of the small buttons on your Logitech Marble and move the ball to scroll in any direction.

## License
MIT License
