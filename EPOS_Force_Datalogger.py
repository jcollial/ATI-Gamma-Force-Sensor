# FOR EACH SENSOR CHANGE: STRETCH AMOUNT, FILE NAME, RESISTANCE SUBTRACTION
# D1 supply must always be at 20V. D2 can change but D1 can’t go past 20V

import pathlib
import sys
from enum import Enum
from time import perf_counter, sleep  # Always returns time as float

import nidaqmx
import nidaqmx.stream_readers
import numpy as np
import pandas as pd
from nidaqmx.constants import AcquisitionType, Edge, TerminalConfiguration

from hardware import EPOS  # Required for EPOS sensor


# --------------------------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------------------------
class DAQTerminalConfig(Enum):
    """This class enumerates the possible values for the DAQ TerminalConfiguration value as specified in the NiDAQmx API"""

    DEFAULT = 0
    DIFF = 1
    NRSE = 2
    PSEUDO_DIFF = 3
    RSE = 4


# --------------------------------------------------------------------------------------------------------------------
# General purpose variables
# --------------------------------------------------------------------------------------------------------------------
# Motion related variables:
###########################
# CHANGE TARGETPOS FOR EACH SENSOR!
###########################
targetPos = 55  # Desired target position in mm --> This value can be changed for different testing cases == the amplitude of the cycle = maximum distance the sensor will stretch over

motorSteps = 2  # in mm -> increments in displacement until we reach the desired target position

# these values can be changed, but should stay consistent for multiple rounds of testing
initPos = 0  # Desired initial position in mm
motorSpeed = 2000  # Motor speed in rpm

# EPOS variables:
baudRate_epos = 115200  # 1000000  # EPOS baud rate (unit of signaling speed)
timeout_epos = 500  # EPOS timeout

# DAQ parameters:
DAQ_SN = "01C27A73"  # This string must match the serial number of the DAQ device being used
DAQ_sample_rate = 1000  # Sample rate in Hz
DAQ_acquisition_duration = 1  # Duration of data acquisition in seconds
DAQ_task_name = "forceTask"  # Name of the task used by the DAQ device to collect data
DAQ_analog_channels = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]  # List of used DAQ analog channels
DAQ_terminal_config = DAQTerminalConfig.DIFF  # Terminal configuration for ai ports of DAQ. See the class 'DAQTerminalConfig' above for a list of possible values

ForceDataFileName = "Test4SP.csv"  # <- Change the name to whatever name you like

# --------------------------------------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------------------------------------
# forceSensor_calibration_matrix = np.array(
#     [
#         [-0.25125, -0.06105, 1.17338, -13.52482, -0.47675, 14.42734],
#         [-1.00959, 16.23421, 0.48377, -7.75925, 0.49090, -8.31992],
#         [25.07049, -0.43117, 25.14917, -0.09450, 25.11196, -0.27838],
#         [-0.01317, 0.19581, -0.72139, -0.09435, 0.72986, -0.10509],
#         [0.83684, -0.00962, -0.43756, 0.16328, -0.41280, -0.17187],
#         [0.02547, -0.43748, 0.03185, -0.41796, 0.02164, -0.44538],
#     ]
# )

# Epos variables:
NODE_ID = 2

# Epos setup specs:  # variables are specific to the motor being used
SCREW_LEAD = 2  # leadscrew lead; lead = linear travel per 1 screw rev
GEAR_HEAD = 29  # motor gearhead; gear ratio
COUNTS_PER_TURN = 256  # encoder counts per turn

# EPOS quadcounts (QCs):
# From 'Section 3.3: System Units' on EPOS2 Firmware Specification guide (Edition 2017)
QC = 4 * COUNTS_PER_TURN  # motor specific variable

MOTOR_MAX_SPEED = 8000  # Speed limit in rpm for the motor. Check motor specifications to find this value. WARNING: moving the motor at max speed can cause damage to the motor


# --------------------------------------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------------------------------------
def findDAQ_device(serial_number):
    """This function is used to obtain a DAQ device name by its serial number"""
    if not isinstance(serial_number, str):
        serial_number = str(serial_number)

    # Get the local DAQ system
    system = nidaqmx.system.System.local()

    # Get a list of all available DAQ devices
    daq_devices = system.devices

    # Search for the device with the specified serial number
    for device in daq_devices:
        # The serial_num property returns an int16 representation of the DAQ device serial number, which is given as an HEX number.
        # This is why we need to cast the input serial number of the function to an int16 number.
        if device.serial_num == int(serial_number, 16):
            return device.name

    # If no device with the given product number is found
    return None


