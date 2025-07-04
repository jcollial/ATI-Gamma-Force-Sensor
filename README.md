
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

# Create a python virtual environment within the project directory
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
## Additional information
Each ATI Force Sensor comes with a calibration matrix unique to each sensor. The calibration matrix is the transducer calibration matrix provided on the software zip folder from ATI. The ATI supplied six-by-six calibration matrix matches the sensor’s FTxxxxx serial number in either the ATI software or the customer software. This standard matrix when multiplied by the biased strain gage data being generated from the transducer provides the force and torque data that can be used for the application.

The `EPOS_Force_Datalogger.py` file included in this repository loads the calibration matrix from `ATI-Gamma-Force-Sensor/Calibration Files/FT21484_cal_mat.txt`. If you have other calibration matrix files, please include them in this directory and update the `EPOS_Force_Datalogger.py` file. 
