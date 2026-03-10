# Logitech Trackman Marble (T-BC21) Scroll Emulation for Labwc

The Logitech Trackman Marble lacks a physical scroll wheel. This repository provides a script that safely configures the **Labwc** Wayland compositor to emulate scrolling. It allows you to hold down either of the small buttons (Left or Right) and move the trackball to act as a scroll wheel.

## Prerequisites
- A system running the **Labwc** Wayland compositor.
- Python 3

## Installation

Simply clone this repository and run the included installation script:

```bash
git clone https://github.com/ldl805/logitech-marble-labwc.git
cd logitech-marble-labwc
./install.py
```

### What does it do?
It safely modifies your local `~/.config/labwc/rc.xml` to add `mousebind` directives for `EnableScrollWheelEmulation` and `DisableScrollWheelEmulation`. It binds the `Back`, `Forward`, `Side`, and `Extra` mouse buttons (which map to the small trackball buttons) to act as scrolling modifiers for trackball movement.

If you already have a custom `<mouse>` section defined in your `rc.xml`, the script will not overwrite it. Instead, it will safely print the necessary XML snippet to your terminal for you to add manually, preventing it from corrupting your custom bindings.

## Reverting changes
The installation script creates a backup of your previous configuration before making any modifications. To easily revert the changes, run:

```bash
mv ~/.config/labwc/rc.xml.bak ~/.config/labwc/rc.xml
labwc -r
```
