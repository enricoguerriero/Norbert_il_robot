from find_qr import detect_qr_code_centers_and_angles
import cv2


# def give_puck_coordinates(pixel_puck, camera_coord):
#     '''
#     naive method for puck coordinates
#     '''   
    
#     focal_length = 3.7 # mm + 5% err
    
#     picture_center = (480, 640) # to check !!!
    
#     pixel_coord = (pixel_puck[0] - picture_center[0], pixel_puck[1] - picture_center[1])
    
#     puck_coord = (pixel_coord[0] * camera_coord[2] / focal_length - camera_coord[0], pixel_coord[1] * camera_coord[2] / focal_length - camera_coord[1])
    
#     return puck_coord

def give_puck_coordinates(pixel_puck, camera_coord, image_width, image_height, sensor_width_mm, sensor_height_mm, focal_length_mm):
    '''
    Improved method for calculating puck coordinates on the table.
    '''

    # Convert focal length to pixels
    f_x = (focal_length_mm / sensor_width_mm) * image_width
    f_y = (focal_length_mm / sensor_height_mm) * image_height

    # Principal point (image center)
    c_x = image_width / 2
    c_y = image_height / 2

    # Adjust pixel coordinates to be centered
    y_prime = -(pixel_puck[0] - c_x)
    x_prime = -(c_y - pixel_puck[1])

    # Physical coordinates on the table plane
    X = camera_coord[0] + (x_prime * camera_coord[2]) / f_x
    Y = camera_coord[1] + (y_prime * camera_coord[2]) / f_y

    puck_coord = (X-3.45, Y+14.95)

    # correct respect to camera position

    return puck_coord




if __name__ == "__main__":
    
    image_paths = ['images/usb_camera_image_1.jpg',
                   'images/usb_camera_image_2.jpg', 'images/usb_camera_image_3.jpg',
                   'images/usb_camera_image_4.jpg', 'images/usb_camera_image_5.jpg']
    
    print("Mapping puck ... ")
    map_dic = {}
    cam_dif = 0
    
    cam_position = [(0+cam_dif, 0, 370), (-100+cam_dif, -100, 370), (-100+cam_dif, 100, 370), (100+cam_dif, 100, 370), (100+cam_dif, -100, 370)]
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
                print(f"Difference for puck {puck['number']} between the two coordinates: {diff}")
                print("Computing the mean")
                x = (map_dic[puck["number"]][0] + puck_coord[0]) / 2
                y = (map_dic[puck["number"]][1] + puck_coord[1]) / 2
                map_dic[puck["number"]] = (x, y)
    print("Puck mapping completed")
    print("Puck mapped: ", map_dic)
        