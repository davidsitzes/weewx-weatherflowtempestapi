# weewx-weatherflowtempestapi

## Right now only python3 is supported

Installation instructions:

1) Install dependencies
```
sudo pip3 install websocket-client
```

2) download the driver:
```
sudo wget -O weewx-weatherflowtempestapi.zip https://github.com/davidsitzes/weewx-weatherflowtempestapi/archive/main.zip
```

3) install the driver:
```
sudo wee_extension --install weewx-weatherflowtempestapi.zip
```

4) Reconfigure:
```
sudo wee_config --reconfigure
```

5) Add your `access_token` and `station_device_id` to the `WeatherFlowTempestAPI` config section. This section should be below the [Station] config section and above the [StdRESTful] config section
```
[WeatherFlowTempestAPI]
    access_token = XXXXXX
    station_device_id = XXXXXX
    driver = user.weatherflowtempestapi
```
5) Restart weewx
sudo /etc/init.d/weewx/restart
