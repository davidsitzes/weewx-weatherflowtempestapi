# weewx-weatherflowtempestapi

## Right now only python3 is supported

Installation instructions:

1) Install dependencies
```
pip3 install websocket-client
```

2) download the driver:
```
wget -O weewx-weatherflowtempestapi.zip https://github.com/davidsitzes/weewx-weatherflowtempestapi/archive/main.zip
```

3) install the driver:
```
wee_extension --install weewx-weatherflowtempestapi.zip
```

4) Reconfigure:
```
wee_config --reconfigure
```

5) Add your `access_token` and `station_device_id` to the `WeatherFlowTempestAPI` config section

5) Restart weewx