def get_DAQ_Data(task_name, channels, sample_rate, nSamples, terminal_configuration):
    # Create a new array that uses the shared memory block. This array must match that of the original shared memory array
    data = np.ndarray((len(channels), nSamples), dtype=np.double)

    # Create a task for the DAQ device
    with nidaqmx.Task(task_name) as task:
        # Configure the task to use the specified channels. Use a differential terminal configuration as explained in the ATI/DAQ
        # manual (DOC#: 9620-05-DAQ)
        for channel in channels:
            task.ai_channels.add_ai_voltage_chan(channel, terminal_config=terminal_configuration)

        # Set timing configuration for the DAQ device
        task.timing.cfg_samp_clk_timing(sample_rate, source="", active_edge=Edge.RISING, sample_mode=AcquisitionType.FINITE, samps_per_chan=nSamples)

        # Create a reader for the task
        reader = nidaqmx.stream_readers.AnalogMultiChannelReader(task.in_stream)

        # print("DAQ Process: Done waiting for serial")
        reader.read_many_sample(data, nSamples, timeout=(nSamples / sample_rate) + 10)

        # Get the average data of each channel
        return np.mean(data, axis=1, keepdims=True)


def nans(shape, dtype=float):
    """Function used to fill a numpy empty array with NaN values. The issue with the function np.empty, is that it does not create an empty array, instead it just fills it with random numbers"""
    nanArray = np.empty(shape, dtype)
    nanArray.fill(np.nan)
    return nanArray


def getForceSensorBias(channels, terminal_configuration):
    task_name = "biasTask"
    sample_rate = 1000
    nSamples = int(sample_rate * 2)  # Collect data for two seconds

    bias_data = get_DAQ_Data(task_name, channels, sample_rate, nSamples, terminal_configuration)
    return bias_data


def get_user_choice(prompt):
    while True:
        user_input = input(prompt).lower()
        if user_input == "y" or user_input == "n":
            return user_input
        else:
            print("Please enter 'y' or 'n'.")


