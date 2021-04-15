from evdev import list_devices, InputDevice, categorize, ecodes
import RPi.GPIO as GPIO

# To do:
## Add button control to increase/decrease PWM freq.

# Setup gamepad
zeroL = 0.0
zeroR = 0.0
axis_max = 33000.0
axis_tol = 10*330.0
gamepad = InputDevice(list_devices()[0])
print(gamepad)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
motorA_dir_pin = 24 # Green
motor_pwm_pin = 23 # Blue
motorB_dir_pin = 27 # Orange

GPIO.setup(motorA_dir_pin, GPIO.OUT)
GPIO.setup(motor_pwm_pin, GPIO.OUT)
GPIO.setup(motorB_dir_pin, GPIO.OUT)
pwm_freq = 500.0
pwm = GPIO.PWM(motor_pwm_pin, pwm_freq)
pwm.start(0)

def stop():
    pwm.ChangeDutyCycle(0.0)

def zero(event):
    global zeroL, zeroR
    if event.code == ecodes.ABS_Y:
        # Zero the left stick
        zeroL = event.value
    elif event.code == ecodes.ABS_RX:
        # Zero the right stick
        zeroR = event.value

def button(event):
    # B button
    if event.code == 305:
        if event.value == 1:
            print("Stop!")
            stop()
            zero(event)
            
def drive(pwm, dir_pinA, dir_pinB, value):
    # Set the direction pin
    if value <= 0.0:
        direction = 'forward'
        GPIO.output(dir_pinA, GPIO.HIGH)
	GPIO.output(dir_pinB, GPIO.HIGH)
    elif value > 0.0:
        direction = 'backward'
        GPIO.output(dir_pinA, GPIO.LOW)
	GPIO.output(dir_pinA, GPIO.LOW)

    # Set the PWM speed
    speed = float(100.0*(abs(value)/axis_max))
    pwm.ChangeDutyCycle(speed)
    print('%s %f'%(direction, speed))
    
def turn(pwm, dir_pinA, dir_pinB, value):
    # Set the direction pin
    if value <= 0.0:
        direction = 'left'
        GPIO.output(dir_pinA, GPIO.HIGH)
	GPIO.output(dir_pinB, GPIO.LOW)
    elif value > 0.0:
        direction = 'right'
        GPIO.output(dir_pinA, GPIO.LOW)
	GPIO.output(dir_pinA, GPIO.HIGH)

    # Set the PWM speed
    speed = float(100.0*(abs(value)/axis_max))
    pwm.ChangeDutyCycle(speed)
    print('%s %f'%(direction, speed))


# Main controller loop
try:
    for event in gamepad.read_loop():
        # Joystick
        if event.type == ecodes.EV_ABS:
            value = event.value
            if abs(event.value) < axis_tol:
                value = 0.0
            if event.code == ecodes.ABS_Y: # Left stick Up/Down
               drive(pwm, motorA_dir_pin, motorB_dir_pin, value)
            elif event.code == ecodes.ABS_RX: # Right stick Left/Right
                turn(pwm, motorA_dir_pin, motorB_dir_pin, value)
        # Buttons
        elif event.type == ecodes.EV_KEY:
            button(event)
except:
    pass
finally:
    stop()
    #GPIO.cleanup()
