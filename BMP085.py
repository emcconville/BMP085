from smbus import SMBus
from time import sleep

class Device(object):
  port = 0x77
  AC1 = 0x00
  AC2 = 0x00
  AC3 = 0x00
  AC4 = 0x00
  AC5 = 0x00
  AC6 = 0x00
  B1  = 0x00
  B2  = 0x00
  B3  = 0x00
  B4  = 0x00
  B5  = 0x00
  B6  = 0x00
  B7  = 0x00
  MB  = 0x00
  MC  = 0x00
  MD  = 0x00
  oversampling_setting = 0x01
  bus = None
  def __init__(self,bus,**kwargs):
    self.bus = SMBus(bus)
    if "port" in kwargs:
      self.address = kwargs["port"]
    self.__calibration__()
  def readByte(self,address):
    byte = self.bus.read_byte_data(self.port,address)
    if byte > 127:
      byte = byte - 256
    return byte
  def readUnsignedByte(self,address):
   return self.bus.read_byte_data(self.port,address)
  def readInt(self,address):
    msb = self.readByte(address)
    lsb = self.readUnsignedByte(address)
    return ( msb<<8 ) + lsb
  def readUnsignedInt(self,address):
    msb = self.bus.read_byte_data(self.port,address)
    lsb = self.bus.read_byte_data(self.port,address+1)
    return ( msb << 8 ) + lsb
  def read(self,address):
    self.bus.write_byte(self.port,address)
    return self.bus.read_byte(self.port)
  def getDeviceTemperature(self):
    self.bus.write_byte_data(self.port,0xF4,0x2E)
    sleep(0.005) # Wait for it
    return self.readUnsignedInt(0xF6)
  def getDevicePressure(self):
    self.bus.write_byte_data(self.port,0xF4,0x34 + ( self.oversampling_setting << 0x06))
    sleep(float(0x02+(0x03<<self.oversampling_setting))/1000)
    msb  = self.readUnsignedByte(0xF6)
    lsb  = self.readUnsignedByte(0xF7)
    xlsb = self.readUnsignedByte(0xF8)
    msb <<= 0x10
    lsb <<= 0x08
    return ( msb + lsb + xlsb ) >> ( 0x08 - self.oversampling_setting )
  def calculateTemperature(self,deviceTemperature=None):
    if deviceTemperature is None:
      deviceTemperature = getDeviceTemperature()
    x1      = (((deviceTemperature - self.AC6) * self.AC5) >> 0x0F)
    x2      = ((self.MC << 0x0B)/(x1 + self.MD))
    self.B5 = x1 + x2
    return ((self.B5 + 0x08) >> 0x04) / 10.0
  def calculatePressure(self,deviceTemperature=None,devicePressure=None):
    if deviceTemperature is None:
      deviceTemperature = getDeviceTemperature()
    if devicePressure is None:
      devicePressure = getDevicePressure()
    self.calculateTemperature(deviceTemperature)
    self.B6 = self.B5 - 0x0FA0
    x1 = (self.B2 * (self.B6 * self.B6) >> 0x0C) >> 0x0B
    x2 = (self.AC2 * self.B6) >> 0x0B
    x3 = x1 + x2
    self.B3 = (((self.AC1 * 4 + x3) << self.oversampling_setting) + 2) / 0x04
    
    x1 = (self.AC3 * self.B6) >> 0x0D
    x2 = (self.B1 * ((self.B6 * self.B6) >> 0x0C)) >> 0x10
    x3 = ((x1 + x2) + 2) >> 0x02
    self.B4 = (self.AC4 * (x3 + 0x8000)) >> 0x0F
    self.B7 = ((devicePressure - self.B3) * (0xC350 >> self.oversampling_setting))
    if self.B7 < 0x80000000 :
      p = (self.B7 * 0x02) / self.B4
    else :
      p = (self.B7 / self.B4) * 0x02
    x1 = (p >> 0x08) * (p >> 0x08)
    x1 = (x1 * 0x0BDE) >> 0x10
    x2 = (-0x1CBD * p) >> 0x10
    p  = p + (( x1 + x2 + 0x0ECF ) >> 0x04 )
    return p
  def calculateAltitude(self,deviceTemperature=None,devicePressure=None,basePressure=101325):
    pressure = self.calculatePressure(deviceTemperature,devicePressure)
    altitude = 44330.0 * (1.0 - pow(float(pressure) / float(basePressure), 0.190295))
    return altitude
  def __calibration__(self):
    self.AC1 = self.readInt(0xAA)
    self.AC2 = self.readInt(0xAC)
    self.AC3 = self.readInt(0xAE)
    self.AC4 = self.readUnsignedInt(0xB0)
    self.AC5 = self.readUnsignedInt(0xB2)
    self.AC6 = self.readUnsignedInt(0xB4)
    self.B1  = self.readInt(0xB6)
    self.B2  = self.readInt(0xB8)
    self.MB  = self.readInt(0xBA)
    self.MC  = self.readInt(0xBC)
    self.MD  = self.readInt(0xBE)
    return True


if __name__ == '__main__':
  device = Device(1)
  deviceTemperature = device.getDeviceTemperature()
  devicePressure    = device.getDevicePressure()
  print "Temperature : ", device.calculateTemperature(deviceTemperature)
  print "Pressure    : ", device.calculatePressure(deviceTemperature,devicePressure)
  print "Altitude    : ", device.calculateAltitude(deviceTemperature,devicePressure)
