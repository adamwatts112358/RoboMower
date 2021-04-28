import RPi.GPIO as GPIO
import socket

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address given on the command line
server_name = 'raspberrypi.local'
server_address = (server_name, 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)
sock.listen(1)

zeroL = 0.0
zeroR = 0.0

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

motorA_dir_pin = 26 # Green
motorA_pwm_pin = 19 # Blue
motorB_dir_pin = 23 #20 # Purple
motorB_pwm_pin = 24 #21 # Grey

status_LED_pin = 14
GPIO.setup(status_LED_pin, GPIO.OUT)
GPIO.output(status_LED_pin, GPIO.HIGH)

GPIO.setup(motorA_dir_pin, GPIO.OUT)
GPIO.setup(motorA_pwm_pin, GPIO.OUT)
GPIO.setup(motorB_dir_pin, GPIO.OUT)
GPIO.setup(motorB_pwm_pin, GPIO.OUT)
pwm_freq = 500.0
pwm_A = GPIO.PWM(motorA_pwm_pin, pwm_freq)
pwm_B = GPIO.PWM(motorB_pwm_pin, pwm_freq)
pwm_A.start(0)
pwm_B.start(0)

def stop():
    GPIO.output(motorA_dir_pin, GPIO.LOW)
    GPIO.output(motorA_pwm_pin, GPIO.LOW)
    GPIO.output(motorB_dir_pin, GPIO.LOW)
    GPIO.output(motorB_pwm_pin, GPIO.LOW)
    pwm_A.ChangeDutyCycle(0.0)
    pwm_B.ChangeDutyCycle(0.0)
    print("Stop!")

def zero(event):
    global zeroL, zeroR
    if event.code == ecodes.ABS_Y:
        # Zero the left stick
        zeroL = event.value
    elif event.code == ecodes.ABS_RY:
        # Zero the right stick
        zeroR = event.value
            
def driveMotor(motor, direction, speed):
    if motor is "L":
        dir_pin = motorA_dir_pin
        pwm = pwm_A
    elif motor is "R":
        dir_pin = motorB_dir_pin
        pwm = pwm_B
    # Set the direction pin
    if direction is 'F':
        GPIO.output(dir_pin, GPIO.HIGH)
    elif direction is 'B':
        GPIO.output(dir_pin, GPIO.LOW)

    # Set the PWM speed
    pwm.ChangeDutyCycle(speed)
    print('%s %s %f'%(motor, direction, speed))

while True:
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('client connected:', client_address)
        while True:
            data = connection.recv(8)
            if data:
                #connection.sendall(data) # respond to client
                message = data.decode('utf-8')
                if "Stop!" in message:
                    stop()
                else:
                    motor = message.split()[0]
                    direction = message.split()[1]
                    speed = float(message.split()[2])
                    driveMotor(motor, direction, speed)
            else:
                break
    finally:
        stop()
        GPIO.cleanup()
        connection.close()
