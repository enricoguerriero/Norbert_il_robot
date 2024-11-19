import cv2
from pyzbar.pyzbar import decode
import numpy as np

def detect_qr_code_centers_and_angles(image):
    """
    Detect QR codes in an image and return the coordinates of their centers and rotation angles.

    Parameters:
    - image: Input image (as a NumPy array)

    Returns:
    - results: List of dictionaries with keys 'center' and 'angle'
               'center' is a tuple (x, y)
               'angle' is the rotation angle in degrees
    """
    results = []
    
    contrast_list = [1, 1.5, 2, 2.5, 3]
    
    color = [True, False]
    
    # try both colored and grayscale images
    for col in color:
        if not col: 
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
        # apply more contrast to the image
        for contrast in contrast_list:
            
            p_image = cv2.convertScaleAbs(image, alpha=contrast, beta=50)

            # Decode the QR codes in the image
            decoded_objects = decode(p_image)
            
            # print(f"color: {col}, contrast: {contrast}")

            for obj in decoded_objects:
                # Get the points of the bounding polygon
                points = obj.polygon

                # Convert the points to a numpy array of shape (n,2)
                pts = np.array([[point.x, point.y] for point in points], dtype=np.float32)

                # Compute the minimum area rectangle that encloses the QR code
                rect = cv2.minAreaRect(pts)
                center, size, angle = rect

                # Convert center coordinates to integers
                center_x, center_y = int(center[0]), int(center[1])
                
                data = obj.data.decode('utf-8')[-1]
                
                if not any(data in qr['number'] for qr in results):
                    
                    results.append({
                        'center': (center_x, center_y),
                        'angle': angle,
                        'size': size,
                        'number': data
                    })
                    # print(f"QR code {data} detected with color {col} and contrast {contrast}")

    return results


def main():
    # Path to your image containing QR codes
    image_path = 'images/usb_camera_image_0.jpg' 

    # Load the image using OpenCV
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Unable to load image at '{image_path}'. Please check the path.")
        return

    # Detect QR codes in the original image
    results_original = detect_qr_code_centers_and_angles(image)


    # Print the detection results
    print("=== Detection on the Image ===")
    if results_original:
        for idx, res in enumerate(results_original):
            print(f"QR Code {idx+1}:")
            print(f" Center: {res['center']}")
            print(f" Rotation Angle: {res['angle']:.1f} degrees")
            print(f" Number: {res['number']}\n")
    else:
        print("No QR codes detected in the image.\n")

    # Display the annotated images
    for idx, res in enumerate(results_original):
        center = res['center']
        cv2.circle(image, center, 5, (0, 0, 255), -1)
        
    cv2.imshow("Image with QRs", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    
if __name__ == "__main__":
    main()
