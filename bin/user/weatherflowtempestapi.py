import websocket
import json
import weewx.drivers
import time
import queue

try:
    import thread
except ImportError:
    import _thread as thread

DRIVER_NAME = 'WeatherFlowTempestAPI'
DRIVER_VERSION = "0.1"


def loader(config_dict, engine):
    station = WeatherFlowTempestAPI(**config_dict[DRIVER_NAME])
    return station


class WeatherFlowTempestAPI(weewx.drivers.AbstractDevice):
    # From what I can tell, here are the weewx parameters that we get data for
    weewx_map = {
        'dateTime': 'timestamp',
        'outTemp': 'air_temp',
        'pressure': 'station_pressure',
        'windSpeed': 'wind_avg',
        'windDir': 'wind_dir',
        'windGust': 'wind_gust',
        'outHumidity': 'relative_humidity',
        'radiation': 'solar_radiation',
        'UV': 'uv',
        'rain': 'rain_accumulated',
        'consBatteryVoltage': 'battery',
    }

    def hardware_name(self):
        return DRIVER_NAME

    def __init__(self, **stn_dict):
        """Initialize the driver

        NAMED ARGUMENTS:

        access_token: The WeatherFlow Tempest API personal access token
        [Required.]

        app_id: The application name to use when speaking with the WeatherFlow APi
        [Optional. Default is weewx-driver]

        station_device_id: The device id for your Tempest station
        [Required.]
        """

        self.app_id = stn_dict.get('app_id', 'weewx-driver')
        self.access_token = stn_dict.get('access_token')
        self.station_device_id = stn_dict.get('station_device_id')
        self.obs_queue = queue.Queue()

        # websocket.enableTrace(True)

        def run(*args):
            ws = websocket.WebSocketApp(f'wss://ws.weatherflow.com/swd/data?token={self.access_token}',
                                        on_open=self.on_ws_open,
                                        on_message=self.on_ws_message,
                                        on_error=self.on_ws_error,
                                        on_close=self.on_ws_close)
            ws.run_forever()

        thread.start_new_thread(run, ())

    def genLoopPackets(self):
        while True:
            time.sleep(10)
            while not self.obs_queue.empty():
                observation = self.obs_queue.get()
                packet = {'usUnits': weewx.METRIC}
                for weewx_type, obs_type in self.weewx_map.items():
                    packet[weewx_type] = getattr(observation, obs_type)

                yield packet

    def on_ws_message(self, ws, message):
        summary = json.loads(message)

        if ('type' in summary and summary['type'] == 'obs_st'):
            observation = Observation(json.loads(message))
            self.obs_queue.put(observation)

    def on_ws_error(self, ws, error):
        print(error)

    def on_ws_close(self, ws):
        print("### closed ###")

    def on_ws_open(self, ws):
        def run(*args):
            startevent = {
                "type": "listen_start",
                "device_id": self.station_device_id,
                "id": self.app_id
            }
            ws.send(json.dumps(startevent))

        thread.start_new_thread(run, ())


class Observation:
    obs_ident = {
        0: "timestamp",
        1: "wind_lull",
        2: "wind_avg",
        3: "wind_gust",
        4: "wind_dir",
        5: "wind_sample_interval",
        6: "station_pressure",
        7: "air_temp",
        8: "relative_humidity",
        9: "illuminance",
        10: "uv",
        11: "solar_radiation",
        12: "rain_accumulated",
        13: "precip_type",
        14: "lightning_strike_distance",
        15: "lightning_strike_count",
        16: "battery",
        17: "report_interval",
        18: "local_daily_rain_accumulation",
        19: "rain_accumulated_final",
        20: "local_daily_rain_accumulation_final",
        21: "precip_analysis_type"
    }

    def __init__(self, summary: dict):

        # "summary": {
        #     "pressure_trend": "rising",
        #     "strike_count_1h": 0,
        #     "strike_count_3h": 0,
        #     "precip_total_1h": 0,
        #     "strike_last_dist": 32,
        #     "strike_last_epoch": 1618072562,
        #     "precip_accum_local_yesterday": 3.429037,
        #     "precip_accum_local_yesterday_final": 3.429037,
        #     "precip_analysis_type_yesterday": 1,
        #     "feels_like": 16,
        #     "heat_index": 16,
        #     "wind_chill": 16,
        #     "pulse_adj_ob_time": 1618249879,
        #     "pulse_adj_ob_wind_avg": 2.8,
        #     "pulse_adj_ob_temp": 16,
        #     "raining_minutes": [
        #         0,
        #         0,
        #         0,
        #         0,
        #         0,
        #         0,
        #         0,
        #         0,
        #         0,
        #         0,
        #         0,
        #         0
        #     ],
        #     "dew_point": 9.9,
        #     "wet_bulb_temperature": 12.5,
        #     "air_density": 1.21442,
        #     "delta_t": 3.5,
        #     "precip_minutes_local_day": 34,
        #     "precip_minutes_local_yesterday": 105
        # },

        for k, v in summary['summary'].items():
            setattr(self, k, v)

        # "obs": [
        #     [
        #         1618249939,
        #         1.03,
        #         2.48,
        #         4.2,
        #         13,
        #         3,
        #         1008,
        #         16,
        #         67,
        #         23049,
        #         1.03,
        #         192,
        #         0,
        #         0,
        #         0,
        #         0,
        #         2.6,
        #         1,
        #         0.500612,
        #         null,
        #         null,
        #         0
        #     ]
        # ],

        for k, v in enumerate(summary['obs'][0]):
            setattr(self, self.obs_ident[k], v)


def confeditor_loader():
    return WeatherFlowTempestAPIConfEditor()


class WeatherFlowTempestAPIConfEditor(weewx.drivers.AbstractConfEditor):
    @property
    def default_stanza(self):
        return """
[WeatherFlowTempestAPI]
    # This section is for the WeatherFlowTempestAPI driver
    access_token = f86e74dc-c7f2-47e9-a28b-2e6e922d0a54
    # The app name to use when accessing the API. This can be anything
    app_id = weewx-driver
    # The device id of your tempest station
    station_device_id = 12345
    # The driver to use:
    driver = user.weatherflowtempestapi
"""


if __name__ == "__main__":
    driver = WeatherFlowTempestAPI(access_token='PUT YOUR ACCESS TOKEN HERE', station_device_id='PUT YOUR STATION ID HERE')
    for packet in driver.genLoopPackets():
        print(packet["dateTime"])
        print(packet["outTemp"])
