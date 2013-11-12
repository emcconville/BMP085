"""
  This file is part of "Notes from barometric pressure sensor".

  "Notes from barometric pressure sensor" is free software: you
  can redistribute it and/or modify it under the terms of the
  GNU General Public License as published by the Free Software
  Foundation, either version 3 of the License, or
  (at your option) any later version.

  "Notes from barometric pressure sensor" is distributed in the
  hope that it will be useful, but WITHOUT ANY WARRANTY; without
  even the implied warranty of MERCHANTABILITY or FITNESS FOR A
  PARTICULAR PURPOSE.  See the GNU General Public License for
  more details.

  You should have received a copy of the GNU General Public License
  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
"""
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
    device = BMP085.Device(int(self.bus),port=int(self.device),oversampling=int(self.sampling))
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
  def record_sql(self):
    insert_query = """
    INSERT INTO recordings (temperature,pressure,altitude,timestamp)
    VALUES ({temperature},{pressure},{altitude},{timestamp})
    """.format(**(self.data_dict()))
  def data_dict(self):
    data = dict()
    data["temperature"] = self.temperature
    data["pressure"]    = self.pressure
    data["altitude"]    = self.altitude
    data["timestamp"]   = int(time.time())
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

