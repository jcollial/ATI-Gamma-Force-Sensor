
# ATI Gamma Force Sensor

This repo provides a simple example to controll an EPOS motor driver and collect data from an ATI Gamma force sensor using a NI DAQ device.

## Requirements
- Some of tha main files may interact with an EPOS motor driver using an USB connection. Please download the EPOS USB Driver from https://www.maxongroup.com/maxon/view/product/control/Positionierung/390438. The driver is located under Downloads -> Software/Firmware -> EPOS USB Driver Installation
- The nidaqmx python library is used to interact with a National Instruments DAQ device. Running nidaqmx requires NI-DAQmx to be installed. Please download from https://www.ni.com/en/support/downloads/drivers/download.ni-daq-mx.html#565026 or from https://www.ni.com/en/support/downloads.html. None of the recommended Additional items are required for nidaqmx to function, and they can be removed to minimize installation size. It is recommended you continue to install the NI Certificates package to allow your Operating System to trust NI built binaries, improving your software and hardware installation experience. More information about the nidaqmx requirements as well as other installation options can be found in https://nidaqmx-python.readthedocs.io/en/latest/index.html

## Main files description

- `EPOS_Force_Datalogger`: Program used to control an EPOS motor driver and collect data from the ATI force sensor
- `single_motor_control_example`: Example code to control the motion of the Maxon motor. ATI force sensor data will not be collected in this example

## Installation

```shell
# Clone the repository in a directory of your choice
git clone https://github.com/jcollial/ATI-Gamma-Force-Sensor.git

# Navigate into the directory that contains the repository files
cd ATI-Gamma-Force-Sensor

# Create a python virtual environment within the project directory (change my-venv for the name of your virtual environment)
python -m venv venv

```

### Activate the virtual environment
Use the appropriate command based on your terminal or operation system:
- Windows Command Prompt
```shell
venv\Scripts\activate

```
- Windows PowerShell
```shell
.\venv\Scripts\Activate.ps1

```

### Install dependencies
```shell
python -m pip install -r requirements.txt

```

### To deactivate the virtual environment, type the following in the terminal window
```shell
deactivate

```
