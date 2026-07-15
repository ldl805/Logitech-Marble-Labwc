import pytest
import re
from unittest.mock import patch, mock_open
import install

def test_check_device_connected_present():
    devices_content = """
I: Bus=0003 Vendor=046d Product=c408 Version=0110
N: Name="Logitech USB Trackball"
"""
    with patch("builtins.open", mock_open(read_data=devices_content)):
        with patch("os.path.exists", return_value=True):
            assert install.check_device_connected() is True

def test_check_device_connected_absent():
    devices_content = """
I: Bus=0003 Vendor=046d Product=405e Version=0111
N: Name="Logitech M720 Triathlon"
"""
    with patch("builtins.open", mock_open(read_data=devices_content)):
        with patch("os.path.exists", return_value=True):
            assert install.check_device_connected() is False

def test_check_device_connected_missing_file():
    with patch("os.path.exists", return_value=False):
        assert install.check_device_connected() is None

def test_get_updated_xml_no_mouse():
    xml_content = """<?xml version="1.0"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <keyboard>
  </keyboard>
</openbox_config>"""
    
    updated = install.get_updated_xml(xml_content, "1", install.BINDINGS_BOTH)
    assert "<mouse>" in updated
    assert "EnableScrollWheelEmulation" in updated
    assert "Logitech-Marble-Labwc-Start" in updated
    assert updated.count("Logitech-Marble-Labwc-Start") == 1

def test_get_updated_xml_with_existing_mouse_no_context():
    xml_content = """<?xml version="1.0"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <mouse>
    <default />
  </mouse>
</openbox_config>"""
    
    updated = install.get_updated_xml(xml_content, "1", install.BINDINGS_BOTH)
    assert "<mouse>" in updated
    assert "context name=\"All\"" in updated
    assert "EnableScrollWheelEmulation" in updated
    assert updated.count("Logitech-Marble-Labwc-Start") == 1

def test_get_updated_xml_with_existing_mouse_and_context():
    xml_content = """<?xml version="1.0"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <mouse>
    <default />
    <context name="All">
      <mousebind button="Left" action="Press"><action name="Focus" /></mousebind>
    </context>
  </mouse>
</openbox_config>"""
    
    updated = install.get_updated_xml(xml_content, "1", install.BINDINGS_BOTH)
    assert "mousebind button=\"Left\"" in updated
    assert "EnableScrollWheelEmulation" in updated
    assert updated.count("Logitech-Marble-Labwc-Start") == 1

def test_get_updated_xml_replaces_old_logitech_config():
    xml_content = """<?xml version="1.0"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <mouse>
    <default />
    <context name="All">
      <mousebind button="Left" action="Press"><action name="Focus" /></mousebind>
      <!-- Logitech-Marble-Labwc-Start -->
      <mousebind button="Back" action="Press"><action name="EnableScrollWheelEmulation" /></mousebind>
      <!-- Logitech-Marble-Labwc-End -->
    </context>
  </mouse>
</openbox_config>"""
    
    # We update it to profile 2 (scroll left only)
    updated = install.get_updated_xml(xml_content, "2", install.BINDINGS_LEFT)
    assert "mousebind button=\"Left\"" in updated
    assert "button=\"Back\"" in updated
    assert "button=\"Forward\"" not in updated # Forward is in Profile 1, but not 2
    assert updated.count("Logitech-Marble-Labwc-Start") == 1

def test_get_updated_xml_malformed():
    xml_content = """<openbox_config>"""
    with pytest.raises(ValueError, match="Could not find </openbox_config>"):
        install.get_updated_xml(xml_content, "1", install.BINDINGS_BOTH)
