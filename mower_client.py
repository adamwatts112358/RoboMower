from evdev import list_devices, InputDevice, categorize, ecodes
import socket

### To do: implement constant heartbeat ###

def set_keepalive_linux(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect the socket to the port on the server
server_address = ('raspberrypi.local', 10000)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)
set_keepalive_linux(sock)
sock.setblocking(False)

# Setup gamepad
zeroL = 0.0
zeroR = 0.0
axis_max = 33000.0
axis_tol = 10*330.0
gamepad = InputDevice(list_devices()[0])
print(gamepad)

def button(event):
    # B button
    if event.code == 305:
        if event.value == 1:
            message = "Stop!".encode('utf-8')
            #message += b'0'*(8-len(message))
            print(message, len(message))
            sock.sendall(message)
            
def driveMotor(stick, value):
    # Set the direction pin
    if value <= 0.0:
        direction = 'F'
    elif value > 0.0:
        direction = 'B'

    # Set the PWM speed
    speed = float(100.0*(abs(value)/axis_max))
    message = '%s %s %.1f'%(stick, direction, speed)
    message = message.encode('utf-8')
    # Pad the message with null bytes if needed to get to 8
    message += b'0'*(8-len(message))
    print(message, len(message))
    
    # Send command to mower
    sock.sendall(message)

while True:
    # Main controller loop
    #try:
    for event in gamepad.read_loop():
        # Joystick
        if event.type == ecodes.EV_ABS:
            value = event.value
            if abs(event.value) < axis_tol:
                value = 0.0
            if event.code == ecodes.ABS_Y: # Left stick Up/Down
                driveMotor('L', value)
            elif event.code == ecodes.ABS_RY: # Right stick Up/Down
                driveMotor('R', value)
        # Buttons
        elif event.type == ecodes.EV_KEY:
            button(event)
    #except:
    #    pass
    #finally:
    #    print('Exiting.')
    #    sock.close()
