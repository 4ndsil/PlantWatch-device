# PlantWatch-device
This is the repository containing the code which is to be ran on a raspberry pi in a PlantWatch system.

## Structure

The project consists of 3 python modules:

`db.py` - database module for connecting and communicating with the database

`insights.py` - performs the processing of sensor values to generate reports to the end user

`publisher.py` - reads sensor values, contextualizes tha sensor data and publishes it to the MQTT broker in an infinite loop

## Setup
Connect to the raspberry using your preferred method

Update the raspberry pi
```
sudo apt-get update
sudo apt-get upgrade
```
Clone the repository into the home folder of the pi user

`git clone git@github.com:lucasvil/PlantWatch-device.git`

### Setup the sensors and python libraries
Enable I2C

`sudo apt-get install -y python-smbus i2c-tools`

Check and upgrade setuptools

`sudo pip3 install --upgrade setuptools`

Install the raspberry pi GPIO library

`pip3 install RPI.GPIO`

Install adafruit_blink

`pip3 install adafruit-blinka`

Install the circuitpython libraries for the lux sensor (TSL2591) and the capacitative soil moisture sensor (seesaw)

```
pip3 install adafruit-circuitpython-seesaw
pip3 install adafruit-circuitpython-tsl2591
```

Install the paho-mqtt library

`pip3 install paho-mqtt`

Install the pymongo library

`pip3 install pymongo`

Reboot the raspberry pi

`sudo reboot`

### Configure the MQTT broker
Install the mosquitto broker

`sudo apt install mosquitto`

Make sure it was installed correctly by checking the status of the broker service

`sudo systemctl status mosquitto.service`

Open the mosquitto configuration using nano

`nano /etc/mosquitto/mosquitto.conf`

The broker needs to listen on two ports, one for MQTT and one for WebSockets (the client communicates using MQTT over WebSockets). Edit the configuration file to the following:

`TODO`

### Environment variables
In order to run the application there is a need for two environment variable. Open the environment file using nano

`nano /etc/environment`

Add a line for the device ID (same as the one stored in the database in the device collection)

`DEVICE_ID=<deivceID>`

Also add a line for the mongoDB atlas connection string

`CONN_STRING=<mongoDB connection string>`

## Running the application
To run the application run the `publisher.py` script

`python3 publisher.py`

### Add a system.d service (optional)
If you want the `publisher.py` script to run automatically on startup you can add a it as a system.d service. To do this create and open a new unit file as shown below

`sudo nano /lib/systemd/system/publisher.service`

Add the following configuration to the unit file

`[Unit]
Description=Publisher
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/home/pi/
User=pi
Environment=DEVICE_ID="raspberry1"
Type=simple
ExecStart=/usr/bin/python3 /home/pi/PlantWatch-device/publisher.py

[Install]
WantedBy=multi-user.target
`

Reload the deamons and enable the publisher service

```
sudo systemctl deamon-reload
sudo systemctl enable publisher.service
```

Reboot the device and the publisher service should be running

`sudo reboot`
