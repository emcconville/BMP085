import sys
import time
import BMP085

class App(object):
  bus = 1
  device = 0x77
  format = "csv"
  output = "stdout"
  sampling = 0
  
  def execute(self):
    device = BMP085.Device(self.bus,port=self.device,oversampling=self.sampling)
    rawTemperature = device.getDeviceTemperature()
    rawPressure    = device.getDevicePressure()
    self.temperature = device.calculateTemperature(rawTemperature)
    self.pressure  = device.calculatePressure(rawTemperature,rawPressure)
    self.altitude  = device.calculateAltitude(rawTemperature,rawPressure)
    return self
  def record(self):
    if self.format is "csv" :
      self.record_csv()
    return self
  def record_csv(self):
    data_line = """{temperature},{pressure},{altitude},{timestamp}\n""".format(**(self.data_dict()))
    if self.output == "stdout":
      sys.stdout.write(data_line)
    else:
      with open(self.output,"a") as file_handle:
        file_handle.write(data_line)
        file_handle.close()
  def data_dict(self):
    data = dict()
    data["temperature"] = self.temperature
    data["pressure"]    = self.pressure
    data["altitude"]    = self.altitude
    data["timestamp"]   = time.time()
    return data
    
if __name__ == "__main__":
  app = App()
  for arg in sys.argv:
    if arg[:2] == "--":
      try:
        (key,value) = arg.split("=")
      except ValueError:
        sys.stderr.write("Invalide optn `%s'" % arg)
        exit()
      key = key.strip(" -_")
      value = value.strip()
      setattr(app,key,value)
  app.execute().record()

