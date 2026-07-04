# Project Report Summary

## Title

**EE3638 Remote DHT11 Environmental Monitoring System**

## Context

This project was completed for the EE3638 Design for IoT module. The aim was to design and demonstrate a remotely accessible IoT device using a Raspberry Pi, a digital sensor, network communication, software processing, and a user-facing interface.

The final implementation is a Raspberry Pi 4 environmental monitoring system using a DHT11 temperature/humidity sensor, Flask web server, CSV logging, Chart.js visualisation, GPIO LED control, and systemd service deployment.

## Objectives

The project objectives were to:

- read real-world temperature and humidity from a digital DHT11 sensor;
- log readings with timestamps for later inspection;
- display live and historical readings through a web dashboard;
- make the dashboard accessible from a mobile device over a wireless/mobile network;
- include an additional actuator feature using an LED;
- improve demonstration reliability using structured logging and automatic service startup.

## Hardware design

The hardware platform was a Raspberry Pi 4 running Linux. A DHT11 sensor was connected to BCM GPIO4 for digital temperature/humidity acquisition. The sensor used 3.3V power and a common ground. An LED actuator was connected to BCM GPIO17 through a 330 ohm resistor to demonstrate two-way IoT interaction.

| Component | Connection | Purpose |
|---|---|---|
| DHT11 signal | GPIO4 / physical pin 7 | Digital sensor input |
| DHT11 VCC | 3.3V / physical pin 1 | Sensor power |
| DHT11 GND | Ground / physical pin 6 | Common ground |
| LED | GPIO17 / physical pin 11 | Remote actuator output |
| Resistor | 330 ohm in series with LED | Current limiting |

## Network design

The Raspberry Pi hosted a Flask server on port 5000. For demonstration reliability, the Raspberry Pi and mobile device were connected to the same smartphone hotspot/local network. The phone could then access the dashboard at:

```text
http://<raspberry-pi-ip>:5000/
```

This avoided unreliable campus network behaviour and provided a repeatable demonstration path.

## Software architecture

The software was split into two processes:

1. `data_logger.py` - owns the DHT11 sensor, retries failed reads, and writes valid readings to daily CSV files.
2. `web_server.py` - reads the CSV output and serves API/dashboard responses.

This split prevents multiple processes from reading the DHT11 at the same time, avoiding message queue and timing contention problems.

## Key modules

| File | Responsibility |
|---|---|
| `src/config.py` | GPIO pins, timing intervals, data/log paths, history limit |
| `src/dht_reader.py` | DHT11 acquisition and retry handling |
| `src/data_logger.py` | Timestamped CSV data logging loop |
| `src/web_server.py` | Flask dashboard and REST API |
| `src/gpio_control.py` | LED setup, output control, and cleanup |
| `web/static/app.js` | Browser-side polling, table updates, Chart.js updates, LED controls |
| `web/templates/dashboard.html` | Dashboard layout |
| `systemd/*.service` | Automatic startup configuration |

## API design

| Route | Function |
|---|---|
| `GET /api/latest` | Returns latest logged reading |
| `GET /api/history` | Returns recent logged readings for table/chart display |
| `GET /api/led` | Returns current LED state |
| `POST /api/led` | Sets LED state |

## Testing and evaluation

The project was tested in stages:

1. Manual DHT11 sensor reads from the terminal.
2. CSV logging at approximately five-second intervals.
3. Flask API responses through `/api/latest` and `/api/history`.
4. Dashboard rendering in Firefox on the Raspberry Pi.
5. Remote dashboard access from a mobile phone on the same hotspot.
6. LED toggle through the dashboard button and `/api/led` route.
7. systemd service startup after reboot.

The final system successfully demonstrated sensor acquisition, data logging, API access, visualisation, remote monitoring, actuator control, and Linux service deployment.

## Main engineering decisions

- **Separate logger and web services:** prevents DHT11 driver contention and keeps the web app responsive.
- **CSV storage:** simple, inspectable, and suitable for a coursework-scale prototype.
- **Five-second sampling interval:** responsive enough for a live dashboard while avoiding over-polling the DHT11.
- **Retry handling:** reduces failure caused by transient DHT checksum/timing errors.
- **systemd deployment:** improves reliability during demonstrations and after reboots.

## Limitations

- DHT11 accuracy and sampling performance are limited compared with better sensors.
- CSV files are not ideal for long-term scaling or multi-sensor queries.
- The dashboard uses HTTP and has no authentication.
- The mobile access method is local-network based rather than public-cloud based.

## Future work

- Replace the DHT11 with a BME280 or SHT sensor.
- Move storage from CSV to SQLite or a time-series database.
- Add HTTPS and authentication.
- Add alert thresholds for environmental changes.
- Add automated tests for API formatting and CSV parsing.
- Package a simulation mode for non-Raspberry Pi development.

## Conclusion

The project successfully integrates hardware, embedded Linux, Python, Flask, CSV persistence, REST APIs, web visualisation, GPIO actuation, and systemd service management into a working IoT prototype. It demonstrates practical end-to-end engineering skills across sensing, processing, networking, visualisation, and control.
