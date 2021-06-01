from PySide2 import QtCore
import requests
import time
from logzero import logger
from configurations import MainConfigurationLoader
from configurations import static_app_configurations



class TemperatureService(QtCore.QThread):
    new_temperature = QtCore.Signal(str, str)
    zip_code_error = QtCore.Signal()

    def __init__(self):
        super(TemperatureService, self).__init__()
        self.__last_time_measured = 0
        self.__measure_now = True

    def run(self):
        while not self.isInterruptionRequested():
            zip_code = MainConfigurationLoader.get_zip_code_value()
            if (time.time() - self.__last_time_measured) > static_app_configurations.MEASURE_TEMPERATURE_EVERY or self.__measure_now:
                try:
                    api_address = f'http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={static_app_configurations.TEMPERATURE_API_KEY}&units=imperial'
                    response = requests.get(api_address)
                    json_data = response.json()
                    if "main" in json_data:
                        display_weather = str(round(json_data['main']['temp'])) + '\xb0 F' + ' ' +\
                                          json_data['weather'][0]['main'] \
                                          + ' Low ' + str(round(json_data['main']['temp_min'])) + '\xb0 High ' \
                                          + str(round(json_data['main']['temp_max'])) + '\xb0'
                        weather_icon = json_data["weather"][0]["icon"]
                        self.new_temperature.emit(display_weather, weather_icon)
                        self.__measure_now = False
                    else:
                        self.zip_code_error.emit()
                        logger.error(f"error in getting info zip code {zip_code}")

                except Exception as e:
                    print(e)
                self.__last_time_measured = time.time()
            time.sleep(3)

    def update_now(self):
        self.__measure_now = True

    def close_service(self):
        self.requestInterruption()


