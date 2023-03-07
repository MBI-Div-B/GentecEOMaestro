# -*- coding: utf-8 -*-
#
# This file is part of the GentecEOMaestro project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" device Server for a Gentec EO Maestro Powermeter

"""

# PyTango imports
import tango
from tango import DebugIt
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from tango.server import device_property
from tango import AttrQuality, DispLevel, DevState
from tango import AttrWriteType, PipeWriteType
import enum
# Additional import
# PROTECTED REGION ID(GentecEOMaestro.additionnal_import) ENABLED START #
import serial
# PROTECTED REGION END #    //  GentecEOMaestro.additionnal_import

__all__ = ["GentecEOMaestro", "main"]


Range = enum.IntEnum(
    value="Range",
    names=[
        ("00 1 picowatt or picojoule", 0),
        ("01 3 picowatts or picojoules", 1),
        ("02 10 picowatts or picojoules", 2),
        ("03 30 picowatts or picojoules", 3),
        ("04 100 picowatts or picojoules", 4),
        ("05 300 picowatts or picojoules", 5),
        ("06 1 nanowatt or nanojoule", 6),
        ("07 3 nanowatts or nanojoules", 7),
        ("08 10 nanowatts or nanojoules", 8),
        ("09 30 nanowatts or nanojoules", 9),
        ("10 100 nanowatts or nanojoules", 10),
        ("11 300 nanowatts or nanojoules", 11),
        ("12 1 microwatt or microjoule", 12),
        ("13 3 microwatts or microjoules", 13),
        ("14 10 microwatts or microjoules", 14),
        ("15 30 microwatts or microjoules", 15),
        ("16 100 microwatts or microjoules", 16),
        ("17 300 microwatts or microjoules", 17),
        ("18 1 milliwatt or millijoule", 18),
        ("19 3 milliwatts or millijoules", 19),
        ("20 10 milliwatts or millijoules", 20),
        ("21 30 milliwatts or millijoules", 21),
        ("22 100 milliwatts or millijoules", 22),
        ("23 300 milliwatts or millijoules", 23),
        ("24 1 Watt or Joule", 24),
        ("25 3 watts or joules", 25),
        ("26 10 watts or joules", 26),
        ("27 30 watts or joules", 27),
        ("28 100 watts or joules", 28),
        ("29 300 watts or joules", 29),
        ("30 1 kilowatt or kilojoule", 30),
        ("31 3 kilowatts or kilojoules", 31),
        ("32 10 kilowatts or kilojoules", 32),
        ("33 30 kilowatts or kilojoules", 33),
        ("34 100 kilowatts or kilojoules", 34),
        ("35 300 kilowatts or kilojoules", 35),
        ("36 1 megawatt or megajoule", 36),
        ("37 3 megawatts or megajoules", 37),
        ("38 10 megawatts or megajoules", 38),
        ("39 30 megawatts or megajoules", 39),
        ("40 100 megawatts or megajoules", 40),
        ("41 300 megawatts or megajoules", 41),
    ]
)
"""Python enumerated type for Range attribute."""


class GentecEOMaestro(Device):
    """

    **Properties:**

    - Device Property
        Port
            - Serial port name
            - Type:'DevString'
    """
    # PROTECTED REGION ID(GentecEOMaestro.class_variable) ENABLED START #

    def send_query(self,cmd):
        self.pm.write(cmd.encoding)
        output = str(self.pm.readline()).replace('\r\n','').replace(' ','')
        return output

    # PROTECTED REGION END #    //  GentecEOMaestro.class_variable

    # -----------------
    # Device Properties
    # -----------------

    Port = device_property(
        dtype='DevString',
    )

    # ----------
    # Attributes
    # ----------

    range = attribute(
        dtype=Range,
        access=AttrWriteType.READ_WRITE,
        label="Range",
    )

    auto_range = attribute(
        dtype='DevBoolean',
        access=AttrWriteType.READ_WRITE,
        label="Auto Range",
    )

    trigger_level = attribute(
        dtype='DevFloat',
        access=AttrWriteType.READ_WRITE,
        label="Trigger Level",
        unit="%",
        format="%4.2f",
    )

    wave_corr = attribute(
        dtype='DevBoolean',
        access=AttrWriteType.READ_WRITE,
        label="Wavelenth correction",
    )

    wave_corr_value = attribute(
        dtype='DevDouble',
        access=AttrWriteType.READ_WRITE,
        label="Value for wavelenth correction",
        unit="nm",
        format="%5.0f",
        doc="This command is used to specify the wavelength in nm being used on the detector. The \nEEPROM in the detector contains measured spectral data for a wide range of wavelengths. If the \nwavelength input by the user is different from the predefined list of wavelengths on the device, a \ncustom value is interpolated. Specifying zero as a wavelength or providing an out-of-bound value \nas a parameter restores the default settings.",
    )

    meter_value = attribute(
        dtype='DevFloat',
        label="Measurement Value",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the GentecEOMaestro."""
        Device.init_device(self)
        # PROTECTED REGION ID(GentecEOMaestro.init_device) ENABLED START #
        self._range = Range["06 1 nanowatt or nanojoule"]
        self._auto_range = False
        self._trigger_level = 0.0
        self._wave_corr = False
        self._wave_corr_value = 0.0
        self._meter_value = 0.0

        self.pm = serial.Serial(self.Port,baudrate=115200, bytesize=8,  stopbits=1, timeout=1)
        self.pm.write(b"*VER")
        self.debug_stream(self.pm.readline())
        self.pm.write(b'*PWC00000')
        # PROTECTED REGION END #    //  GentecEOMaestro.init_devicey

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(GentecEOMaestro.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  GentecEOMaestro.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(GentecEOMaestro.delete_device) ENABLED START #
        self.pm.close()
        # PROTECTED REGION END #    //  GentecEOMaestro.delete_device
    # ------------------
    # Attributes methods
    # ------------------

    def read_range(self):
        # PROTECTED REGION ID(GentecEOMaestro.range_read) ENABLED START #
        """Return the range attribute."""
        self._range = Range(int(self.send_query('*GCR')))
        return self._range
        # PROTECTED REGION END #    //  GentecEOMaestro.range_read

    def write_range(self, value):
        # PROTECTED REGION ID(GentecEOMaestro.range_write) ENABLED START #
        """Set the range attribute."""
        if int(value)<10:
            value = b'0' + str(value).encode()
        self.pm.write(b'*SCS'+value)
        # PROTECTED REGION END #    //  GentecEOMaestro.range_write

    def read_auto_range(self):
        # PROTECTED REGION ID(GentecEOMaestro.auto_range_read) ENABLED START #
        """Return the auto_range attribute."""
        return bool(self.send_query('*GAS'))
        # PROTECTED REGION END #    //  GentecEOMaestro.auto_range_read

    def write_auto_range(self, value):
        # PROTECTED REGION ID(GentecEOMaestro.auto_range_write) ENABLED START #
        self.pm.write(b'*SAS'+str(value).encode)
        # PROTECTED REGION END #    //  GentecEOMaestro.auto_range_write

    def read_trigger_level(self):
        # PROTECTED REGION ID(GentecEOMaestro.trigger_level_read) ENABLED START #
        """Return the trigger_level attribute."""
        return float(self.send_query(b'*GTL'))
        # PROTECTED REGION END #    //  GentecEOMaestro.trigger_level_read

    def write_trigger_level(self, value):
        # PROTECTED REGION ID(GentecEOMaestro.trigger_level_write) ENABLED START #
        """Set the trigger_level attribute."""
        self.pm.write(b'*STL'+str(value).encode)
        # PROTECTED REGION END #    //  GentecEOMaestro.trigger_level_write

    def read_wave_corr(self):
        # PROTECTED REGION ID(GentecEOMaestro.wave_corr_read) ENABLED START #
        """Return the wave_corr attribute."""
        return self._wave_corr
        # PROTECTED REGION END #    //  GentecEOMaestro.wave_corr_read

    def write_wave_corr(self, value):
        # PROTECTED REGION ID(GentecEOMaestro.wave_corr_write) ENABLED START #
        """Set the wave_corr attribute."""
        if not value:
            self.pm.write(b'*PWC00000')
        self._wave_corr = value
        # PROTECTED REGION END #    //  GentecEOMaestro.wave_corr_write

    def read_wave_corr_value(self):
        # PROTECTED REGION ID(GentecEOMaestro.wave_corr_value_read) ENABLED START #
        """Return the wave_corr_value attribute."""
        return int(self.send_query(b'*GWL').replace('PWC:',''))
        # PROTECTED REGION END #    //  GentecEOMaestro.wave_corr_value_read

    def write_wave_corr_value(self, value):
        # PROTECTED REGION ID(GentecEOMaestro.wave_corr_value_write) ENABLED START #
        """Set the wave_corr_value attribute."""
        value = str(value)
        value = '0'*(5-len(value))+value
        self.pm.write(b'*PWC'+value.encode)
        # PROTECTED REGION END #    //  GentecEOMaestro.wave_corr_value_write

    def read_meter_value(self):
        # PROTECTED REGION ID(GentecEOMaestro.meter_value_read) ENABLED START #
        """Return the meter_value attribute."""
        return float(self.send_query('*CVU'))
        # PROTECTED REGION END #    //  GentecEOMaestro.meter_value_read

    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the GentecEOMaestro module."""
    # PROTECTED REGION ID(GentecEOMaestro.main) ENABLED START #
    return run((GentecEOMaestro,), args=args, **kwargs)
    # PROTECTED REGION END #    //  GentecEOMaestro.main


if __name__ == '__main__':
    main()
