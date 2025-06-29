"""EposCls.py:

This class library is used to send and receive commands from an EPOS driver.
This file requires the "EposCmd64.dll" library to be located on the same directory as this file
For more information about the methods used, refer to the EPOS Command Library which can be downloaded from:
    https://www.maxongroup.com/maxon/view/product/control/Positionierung/390438



Author:   Jose Guillermo Colli Alfaro
email:    jcollial@uwo.ca
Date:     March 22, 2022
Version:  1.0

"""

import ctypes
import pathlib


class EPOS:

    # --------------------------------------------------------------------------------------------------------------------
    # Declare "private" variables. Note: These are not really private variables as private variables don't exist in Python
    # --------------------------------------------------------------------------------------------------------------------
    # EPOS Command Library path
    _path = pathlib.Path(__file__).parent / "EposCmd64.dll"

    # Load library
    _epos = ctypes.CDLL(str(_path))

    # Global "private" variables
    _keyHandle = None  # Set to none as it is easier to manage, memorywise
    _nodeID = None
    _pPositionIs = ctypes.c_long()
    _pErrorCode = ctypes.c_uint()
    _pOpMode = ctypes.c_uint()
    _nbOfBytesRead = ctypes.c_uint()
    _nbOfBytesWritten = ctypes.c_uint()
    _pData = ctypes.c_long()
    _pTargetPosition = ctypes.c_long()

    # --------------------------------------------------------------------------------------------------------------------
    # Class constructor
    # --------------------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        deviceName="EPOS2",
        protocolStackName="MAXON SERIAL V2",
        interfaceName="USB",
        portName="USB0",
    ):
        # Use str.encode to convert string to bytes. Required as some VCS commands require bytes as inputs
        self.deviceName = str.encode(deviceName)
        self.protocolStackName = str.encode(protocolStackName)
        self.interfaceName = str.encode(interfaceName)
        self.portName = str.encode(portName)

    # --------------------------------------------------------------------------------------------------------------------
    # State machine functions
    # --------------------------------------------------------------------------------------------------------------------
    # Enable device
    def EnableDevice(self):
        self._epos.VCS_SetEnableState(self._keyHandle, self._nodeID, ctypes.byref(self._pErrorCode))

    # Clear error state
    def ClearFault(self):
        self._epos.VCS_ClearFault(self._keyHandle, self._nodeID, ctypes.byref(self._pErrorCode))

    # Disable device
    def DisableDevice(self):
        self._epos.VCS_SetDisableState(self._keyHandle, self._nodeID, ctypes.byref(self._pErrorCode))

    # --------------------------------------------------------------------------------------------------------------------
    # Initialization functions
    # --------------------------------------------------------------------------------------------------------------------
    # Open communication the device
    def ConnectDevice(self, nodeID, baudrate=1000000, timeout=500):
        self._nodeID = nodeID  # save it to global variable so that it can be used in other functions
        self._keyHandle = self._epos.VCS_OpenDevice(
            self.deviceName,
            self.protocolStackName,
            self.interfaceName,
            self.portName,
            ctypes.byref(self._pErrorCode),
        )

        if self._keyHandle == 0:
            print("\nError: could not establish communication with EPOS device\n")
            return self._pErrorCode.value

        # Set baudrate and timeout
        self._epos.VCS_SetProtocolStackSettings(self._keyHandle, baudrate, timeout, ctypes.byref(self._pErrorCode))
        # Clear all error states
        self.ClearFault()
        # Enable device
        self.EnableDevice()
        print("Device is connected and enabled")

    # Close communication with EPOS device
    def CloseDevice(self):
        self._epos.VCS_CloseDevice(self._keyHandle, ctypes.byref(self._pErrorCode))

    # --------------------------------------------------------------------------------------------------------------------
    # Configuration functions
    # --------------------------------------------------------------------------------------------------------------------
    # Read EPOS object
    def GetObject(self, objectIndex, objectSubIndex, nbOfBytesToRead):
        self._epos.VCS_GetObject(
            self._keyHandle,
            self._nodeID,
            objectIndex,
            objectSubIndex,
            ctypes.byref(self._pData),
            nbOfBytesToRead,
            ctypes.byref(self._nbOfBytesRead),
            ctypes.byref(self._pErrorCode),
        )
        return self._pData.value

    def SetObject(self, objectIndex, objectSubIndex, nbOfBytesToWrite, data):
        self._pData.value = data

        self._epos.VCS_SetObject(
            self._keyHandle,
            self._nodeID,
            objectIndex,
            objectSubIndex,
            ctypes.byref(self._pData),
            nbOfBytesToWrite,
            ctypes.byref(self._nbOfBytesWritten),
            ctypes.byref(self._pErrorCode),
        )

    # --------------------------------------------------------------------------------------------------------------------
    # Operation mode functions
    # --------------------------------------------------------------------------------------------------------------------
    # Get operation mode
    def GetOperationMode(self):
        self._epos.VCS_GetOperationMode(
            self._keyHandle,
            self._nodeID,
            ctypes.byref(self._pOpMode),
            ctypes.byref(self._pErrorCode),
        )
        return self._pOpMode.value

    # --------------------------------------------------------------------------------------------------------------------
    # Motion info functions
    # --------------------------------------------------------------------------------------------------------------------
    # Query motor position
    def GetPositionIs(self):
        self._epos.VCS_GetPositionIs(
            self._keyHandle,
            self._nodeID,
            ctypes.byref(self._pPositionIs),
            ctypes.byref(self._pErrorCode),
        )
        return self._pPositionIs.value  # motor steps

    # Get motor absolute actual position (GetPositionIs function calls the GetObject function in the background)
    def GetPosition(self):
        objectIndex = 0x6064
        objectSubIndex = 0x00
        nbOfBytesToRead = 0x04
        return self.GetObject(objectIndex, objectSubIndex, nbOfBytesToRead)

    # Wait for target position to be reached. Blocking function. The driver won't execute any other functions until this one is completed (similar to a delay)
    def WaitForTargetReached(self, timeout=60000):
        targetReached = self._epos.VCS_WaitForTargetReached(self._keyHandle, self._nodeID, timeout, ctypes.byref(self._pErrorCode))
        return targetReached

    # Wait for target position to be reached. Access EPOS2 driver object dictionary using the GetObject function defined above
    def IsTargetReached(self):
        objectIndex = 0x6041
        objectSubIndex = 0x00
        nbOfBytesToRead = 0x02
        statusWord = self.GetObject(objectIndex, objectSubIndex, nbOfBytesToRead)

        # statusWord bit10 = 0, target not reached
        # statusWord bit10 = 1, target reached
        return (statusWord & 0x0400) == 0x0400

    # --------------------------------------------------------------------------------------------------------------------
    # Profile Position Mode functions
    # --------------------------------------------------------------------------------------------------------------------
    # Set Profile Position Mode (PPM)
    def ActivatePPM(self):
        self._epos.VCS_ActivateProfilePositionMode(self._keyHandle, self._nodeID, ctypes.byref(self._pErrorCode))

    # Set target position
    def SetTargetPosition(self, targetPosition):
        objectIndex = 0x607A
        objectSubIndex = 0x00
        nbOfBytesToWrite = 0x04

        if self.GetOperationMode() != 1:
            print("\nError: EPOS not in Profile Position Mode\n")
            return

        self.SetObject(objectIndex, objectSubIndex, nbOfBytesToWrite, targetPosition)

    # Get target position
    def GetTargetPosition(self):
        self._epos.VCS_GetTargetPosition(
            self._keyHandle,
            self._nodeID,
            ctypes.byref(self._pTargetPosition),
            ctypes.byref(self._pErrorCode),
        )
        return self._pTargetPosition.value

    # Macro to move to target position at a specified speed
    def MoveToPositionSpeed(
        self,
        targetPosition,
        profVelocity=1000,
        profAcceleration=100000,
        profDeceleration=100000,
        absolute=True,
        immediately=True,
    ):
        if self.GetOperationMode() != 1:
            print("\nError: EPOS not in Profile Position Mode\n")
            return

        # Set PPM parameters
        self._epos.VCS_SetPositionProfile(
            self._keyHandle,
            self._nodeID,
            profVelocity,
            profAcceleration,
            profDeceleration,
            ctypes.byref(self._pErrorCode),
        )
        self._epos.VCS_MoveToPosition(
            self._keyHandle,
            self._nodeID,
            targetPosition,
            absolute,
            immediately,
            ctypes.byref(self._pErrorCode),
        )

    # Halt motor
    def HaltMotion(self):
        self._epos.VCS_HaltPositionMovement(self._keyHandle, self._nodeID, ctypes.byref(self._pErrorCode))

    # --------------------------------------------------------------------------------------------------------------------
    # Homing Mode functions
    # --------------------------------------------------------------------------------------------------------------------
    # Set Homing Mode (HM)
    def ActivateHM(self):
        self._epos.VCS_ActivateHomingMode(self._keyHandle, self._nodeID, ctypes.byref(self._pErrorCode))

    # Define current position as home position
    def HomeActualPosition(self):
        newHomePosition = self.GetPosition()
        self._epos.VCS_DefinePosition(self._keyHandle, self._nodeID, newHomePosition, ctypes.byref(self._pErrorCode))

    # Macro to do homing
    def DoHoming(self):
        self.ActivateHM()
        self.HomeActualPosition()


