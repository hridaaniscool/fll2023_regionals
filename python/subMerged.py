from hub import port
from hub import motion_sensor
import motor
import runloop
import motor_pair
import asyncio

# left motor is connected to port A and right motor is connected to port B

class Direction:
    LEFT = -1
    BACKWARD = -1
    FORWARD = 1
    RIGHT = 1
    UP = 1
    DOWN = -1

def get_drift(tgt_yaw):
    c_yaw = get_yaw()
    if tgt_yaw > 270 and c_yaw < 90:
        drift = 360 - tgt_yaw + c_yaw
    else:
        drift = c_yaw - tgt_yaw

    return drift

"""
Gives current yaw in between 0 to 359
As our Motor Left is connected to A and Right is Connected to B
When turning right we get negative Yaw values
"""
def get_yaw() -> int:
    yaw = motion_sensor.tilt_angles()[0]
    yaw = (round(yaw/10 * -1) + 360) % 360# Get Remainder, Yaw angle after one full circle.
    return yaw

"""
Give the angle difference between current yaw and target yaw
There are 4 Cases Here:
    1. When turnnig Right and When current yaw is 350 and Target yaw is 30 
    2. When turning Left and When current yaw is 10 and Target yaw is 350
    3. When turning Right and When target yaw is 90 and current yaw is 30
    4. When turning Left and When target yaw is 270 and current yaw is 350
"""
def angleDiff(tgt_yaw):
    cur_yaw = get_yaw()
    # right turn for robot and crossing 360 degree boundry
    if tgt_yaw < 90 and cur_yaw > 270:
        return 360 - cur_yaw + tgt_yaw
    # left turn for robot and crossing 360 degree boundry
    elif cur_yaw < 90 and tgt_yaw > 270:
        return 360 - tgt_yaw + cur_yaw
    elif tgt_yaw > cur_yaw:
        return tgt_yaw - cur_yaw
    
    return cur_yaw - tgt_yaw


async def straight(speed, distance, f_b):
    global g_yaw
    tgtYaw = g_yaw
    # Pair motors on port A and port B
    #resets the relative position of one of the wheels
    motor.reset_relative_position(port.B, 0)
    drift = get_drift(tgtYaw)

    while distance > abs(motor.relative_position(port.B)):
        #sets the return value of the tuple to a tuple, so we can pull a specific value from it
        drift = get_drift(tgtYaw)
        motor_pair.move(motor_pair.PAIR_1, drift * -1, velocity = speed * f_b, acceleration = 500)
    
    #stops the motors after they are out of the while loop
    motor_pair.stop(motor_pair.PAIR_1)

    await runloop.sleep_ms(100)



"""
direction is Direction.RIGHT or Direction.LEFT
degrees: Amount of degrees to turn
speed: speed at which to turn
"""
async def turn(direction, degrees, speed):
    global g_yaw
    tgtYaw = g_yaw

    if direction == Direction.RIGHT:
        while angleDiff(tgtYaw) > 0:
            tgtYaw = (g_yaw + degrees) % 360
            motor.run(port.A, speed * Direction.RIGHT * -1)  # We need to turn both wheels backwards to turn Right
            motor.run(port.B, speed * Direction.RIGHT * -1)
    elif direction == Direction.LEFT:
        tgtYaw = (g_yaw - degrees + 360) % 360
        while angleDiff(tgtYaw) > 0:  #Angle diff gives us the difference between my current yaw and the target yaw
            motor.run(port.A, speed)
            motor.run(port.B, speed)

    motor_pair.stop(motor_pair.PAIR_1, stop = motor.SMART_BRAKE)
    g_yaw = tgtYaw  # Save the target yaw into our Global yaw.
    await runloop.sleep_ms(100)

async def main():
    global g_yaw
    g_yaw = 0
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)
    await straight(300, 500, 1)
    await turn(Direction.LEFT, 380,100)
    await turn(Direction.RIGHT, 390,100)
    """
    await straight(300, 500, 1)
    await turn(Direction.LEFT, 20,100)
    await straight(300, 500, 1)
    await turn(Direction.LEFT, 350,100)
    await straight(300, 500, 1)
   
    await turn(Direction.RIGHT, 350, 100)
    await straight(300, 500, 1)
    await turn(Direction.RIGHT, 20, 100)
"""

    print(get_yaw())

# This is the starting point
runloop.run(main())
