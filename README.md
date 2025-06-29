
# ATI Gamma Force Sensor

This repo provides a simple example to interact with the ATI Gamma force sensor.

## Requirements
- Some of tha main files may interact with an EPOS motor driver. Please download the drivers from https://www.maxongroup.com/maxon/view/product/control/Positionierung/390438. The driver is located under Downloads -> Software/Firmware -> EPOS USB Driver Installation

## Main files description

- EPOS_Force_Datalogger: Program used to control an EPOS motor driver and collect data from the ATI force sensor

## Installation

```shell
# Clone the repository
git clone https://github.com/jcollial/ATI-Gamma-Force-Sensor.git

# Navigate into the directory
cd ATI-Gamma-Force-Sensor

# Create a python virtual environment within the project directory (change my-venv for the name of your virtual environment)
python -m venv my-venv

# Activate the virtual environment
my-venv\Scripts\activate

# Install dependencies
python -m pip install -r requirements.txt

# To deactivate the virtual environment, type the following in the terminal window
deactivate