# --------------------------------------------------------------------------------------------------------------------
# Test example
# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    # Epos variables:
    nodeID = 2

    # Epos setup specs:
    lead = 2  # leadscrew lead
    gh = 29  # motor gearhead
    qc = 4  # EPOS quadrature constant
    cpt = 256  # encoder counts per turn

    # Desired displacement:
    disp = 10

    # Calculate motor displacement:
    # Our setup uses a single lead leadscrew, with a 2 mm lead (lead)
    # The motor gearhead has a reduction of 29:1 (gh)
    # Finally, the encoder used is a 4 qc 3 channel encoder with 256 counts per turn (cpt)
    # Therefore, the total displacement (disp) of 10 mm is given by:
    #           target_pos = (disp*qc*cpt*gh)/lead

    target_pos = (disp * qc * cpt * gh) / lead

    # Create new EPOS instance
    motor1 = EPOS("EPOS2", "MAXON SERIAL V2", "USB", "USB0")

    # Open communication with device
    motor1.ConnectDevice(nodeID, 1000000, 500)

    # Activate Profile Position Mode
    motor1.ActivatePPM()

    # Uncomment any of the following 3 lines to test a fixed target position
    # target_pos = 1484800 # 10 cm
    # target_pos = 742400 # 5 cm
    target_pos = 29696  # approx. 2 mm displacement
    old_mPos = motor1.GetPositionIs()  # Used to know previous position state
    init_mPos = old_mPos  # Required to know if the target displacement has been reached
    print(old_mPos)

    # Move motor
    if init_mPos == 0:
        # Cast target_pos to an int as the function cannot handle floats
        motor1.MoveToPositionSpeed(int(-target_pos), 1000, 100000, 100000, False, True)
    else:
        # Cast target_pos to an int as the function cannot handle floats
        motor1.MoveToPositionSpeed(0, 1000, 100000, 100000, True, True)

    target_reached = False
    while not target_reached:
        actual_mPos = motor1.GetPositionIs()
        if abs(actual_mPos - init_mPos) == target_pos:
            target_reached = True

        if abs(actual_mPos - old_mPos) >= 29696:
            old_mPos = actual_mPos
            print("Motor position is: %s" % actual_mPos)

    print("Done. Final position is: %s" % motor1.GetPositionIs)

    motor1.CloseDevice()
