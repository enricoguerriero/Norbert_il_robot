import requests
from rwsuis import RWS
from connect_camera import capture_and_save_image
import time

# help(RWS)
# Step 1: Set up the connection to Norbert
norbert_ip = "http://152.94.160.198"  
try:
    requests.get(norbert_ip)
    print("Connected to Norbert.")
except requests.exceptions.ConnectionError:
    print("Error: Unable to connect to Norbert. Please check the IP address.")
    exit(1)
robot = RWS.RWS(norbert_ip)

# Step 2: Read the WRD (or any other robtarget variable) and display its initial state
robot.request_rmmp()
while True:
    wrd_value = int(robot.get_rapid_variable("WRD"))
    print(wrd_value)
    if wrd_value == 0:
        print("Robot is waiting for Python to set 'WPW'")
        inputvalue = int(input("action: "))
        try:
            robot.set_rapid_variable("WPW",inputvalue)
            print("WPW set to",inputvalue)
        except:
            print("Error: Unable to set 'WPW' variabl1e.")
            robot.request_rmmp()
        if(inputvalue == 1):
            print("Move camera and take pictures")
            while True:
                dz_py = input("dz_py: ")
                robot.set_rapid_variable("dzpy", dz_py)
                capture_and_save_image(camera_index=0, save_path=f'usb_camera_image{time.time}.jpg')
                if input("Continue? (y/n): ") == "n":
                    break
        elif inputvalue > 1 and inputvalue < 5:
            print("execute action")
        else:
            print("Invalid input")
            break

