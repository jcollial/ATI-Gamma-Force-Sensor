
# ATI Gamma Force Sensor

This repo provides a simple example to interact with the ATI Gamma force sensor.

## Requirements
- Some of tha main files may interact with an EPOS motor driver. Please download the drivers from https://www.maxongroup.com/maxon/view/product/control/Positionierung/390438. The driver is located under Downloads -> Software/Firmware -> EPOS USB Driver Installation
- To interact with a National Instruments DAQ, you will need the NI-DAQmx drivers. Please download from https://www.ni.com/en/support/downloads/drivers/download.ni-daq-mx.html#565026 

## Main files description

- EPOS_Force_Datalogger: Program used to control an EPOS motor driver and collect data from the ATI force sensor
- single_motor_control_example: Example code to control the motion of the Maxon motor. ATI force sensor data will not be collected in this example

## Installation

```shell
# Clone the repository in a directory of your choice
git clone https://github.com/jcollial/ATI-Gamma-Force-Sensor.git

# Navigate into the directory that contains the repository files
cd ATI-Gamma-Force-Sensor

# Create a python virtual environment within the project directory (change my-venv for the name of your virtual environment)
python -m venv venv

# Activate the virtual environment
# If using Windows cmd
venv\Scripts\activate
# If using PowerShell
.\venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r requirements.txt

# To deactivate the virtual environment, type the following in the terminal window
deactivate