# --------------------------------------------------------------------------------------------------------------------
# Main function
# --------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Load force sensor calibration matrix
    cal_matrix = np.loadtxt(pathlib.Path(__file__).parent / "Calibration Files/FT21484_cal_mat.txt")

    # Find the DAQ device using the device serial number
    deviceName = findDAQ_device(DAQ_SN)

    if deviceName is None:
        raise ValueError("DAQ device not found.")

    # Format the list of DAQ_analog_channels so that it includes the device name
    DAQ_channels = [deviceName + "/ai" + str(ii) for ii in DAQ_analog_channels]

    # Configure DAQ terminals
    if DAQ_terminal_config == DAQTerminalConfig.DEFAULT:
        terminal_config = TerminalConfiguration.DEFAULT

    elif DAQ_terminal_config == DAQTerminalConfig.DIFF:
        # Specify the DAQ channels that can be configured as a differential input
        diff_channels = ["ai" + str(ii) for ii in list(range(0, 8)) + list(range(16, 24))]

        # Filter the user defined channels (DAQ_analog_channels) so that we only configure the channels defined in diff_channels
        DAQ_channels = [channel for channel in DAQ_channels if channel.split("/")[1] in diff_channels]

        terminal_config = TerminalConfiguration.DIFF

    elif DAQ_terminal_config == DAQTerminalConfig.NRSE:
        terminal_config = TerminalConfiguration.NRSE

    elif DAQ_terminal_config == DAQTerminalConfig.PSEUDO_DIFF:
        terminal_config = TerminalConfiguration.PSEUDO_DIFF

    elif DAQ_terminal_config == DAQTerminalConfig.RSE:
        terminal_config = TerminalConfiguration.RSE

    else:
        raise ValueError("Incorrect value for DAQ_terminal_config")

    # ------------------------------------------------------------------------------------------------------------------
    # Calculate motor displacement:
    # Our setup uses a single lead leadscrew, with a 2 mm lead (SCREW_LEAD); lead = linear travel per 1 screw rev
    # The motor gearhead has a reduction of 29:1 (GEAR_HEAD)
    # Finally, the encoder used is a 3 channel encoder with 256 counts per turn (COUNTS_PER_TURN)
    # Therefore, using a displacement (disp), the target position is given by:
    #           target_pos = (disp*QC*GEAR_HEAD)/SCREW_LEAD

    targetPos = int((targetPos * QC * GEAR_HEAD) / SCREW_LEAD)
    initPos = int((initPos * QC * GEAR_HEAD) / SCREW_LEAD)
    motorSteps = int((motorSteps * QC * GEAR_HEAD) / SCREW_LEAD)

    # Create new EPOS instance:
    motor1 = EPOS("EPOS2", "MAXON SERIAL V2", "USB", "USB0")

    # Open communication with EPOS device
    motor1.ConnectDevice(NODE_ID, baudRate_epos, timeout_epos)

    # Activate EPOS Profile Position Mode
    motor1.ActivatePPM()

    # Set motor initial position, perform homming if current position is not initPos
    currentPos = motor1.GetPositionIs()
    if currentPos != initPos:
        print("Moving motor to desired initial position, please wait until motor stops moving")
        motor1.MoveToPositionSpeed(initPos, min(motorSpeed, MOTOR_MAX_SPEED), 100000, 100000, True, True)
        motor1.WaitForTargetReached()
        sleep(1)

    # Due to mechanical issues, current position needs to be set to zero manually after performing the homming motion
    currentPos = initPos

    # Create an empty list to store the sensor and motor data
    posData = []

    # Improve list append times by avoiding dot chaining. We achieve this by assigning the append function to an object
    posDataAppend = posData.append

    # ------------------------------------------------------------------------------------------------------------------
    choice = get_user_choice("Getting Force Sensor bias vector, please remove any weight attached to the sensor. Do you want to continue? [y/n]: ")

    if choice == "y":
        print("Getting bias vector, please do not touch the force sensor.")
        biasVector = getForceSensorBias(DAQ_channels, terminal_config)
    else:
        print("You chose to not continue.")
        sys.exit(1)

    print("Sensor bias complete")

    # ------------------------------------------------------------------------------------------------------------------
    # Calculate DAQ number of samples to read
    num_samples = int(DAQ_sample_rate * DAQ_acquisition_duration)

    # Create a numpy array to store the force data. Preallocate memory based on the number of steps made
    steps = range(initPos + motorSteps, targetPos + motorSteps, motorSteps)
    forceData = np.zeros((6, len(steps)))

    choice = get_user_choice("Ready to start? Do you want to continue? [y/n]: ")

    if choice == "y":
        print("Getting bias vector, please do not touch the force sensor.")
        biasVector = getForceSensorBias(DAQ_channels, terminal_config)
    else:
        print("You chose to not continue.")
        sys.exit(1)

    print("Sensor bias complete")

    # ------------------------------------------------------------------------------------------------------------------

    print("Starting motion")
    sleep(1)
    print(f"Motor will move {len(steps)}")
    for index, step in enumerate(steps):
        print(f"Step: {index+1}")
        motor1.MoveToPositionSpeed(step, motorSpeed, 100000, 100000, True, False)

        motor1.WaitForTargetReached()

        # ------------------------------------------------------------------------------------------------------------------
        # Create a temporal numpy array to store the force data
        temp_forceData = get_DAQ_Data(DAQ_task_name, DAQ_channels, DAQ_sample_rate, num_samples, terminal_config)

        posDataAppend(motor1.GetPositionIs())
        forceData[:, index] = temp_forceData.flatten()

    posData[:] = [abs((int(x) * SCREW_LEAD) / (QC * GEAR_HEAD)) for x in posData]
    posData = np.array(posData)[None, :]

    transformedData = cal_matrix @ (forceData - biasVector)  # @ is part from numpy and is used for matrix multiplications

    totalSamples = np.arange(1, transformedData.shape[1] + 1).reshape(1, -1)

    print("Done. Final position is: %s" % motor1.GetPositionIs())
    currentPos = motor1.GetPositionIs()
    if currentPos != 0:
        print("Homing motor, please wait until motor stops moving")
        sleep(1)
        motor1.MoveToPositionSpeed(0, motorSpeed, 100000, 100000, True, True)
        motor1.WaitForTargetReached()

    motor1.DisableDevice()
    motor1.CloseDevice()

    # ------------------------------------------------------------------------------------------------------------------
    print(f"\nSaving data, please wait...")

    # Check if Force Data folder exists. If it does not, then create the folder to store data
    dataFolderNamePath = pathlib.Path(__file__).parent.joinpath("Force Data")
    if not dataFolderNamePath.is_dir():
        dataFolderNamePath.mkdir()

    transformedData = np.concatenate((totalSamples, transformedData, posData), axis=0)

    forceHeaders = {
        "A": ["Data Collection Duration (s):", "Force Sensor Sample rate (Hz):", None, "Sample No."],
        "B": [DAQ_acquisition_duration, DAQ_sample_rate, None, "Fx"],
        "C": [None, None, None, "Fy"],
        "D": [None, None, None, "Fz"],
        "E": [None, None, None, "Tx"],
        "F": [None, None, None, "Ty"],
        "G": [None, None, None, "Tz"],
        "H": [None, None, None, "Motor Pos (mm)"],
    }

    df_forceHeaders = pd.DataFrame(forceHeaders)

    # Transform force data into a dataframe
    df_forceBody = pd.DataFrame(transformedData.T, columns=["A", "B", "C", "D", "E", "F", "G", "H"])  # Columns names must match those of the headers dataframe

    df_forceData = pd.concat([df_forceHeaders, df_forceBody], ignore_index=True)

    # # Concatenate an empty row to df_forceData for formatting purposes
    # df_forceData = pd.concat([df_forceData, pd.DataFrame([None])], axis=1, ignore_index=True)

    df_forceData.to_csv(
        dataFolderNamePath.joinpath(ForceDataFileName),
        index=False,
        header=False,
    )

    print(f"\nDone saving data")
