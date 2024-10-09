#!/usr/bin/python3 -u
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
unit_lib = {
    b'0': 'W',
    b'1': 'J',
    b'2': 'J (singe shot)',
    b'6': 'dBm'
}
# PROTECTED REGION END #    //  GentecEOMaestro.additionnal_import

__all__ = ["GentecEOMaestro", "main"]


Range = enum.IntEnum(
    value="Range",
    names=[
        ("1 picowatt or picojoule", 0),
        ("3 picowatts or picojoules", 1),
        ("10 picowatts or picojoules", 2),
        ("30 picowatts or picojoules", 3),
        ("100 picowatts or picojoules", 4),
        ("300 picowatts or picojoules", 5),
        ("1 nanowatt or nanojoule", 6),
        ("3 nanowatts or nanojoules", 7),
        ("10 nanowatts or nanojoules", 8),
        ("30 nanowatts or nanojoules", 9),
        ("100 nanowatts or nanojoules", 10),
        ("300 nanowatts or nanojoules", 11),
        ("1 microwatt or microjoule", 12),
        ("3 microwatts or microjoules", 13),
        ("10 microwatts or microjoules", 14),
        ("30 microwatts or microjoules", 15),
        ("100 microwatts or microjoules", 16),
        ("300 microwatts or microjoules", 17),
        ("1 milliwatt or millijoule", 18),
        ("3 milliwatts or millijoules", 19),
        ("10 milliwatts or millijoules", 20),
        ("30 milliwatts or millijoules", 21),
        ("100 milliwatts or millijoules", 22),
        ("300 milliwatts or millijoules", 23),
        ("1 Watt or Joule", 24),
        ("3 watts or joules", 25),
        ("10 watts or joules", 26),
        ("30 watts or joules", 27),
        ("100 watts or joules", 28),
        ("300 watts or joules", 29),
        ("1 kilowatt or kilojoule", 30),
        ("3 kilowatts or kilojoules", 31),
        ("10 kilowatts or kilojoules", 32),
        ("30 kilowatts or kilojoules", 33),
        ("100 kilowatts or kilojoules", 34),
        ("300 kilowatts or kilojoules", 35),
        ("1 megawatt or megajoule", 36),
        ("3 megawatts or megajoules", 37),
        ("10 megawatts or megajoules", 38),
        ("30 megawatts or megajoules", 39),
        ("100 megawatts or megajoules", 40),
        ("300 megawatts or megajoules", 41),
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
    def send_query(self, cmd):
        self.debug_stream('in query')
        self.debug_stream(cmd)
        # self.write(self.pm.in_waiting)  # deleting all old data in que
        self.write(str(cmd))
        res = self.read().decode('utf8').strip()
        if res.find(':') == -1:
            output = res
        else:
            output = res.split(':')[1]

        self.debug_stream(output)
        self.debug_stream('out querry')
        return output

    # PROTECTED REGION END #    //  GentecEOMaestro.class_variable

    # -----------------
    # Device Properties
    # -----------------


    ConnectType = device_property(
        dtype="str",
        default_value="serial",
        doc="either `net` or `serial`"
    )

    SerialPort = device_property(
        dtype="str",
        default_value="/dev/ttyUSB0",
        doc="Serial port of device",
    )

    Baudrate = device_property(
        dtype="int",
        default_value=115200,
        doc="Baudrate of serial port",
    )

    HostName = device_property(
        dtype="str",
        default_value="device.domain",
        doc="Hostname / IP address of device",
    )

    PortNumber = device_property(
        dtype="int",
        default_value=20,
        doc="Socket port number of device",
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
        format="%6.4f",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the GentecEOMaestro."""
        Device.init_device(self)
        # PROTECTED REGION ID(GentecEOMaestro.init_device) ENABLED START #
        self.set_state(DevState.INIT)
        self._range = Range["1 nanowatt or nanojoule"]
        self._auto_range = False
        self._trigger_level = 0.0
        self._wave_corr = False
        self._wave_corr_value = 0.0
        self._meter_value = 0.0

        if self.ConnectType == "net":
            import socket
            self.pm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.pm.connect((self.HostName, self.PortNumber))
        elif self.ConnectType == "serial":
            import serial
            self.pm = serial.Serial(port=self.SerialPort,
                                    baudrate=self.Baudrate,
                                    bytesize=8,
                                    stopbits=1,
                                    timeout=0.1)
            

        self.write("*VER")
        self.debug_stream(self.read())
        self.write('*PWC00800')
        self.set_state(DevState.ON)
        # PROTECTED REGION END #    //  GentecEOMaestro.init_devicey

    def write(self, cmd):
        if self.ConnectType == "net":
            self.pm.send(cmd.encode())
        else:
            self.pm.write(cmd.encode())

    def read(self):
        if self.ConnectType == "net":
            return self.pm.recv(1024)
        else:
            return self.pm.readline()

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
        try:
            self.pm.close()
        except:
            pass
        # PROTECTED REGION END #    //  GentecEOMaestro.delete_device
    # ------------------
    # Attributes methods
    # ------------------

    def read_range(self):
        # PROTECTED REGION ID(GentecEOMaestro.range_read) ENABLED START #
        """Return the range attribute."""
        self.debug_stream('in RANGE')
        a = self.send_query('*GCR')
        self.debug_stream(a)
        self._range = Range(int(a))
        self.debug_stream(str(self._range))
        return self._range
        # PROTECTED REGION END #    //  GentecEOMaestro.range_read

    def write_range(self, value):
        # PROTECTED REGION ID(GentecEOMaestro.range_write) ENABLED START #
        """Set the range attribute."""
        temp = str(value)
        if int(value) < 10:
            temp += '0'
        self.write('*SCS'+temp)
        # PROTECTED REGION END #    //  GentecEOMaestro.range_write

    def read_auto_range(self):
        # PROTECTED REGION ID(GentecEOMaestro.auto_range_read) ENABLED START #
        """Return the auto_range attribute."""
        return bool(int(self.send_query('*GAS')))
        # PROTECTED REGION END #    //  GentecEOMaestro.auto_range_read

    def write_auto_range(self, value):
        # PROTECTED REGION ID(GentecEOMaestro.auto_range_write) ENABLED START #
        self.write('*SAS'+str(int(value)))
        # PROTECTED REGION END #    //  GentecEOMaestro.auto_range_write

    def read_trigger_level(self):
        # PROTECTED REGION ID(GentecEOMaestro.trigger_level_read) ENABLED START #
        """Return the trigger_level attribute."""
        return float(self.send_query('*GTL'))
        # PROTECTED REGION END #    //  GentecEOMaestro.trigger_level_read

    def write_trigger_level(self, value):
        # PROTECTED REGION ID(GentecEOMaestro.trigger_level_write) ENABLED START #
        """Set the trigger_level attribute."""
        self.write('*STL'+str(value).encode())
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
            self.write('*PWC00000')
        self._wave_corr = value
        # PROTECTED REGION END #    //  GentecEOMaestro.wave_corr_write

    def read_wave_corr_value(self):
        # PROTECTED REGION ID(GentecEOMaestro.wave_corr_value_read) ENABLED START #
        """Return the wave_corr_value attribute."""
        return int(self.send_query('*GWL'))
        # PROTECTED REGION END #    //  GentecEOMaestro.wave_corr_value_read

    def write_wave_corr_value(self, value):
        # PROTECTED REGION ID(GentecEOMaestro.wave_corr_value_write) ENABLED START #
        """Set the wave_corr_value attribute."""
        self.write('*PWC{:05d}'.format(int(value)))
        # PROTECTED REGION END #    //  GentecEOMaestro.wave_corr_value_write

    def read_meter_value(self):
        # PROTECTED REGION ID(GentecEOMaestro.meter_value_read) ENABLED START #
        """Return the meter_value attribute."""
        # mode = self.send_query('*GMD')
        # change_prop = self.meter_value.get_properties()
        # if unit_lib[mode] != change_prop.unit:
        #     change_prop.unit = unit_lib[mode]
        #     self.meter_value.set_properties(change_prop)
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
