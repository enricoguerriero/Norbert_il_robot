import requests
from rwsuis import RWS
from connect_camera import capture_and_save_image
from find_qr import detect_qr_code_centers_and_angles
import time
from map_puck import give_puck_coordinates
import cv2

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
    time.sleep(3)
    wrd_value = int(robot.get_rapid_variable("WRD"))
    print(wrd_value)
    
    if wrd_value == 0:
        print("Robot is waiting for Python to set 'WPW'")
        inputvalue = int(input("action: "))
            
        if(inputvalue == 1):
            robot.set_rapid_variable("WPW",inputvalue)
            print("Move camera and take pictures")
            map_dic = {}
            for i in range(5):
                # print(i)
                # robot.set_rapid_variable("Wait", i)
                print("Sleeping...")
                time.sleep(4.5)
                # check = int(robot.get_rapid_variable("check"))
                # print(check)
                # while check == 0:
                #     check = int(robot.get_rapid_variable("check"))
                #     print("sleep... zzz... zzz...")
                #     time.sleep(3)
                print("Taking picture ...")
                start = time.time()
                capture_and_save_image(camera_index=1, save_path=f'images/usb_camera_image_{i}.jpg')
                end = time.time()
                delta = end - start
                print(f'Tempo di una foto: {delta}')

            print("Pictures taken")
            print("Mapping puck ... ")
            cam_position = [(0, 0, 470), (-100, -100, 470), (-100, 100, 470), (100, 100, 470), (100, -100, 470)]
            for i in range(5):
                image_path = f'images/usb_camera_image_{i}.jpg'
                image = cv2.imread(image_path)
                pucks = detect_qr_code_centers_and_angles(image)
                numbers = [puck['number'] for puck in pucks]
                print(f'Detected QR code numbers: {numbers}')

                for puck in pucks:
                    puck_coord = give_puck_coordinates(puck['center'], cam_position[i], image.shape[1], image.shape[0], 3.68, 2.76, 3.7)
                    if puck["number"] not in map_dic:
                        map_dic[puck["number"]] = puck_coord
                    else:
                        print("Puck already in the dictionary")
                        diff = (map_dic[puck['number']][0] - puck_coord[0],map_dic[puck['number']][1] - puck_coord[1])
                        print(f"Difference between the two coordinates: {diff}")
                        print("Computing the mean")
                        x = (map_dic[puck["number"]][0] + puck_coord[0]) / 2
                        y = (map_dic[puck["number"]][1] + puck_coord[1]) / 2
                        map_dic[puck["number"]] = (x, y)
            print("Puck mapping completed")
            print("Puck mapped: ", map_dic)
            robot.set_rapid_variable("WPW",0)
            
        elif (inputvalue == 3):
            print("Move to puck")
            dx = input("dx: ")
            dy = input("dy: ")
            dz = input("dz: ")
            robot.set_rapid_variable("dx1py", dx)
            robot.set_rapid_variable("dy1py", dy)
            robot.set_rapid_variable("dz1py", dz)
            robot.set_rapid_variable("WPW",inputvalue)
            time.sleep(5)
            robot.set_rapid_variable("WPW",0)
        
        elif (inputvalue == 4):
            print("Move to puck")
            dx = input("dx: ")
            dy = input("dy: ")
            dz = input("dz: ")
            robot.set_rapid_variable("dx1py", dx)
            robot.set_rapid_variable("dy1py", dy)
            robot.set_rapid_variable("dz1py", dz)
            robot.set_rapid_variable("WPW",inputvalue)
            time.sleep(5)
            robot.set_rapid_variable("WPW",0)
            
        elif inputvalue > 1 and inputvalue < 5:
            print("execute action")
        else:
            print("Invalid input")
            break
        

