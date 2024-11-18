from find_qr import detect_qr_code_centers_and_angles
import cv2


def give_puck_coordinates(pixel_puck, camera_coord):
    '''
    naive method for puck coordinates
    '''   
    
    focal_length = 3.7 # mm + 5% err
    
    picture_center = (480, 640) # to check !!!
    
    pixel_coord = (pixel_puck[0] - picture_center[0], pixel_puck[1] - picture_center[1])
    
    puck_coord = (pixel_coord[0] * camera_coord[2] / focal_length - camera_coord[0], pixel_coord[1] * camera_coord[2] / focal_length - camera_coord[1])
    
    return puck_coord

def give_puck_coordinates_2(pixel_puck, camera_coord, image_width, image_height, sensor_width_mm, sensor_height_mm, focal_length_mm):
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
    x_prime = pixel_puck[0] - c_x
    y_prime = pixel_puck[1] - c_y

    # Physical coordinates on the table plane
    X = camera_coord[0] + (x_prime * camera_coord[2]) / f_x
    Y = camera_coord[1] + (y_prime * camera_coord[2]) / f_y

    puck_coord = (X + 53, Y)

    return puck_coord




if __name__ == "__main__":
    
    image_paths = ['Norbert_il_robot/images/usb_camera_image_n50_2.jpg', 'Norbert_il_robot/images/usb_camera_image_2.jpg',
        'Norbert_il_robot/images/usb_camera_image_50_2.jpg']
    
    results_storage = []
    
    for idx, image_path in enumerate(image_paths):
        # Load the image using OpenCV
        image = cv2.imread(image_path)
        
        # Print the dimension of the image
        # print(f"Image dimensions: {image.shape}")
    
        # Detect QR codes in the original image
        results = detect_qr_code_centers_and_angles(image)

        # print(f"Results for image '{image_path}':")        
        # for result in results:
        #     result['center'] = (result['center'][0], result['center'][1])
        #     result['perspective'] = 50 * (idx-1)
        #     result['puck_coord'] = give_puck_coordinates(result['center'], (50*(idx-1), 50*(idx-1), 400))
        #     print(result)            
        # print("-" * 50, "\n")
        
        results_storage.extend(results)
        
        print(f'Results with the second method for image {image_path}:')
        for result in results:
            result['puck_coord_2'] = give_puck_coordinates_2(result['center'], (-50*(idx-1), 50*(idx-1), 370), image.shape[1], image.shape[0], 3.63, 2.72, 3.7)
            print(result['number'], ": ", result['puck_coord_2'])
        
        