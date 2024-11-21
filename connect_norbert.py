import requests
from rwsuis import RWS
from connect_camera import capture_and_save_image
from find_qr import detect_qr_code_centers_and_angles
import time
from map_puck import give_puck_coordinates
import cv2
import numpy as np
from utils import ask_for_a_puck, ask_for_a_place, is_the_spot_free

# help(RWS)
# connection with norbert
norbert_ip = "http://152.94.160.198"  
try:
    requests.get(norbert_ip)
    print("Connected to Norbert.")
except requests.exceptions.ConnectionError:
    print("Error: Unable to connect to Norbert. Please check the IP address.")
    exit(1)
robot = RWS.RWS(norbert_ip)

# actually starting
robot.request_rmmp()
while True:
    time.sleep(3)
    wrd_value = int(robot.get_rapid_variable("WRD"))
    print(wrd_value)
    close_gripper = False
    
    if wrd_value == 0:
        print("Robot is waiting for Python to set 'WPW'")
        inputvalue = int(input("action: "))
            
        if(inputvalue == 1):
            print("\n--- Mapping pucks ---\n")
            robot.set_rapid_variable("WPW",inputvalue)
            print("Move camera and take pictures")
            map_dic = {}
            angle_dic = {}
            # try to manage camera - robot communication with index variable
            for i in range(5):
                robot.set_rapid_variable("index", 1)
                while int(robot.get_rapid_variable("index")) == 1:
                    print("Waiting for robot to move ... zzz ...")
                    time.sleep(1)
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
                        map_dic[puck["number"]] = (puck_coord[0], puck_coord[1], 0)
                        angle_dic[puck["number"]] = puck["angle"]
                    else:
                        print("Puck already in the dictionary")
                        diff = (map_dic[puck['number']][0] - puck_coord[0],map_dic[puck['number']][1] - puck_coord[1])
                        print(f"Difference between the two coordinates: {diff}")
                        print("Computing the mean")
                        x = (map_dic[puck["number"]][0] + puck_coord[0]) / 2
                        y = (map_dic[puck["number"]][1] + puck_coord[1]) / 2
                        angle = (angle_dic[puck["number"]] + puck["angle"]) / 2
                        map_dic[puck["number"]] = (x, y, 0)
                        angle_dic[puck["number"]] = angle # * (np.pi / 180)
            print("Puck mapping completed")
            print("Puck mapped: ", map_dic)
            print("Puck angle: ", angle_dic)
            robot.set_rapid_variable("WPW",0)
            
        elif (inputvalue == 2):
            print("\n--- Rotate pucks ---\n")
            if close_gripper:
                print("Gripper is closed, you can't pick up the pucks")
                robot.set_rapid_variable("WPW",0)
                continue
            robot.set_rapid_variable("numqr", len(map_dic))
            robot.set_rapid_variable("index", 0)
            robot.set_rapid_variable("WPW",inputvalue)
            for puck in map_dic.keys():
                time.sleep(1)
                print(f"Rotating puck {puck}")
                robot.set_rapid_variable("dx1py", map_dic[puck][0])
                robot.set_rapid_variable("dy1py", map_dic[puck][1])
                robot.set_rapid_variable("dz1py", map_dic[puck][2])
                robot.set_rapid_variable("anglepy", round(angle_dic[puck]))
                robot.set_rapid_variable("index", 1)
                angle_dic[puck] = 0
                time.sleep(5)
                while int(robot.get_rapid_variable("index")) == 1:
                    time.sleep(1)
            robot.set_rapid_variable("WPW",0)
            
        elif (inputvalue == 3):
            print("\n --- Take a puck ---\n")
            if close_gripper:
                print("Gripper is closed, you can't take a puck")
                robot.set_rapid_variable("WPW",0)
                continue
            puck_to_take = input("Puck to take: ")
            dx = map_dic[puck_to_take][0]
            dy = map_dic[puck_to_take][1]
            dz = map_dic[puck_to_take][2]
            robot.set_rapid_variable("dx1py", dx)
            robot.set_rapid_variable("dy1py", dy)
            robot.set_rapid_variable("dz1py", dz)
            robot.set_rapid_variable("WPW",inputvalue)
            time.sleep(5)
            close_gripper = True
            robot.set_rapid_variable("WPW",0)
        
        elif (inputvalue == 4):
            print("\n --- Place a puck ---\n")
            if not close_gripper:
                print("Gripper is not closed, you can't place a puck")
                robot.set_rapid_variable("WPW",0)
                continue
            print("Where do you want to place the puck?")
            dx = input("dx: ")
            dy = input("dy: ")
            dz = input("dz: ")
            robot.set_rapid_variable("dx1py", dx)
            robot.set_rapid_variable("dy1py", dy)
            robot.set_rapid_variable("dz1py", dz)
            robot.set_rapid_variable("WPW",inputvalue)
            time.sleep(5)
            close_gripper = False
            robot.set_rapid_variable("WPW",0)
            
            
        elif (inputvalue == 5):
            print("\n --- Invert pucks ---\n")
            if close_gripper:
                print("Gripper is closed, you can't invert the pucks")
                robot.set_rapid_variable("WPW",0)
                continue
            puck_1 = ask_for_a_puck(map_dic)
            if puck_1 is None:
                robot.set_rapid_variable("WPW",0)
                continue
            puck_2 = ask_for_a_puck(map_dic)
            if puck_2 is None:
                robot.set_rapid_variable("WPW",0)
                continue
            if is_the_spot_free(map_dic, 0, 0):
                print("Origin is free")
                dx_spot = 0
                dy_spot = 0
            elif is_the_spot_free(map_dic, 0, 100):
                print("Origin is not free, moving to the right")
                dx_spot = 0
                dy_spot = 100
            elif is_the_spot_free(map_dic, 0, -100):
                print("Origin is not free, moving to the left")
                dx_spot = 0
                dy_spot = -100
            elif is_the_spot_free(map_dic, 100, 0):
                print("Origin is not free, moving up")
                dx_spot = 100
                dy_spot = 0
            elif is_the_spot_free(map_dic, -100, 0):
                print("Origin is not free, moving down")
                dx_spot = -100
                dy_spot = 0
            else:
                print("No free spot found")
                robot.set_rapid_variable("WPW",0)
                continue
            robot.set_rapid_variable("dx1py", map_dic[puck_1][0])
            robot.set_rapid_variable("dy1py", map_dic[puck_1][1])
            robot.set_rapid_variable("dz1py", map_dic[puck_1][2])
            robot.set_rapid_variable("dx2py", map_dic[puck_2][0])
            robot.set_rapid_variable("dy2py", map_dic[puck_2][1])
            robot.set_rapid_variable("dz2py", map_dic[puck_2][2])
            robot.set_rapid_variable("dx3py", dx_spot)
            robot.set_rapid_variable("dy3py", dy_spot)
            robot.set_rapid_variable("dz3py", 0)
            robot.set_rapid_variable("WPW",inputvalue)
            time.sleep(5)
            robot.set_rapid_variable("WPW",0)
        
        
        elif (inputvalue == 6):
            print("\n--- Create a stack ---\n")
            if close_gripper:
                print("Gripper is closed, you can't create a stack")
                robot.set_rapid_variable("WPW",0)
                continue
            robot.set_rapid_variable("numqr", len(map_dic))
            robot.set_rapid_variable("index", 0)
            robot.set_rapid_variable("WPW",inputvalue)
            n_puck = 0
            if any(abs(map_dic[puck][0]) < 20 and abs(map_dic[puck][1])):
                origin = (0,0,0)
            else:
                print("Origin is not free for building the stack, give me custom coordinates")
                dx = input("dx: ")
                dy = input("dy: ")
                origin = (dx, dy, 0)
            for puck in map_dic.keys():
                time.sleep(1)
                print(f"Creating stack for puck {puck}")
                robot.set_rapid_variable("dx1py", map_dic[puck][0])
                robot.set_rapid_variable("dy1py", map_dic[puck][1])
                robot.set_rapid_variable("dz1py", map_dic[puck][2])
                robot.set_rapid_variable("anglepy", angle_dic[puck])
                robot.set_rapid_variable("dx2py", origin[0])
                robot.set_rapid_variable("dy2py", origin[1])
                robot.set_rapid_variable("dz2py", origin[2])
                origin = (origin[0], origin[1], origin[2] + 30)                    
                n_puck += 1
                
                robot.set_rapid_variable("index", 1)
                angle_dic[puck] = 0
                time.sleep(5)
                while int(robot.get_rapid_variable("index")) == 1:
                    time.sleep(1)
            time.sleep(5)
            robot.set_rapid_variable("WPW",0)
        
        elif (inputvalue == 7):
            print("\n--- Open / Close gripper ---\n")
            print("1. Open gripper")
            print("2. Close gripper")
            gripper_action = 0
            while gripper_action != 1 and gripper_action != 2:
                gripper_action = int(input("Action: "))
                if gripper_action == 1:
                    robot.set_rapid_variable("gripper_py", 1)
                    close_gripper = False
                elif gripper_action == 2:
                    robot.set_rapid_variable("gripper_py", 2)
                    close_gripper = True
                else:
                    print("Invalid input, please try again")
                    print("Choose a number between 1 and 2")
            robot.set_rapid_variable("WPW",inputvalue)
            time.sleep(5)
            robot.set_rapid_variable("WPW",0)
            
        elif (inputvalue == 8):
            print("\n--- Move puck ---\n")
            if close_gripper:
                print("Gripper is closed, you can't move a puck")
                robot.set_rapid_variable("WPW",0)
                continue
            puck_to_move = ask_for_a_puck(map_dic)
            if puck_to_move is None:
                robot.set_rapid_variable("WPW",0)
                continue
            place = ask_for_a_place(map_dic)
            dx = place[0]
            dy = place[1]
            dz = place[2]
            robot.set_rapid_variable("dx1py", map_dic[puck_to_move][0])
            robot.set_rapid_variable("dy1py", map_dic[puck_to_move][1])
            robot.set_rapid_variable("dz1py", map_dic[puck_to_move][2])
            robot.set_rapid_variable("dx2py", dx)
            robot.set_rapid_variable("dy2py", dy)
            robot.set_rapid_variable("dz2py", dz)
            robot.set_rapid_variable("WPW",inputvalue)
            time.sleep(5)
            robot.set_rapid_variable("WPW",0)
                       
        elif (inputvalue == 9):
            print("\n--- Take some pictures ---\n")
            robot.set_rapid_variable("WPW",inputvalue)
            while True:
                robot.set_rapid_variable("index",0)
                print("1. Take a picture")
                print("2. Exit")
                action = int(input("Action: "))
                if action == 1:
                    print("From where do you want to take the picture?")
                    dx = input("dx: ")
                    dy = input("dy: ")
                    dz = input("dz: ")
                    robot.set_rapid_variable("dx1py", dx)
                    robot.set_rapid_variable("dy1py", dy)
                    robot.set_rapid_variable("dz1py", dz)
                    robot.set_rapid_variable("index",1)
                    while int(robot.get_rapid_variable("index")) == 1:
                        time.sleep(1)
                        print("Waiting for robot to move ... zzz ...")
                    print("Taking picture ...")
                    capture_and_save_image(camera_index=1, save_path=f'images_tf/{dx}_{dy}_{dz}.jpg')
                elif action == 2:
                    robot.set_rapid_variable("index",1)
                    robot.set_rapid_variable("stop_py",1)
                    robot.set_rapid_variable("WPW",0)
                    break
                else:
                    print("Invalid input")
                    break
     
        else:
            print("Invalid input")
            break
        

