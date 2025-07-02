from hardware import EPOS  # Required for EPOS sensor

# --------------------------------------------------------------------------------------------------------------------
# General purpose variables
# --------------------------------------------------------------------------------------------------------------------
# Motion related variables:
targetPos = 40  # Desired target position in mm
absoluteMotion = False # True/False. Set to False if you want to move relative to the current position 

# EPOS variables:
baudRate_epos = 115200  # 1000000  # EPOS baud rate (unit of signaling speed)
timeout_epos = 500  # EPOS timeout

# --------------------------------------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------------------------------------
# Epos variables:
NODE_ID = 2

# Epos setup specs:
SCREW_LEAD = 2  # leadscrew lead; lead = linear travel per 1 screw rev
GEAR_HEAD = 29  # motor gearhead; gear ratio
COUNTS_PER_TURN = 256  # encoder counts per turn

# EPOS quadcounts (QCs):
# From 'Section 3.3: System Units' on EPOS2 Firmware Specification guide (Edition 2017)
QC = 4 * COUNTS_PER_TURN

# --------------------------------------------------------------------------------------------------------------------
# Main function
# --------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Calculate motor displacement:
    # Our setup uses a single lead leadscrew, with a 2 mm lead (SCREW_LEAD); lead = linear travel per 1 screw rev
    # The motor gearhead has a reduction of 29:1 (GEAR_HEAD)
    # Finally, the encoder used is a 3 channel encoder with 256 counts per turn (COUNTS_PER_TURN)
    # Therefore, using a displacement (disp), the target position is given by:
    #           target_pos = (disp*QC*GEAR_HEAD)/SCREW_LEAD

    targetPos = int((targetPos * QC * GEAR_HEAD) / SCREW_LEAD)

    # Create new EPOS instance:
    motor1 = EPOS("EPOS2", "MAXON SERIAL V2", "USB", "USB0")

    # Open communication with EPOS device
    motor1.ConnectDevice(NODE_ID, baudRate_epos, timeout_epos)

    # Activate EPOS Profile Position Mode
    motor1.ActivatePPM()

    # If the ESP32 is ready start motion
    motor1.MoveToPositionSpeed(targetPos, 2000, 100000, 100000, absoluteMotion, False)

    motor1.WaitForTargetReached()

    motor1.DoHoming()

    print("Done. Final position is: %s" % motor1.GetPositionIs())

    motor1.DisableDevice()
    motor1.CloseDevice()
