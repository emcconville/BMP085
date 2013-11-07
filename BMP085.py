from smbus import SMBus
from time import sleep

class BMP085(SMBus):
  port = 0x77
  AC1 = 0x00
  AC2 = 0x00
  AC3 = 0x00
  AC4 = 0x00
  AC5 = 0x00
  AC6 = 0x00
  B1  = 0x00
  B2  = 0x00
  MB  = 0x00
  MC  = 0x00
  MD  = 0x00
  oversampling_setting = 0x00
  def __init__(self,bus,**kwargs):
    SMBus.__init__(self,bus)
    if "port" in kwargs:
      self.address = kwargs["port"]
    self.__calibration__()
  def readInt(self,address):
    self.write_byte(self.port,address)
    msb = self.read_byte(self.port)
    lsb = self.read_byte(self.port)
    return int( msb<<8 | lsb )
  def read(self,address):
    self.write_byte(self.port,address)
    return self.read_byte(self.port)
  def getDeviceTemperature(self):
    self.write_byte_data(self.port,0xFE,0x2E)
    sleep(0.005) # Wait for it
    return self.readInt(0xF6)
  def getDevicePressure(self):
    self.write_byte_data(self.port,0xF4,0x34+(self.oversampling_setting<<6))
    sleep(float(0x02+(0x03<<self.oversampling_setting))/1000)
    self.write_byte(self.port,0xF6)
    msb = self.read_byte(self.port)
    lsb = self.read_byte(self.port)
    xlsb = self.read_byte(self.port)
    return (msb << 16 | lsb << 8 | xlsb) >> (8-self.oversampling_setting)
  def __calibration__(self):
    self.AC1 = self.readInt(0xAA)
    self.AC2 = self.readInt(0xAC)
    self.AC3 = self.readInt(0xAE)
    self.AC4 = self.readInt(0xB0)
    self.AC5 = self.readInt(0xB2)
    self.AC6 = self.readInt(0xB4)
    self.B1  = self.readInt(0xB6)
    self.B2  = self.readInt(0xB8)
    self.MB  = self.readInt(0xBA)
    self.MC  = self.readInt(0xBC)
    self.MD  = self.readInt(0xBE)
    return True