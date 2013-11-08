from smbus import SMBus
from time import sleep

class BMP085(object):
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
  oversampling_setting = 0x00
  bus = None
  def __init__(self,bus,**kwargs):
    self.bus = SMBus(bus)
    if "port" in kwargs:
      self.address = kwargs["port"]
    self.__calibration__()
  def readInt(self,address):
    self.bus.write_byte(self.port,address)
    msb = self.bus.read_byte(self.port)
    lsb = self.bus.read_byte(self.port)
    return int( msb<<8 | lsb )
  def read(self,address):
    self.bus.write_byte(self.port,address)
    return self.bus.read_byte(self.port)
  def getDeviceTemperature(self):
    self.bus.write_byte_data(self.port,0xFE,0x2E)
    sleep(0.005) # Wait for it
    return self.readInt(0xF6)
  def getDevicePressure(self):
    self.bus.write_byte_data(self.port,0xF4,0x34+(self.oversampling_setting<<6))
    sleep(float(0x02+(0x03<<self.oversampling_setting))/1000)
    self.bus.write_byte(self.port,0xF6)
    msb = self.bus.read_byte(self.port)
    lsb = self.bus.read_byte(self.port)
    xlsb = self.bus.read_byte(self.port)
    return (msb << 16 | lsb << 8 | xlsb) >> (8-self.oversampling_setting)
  def calculateTemperature(self,deviceTemperature):
    x1      = (((deviceTemperature - self.AC6) * self.AC5) >> 0x0F)
    self.B5 = x1 + ((self.MC << 0x0B)/(x1 + self.MD))
    return (self.B5 + 0x08) >> 0x04
  def calculatePressure(self,devicePressure):
    self.B6 = self.B5 - 0x0FA0
    temp = (self.B2 * (self.B6 * self.B6) >> 0x0C) >> 0x0B \
         + (self.AC2 * self.B6) >> 0x0B
    self.B3 = ((self.AC1 * 4 + temp) << self.oversampling_setting) + 2 >> 0x02
    x1 = (self.AC3 * self.B6) >> 0x0D
    x2 = (self.B1 * ((self.B6 * self.B6) >> 0x0C)) >> 0x10
    x3 = ((x1 + x2) + 2) >> 0x02
    self.B4 = (self.AC4 * (x3 + 0x8000)) >> 0x0F
    self.B7 = ((devicePressure - self.B3) * (0xC350 >> self.oversampling_setting))
    if self.B7 < 0x80000000 :
      p = (self.B7 << 1) / self.B4
    else :
      p = (self.B7 / self.B4) << 1;
    x1 = ((p >> 8) * (p >> 8) * 3038) >> 0x10
    x2 = (-7357 * p) >> 0x10;
    return p + (x1 + x2 + 3791) >> 0x04
    
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


if __name__ == '__main__':
  device = BMP085(1)
  print "Temp: ", float(device.calculateTemperature(device.getDeviceTemperature()) * 0.01)
  print "Pres: ", device.calculatePressure(device.getDevicePressure())
