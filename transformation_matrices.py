import numpy as np
import cv2
from find_qrgood import detect_qr_codes
from find_qr import detect_qr_code_centers_and_angles

def transformation_with_transformation_matrix(transformation_matrix, vector):
    
    transformation_matrix = np.array(transformation_matrix)
    vector = np.append(np.array(vector), 0)
    print(transformation_matrix)
    print(vector)
    
    if transformation_matrix.shape != (3, 3):
        print("Transformation matrix must be 3x3")
        return None
    if vector.shape != (3,):
        print("Vector must be 3x1")
        return None
    
    real_world_position_vector = np.dot(transformation_matrix, vector)
    real_world_position_vector = tuple(real_world_position_vector[:-1])
    print(real_world_position_vector)
    
    return real_world_position_vector

def compute_transformation_matrix(pixel_vector, real_vector, count):
    
    pixel_vector = np.array(pixel_vector)
    real_vector = np.array(real_vector)
    real_vector = np.tile(real_vector, (count, 1))
    print(pixel_vector.shape)
    print(real_vector.shape)
    
    # Compute the transformation matrix using np.linalg.lstsq
    transformation_matrix, residuals, rank = np.linalg.lstsq(pixel_vector, real_vector, rcond=None)[0]
    
    return transformation_matrix


if __name__ == "__main__":
    
    h_grip = 486
    cam_dif = 52
    cam_h = 44
    h = h_grip - cam_h
    
    image_paths = [f'Norbert_il_robot/images_tf/-100_-100_{h_grip}.jpg', f'Norbert_il_robot/images_tf/0_-100_{h_grip}.jpg', f'Norbert_il_robot/images_tf/100_-100_{h_grip}.jpg',
                   f'Norbert_il_robot/images_tf/-100_0_{h_grip}.jpg', f'Norbert_il_robot/images_tf/0_0_{h_grip}.jpg', f'Norbert_il_robot/images_tf/100_0_{h_grip}.jpg',
                   f'Norbert_il_robot/images_tf/-100_100_{h_grip}.jpg', f'Norbert_il_robot/images_tf/0_100_{h_grip}.jpg', f'Norbert_il_robot/images_tf/100_100_{h_grip}.jpg']
    print("Mapping puck ... ")
    cam_position = [(-100+cam_dif, -100, h), (-100+cam_dif, -0, h), (-100+cam_dif, 100, h),
                    (0+cam_dif, -100, h), (0+cam_dif, -0, h), (0+cam_dif, 100, h),
                    (100+cam_dif, -100, h), (100+cam_dif, -0, h), (100+cam_dif, 100, h),]
    centers = []
    count = 0
    for i, image_path in enumerate(image_paths):
        image = cv2.imread(image_path)
        qr = detect_qr_codes(image)
        print(qr)
        if not qr:
            print(f'QR code not detected in image {i}')
            qr = detect_qr_code_centers_and_angles(image)
            print(qr)
            if not qr:
                print(f'QR code not detected in image {i}')
                continue
        qr_center = qr[0]['center']
        c_x = image.shape[1] / 2
        c_y = image.shape[0] / 2
        y_prime = -(qr_center[0] - c_x)
        x_prime = -(c_y - qr_center[1])
        center = (x_prime, y_prime, 1)
        centers.append(center)
        count = count + 1

    real_position = [0,0,1]
    
    
    mat = compute_transformation_matrix(centers, real_position, count)
    print(mat)
    
    
    