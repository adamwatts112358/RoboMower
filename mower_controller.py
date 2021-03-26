from evdev import list_devices, InputDevice, categorize, ecodes
import RPi.GPIO as GPIO

# Setup gamepad
axis_max = 33000.0
gamepad = InputDevice(list_devices()[0])
print(gamepad)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
motorA_dir_pin = 17
motorA_pwm_pin = 18
motorB_dir_pin = 22
motorB_pwm_pin = 23
GPIO.setup(motorA_dir_pin, GPIO.OUT)
GPIO.setup(motorA_pwm_pin, GPIO.OUT)
GPIO.setup(motorB_dir_pin, GPIO.OUT)
GPIO.setup(motorB_pwm_pin, GPIO.OUT)
pwm_freq = 500
pwm_A = GPIO.PWM(motorA_pwm_pin, pwm_freq)
pwm_B = GPIO.PWM(motorB_pwm_pin, pwm_freq)
pwm_A.start(0)
pwm_B.start(0)

def stop():
    GPIO.output(motorA_dir_pin, GPIO.LOW)
    GPIO.output(motorA_pwm_pin, GPIO.LOW)
    GPIO.output(motorB_dir_pin, GPIO.LOW)
    GPIO.output(motorB_pwm_pin, GPIO.LOW)
    
def button(event):
    # B button
    if event.code == 305:
        if event.value == 1:
            print("Stop!")
            stop()
            
def driveMotor(pwm_pin, dir_pin, value):
    # Set the direction pin
    if value > 0.0:
        GPIO.output(dir_pin, GPIO.HIGH)
        direction = 'forward'
    elif value < 0.0:
        GPIO.output(dir_pin, GPIO.LOW)
        direction = 'backward'
        
    # Set the PWM speed
    speed = 100.0*(value/axis_max)
    pwn_pin.ChangeDutyCycle(speed)
    
    print('%s %s %f'%(pwn_pin, direction, speed))
    
# Main controller loop
for event in gamepad.read_loop():
    # Joystick
    if event.type == ecodes.EV_ABS:
        if event.code == ecodes.ABS_X: # Left stick Up/Down
            driveMotor(motorA_pwm_pin, motorA_dir_pin, event.value)
        elif event.code == ecodes.ABS_Y: # Right stick Up/Down
            driveMotor(motorB_pwm_pin, motorB_dir_pin, event.value)
    # Buttons
    elif event.type == ecodes.EV_KEY:
        button(event)