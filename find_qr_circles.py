import cv2
import numpy as np
from pyzbar import pyzbar

def find_qr_codes_in_circles(image):
    qr_codes_info = []  # List to store info about detected QR codes

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply median blur to reduce noise
    gray_blurred = cv2.medianBlur(gray, 5)

    # Detect circles using HoughCircles
    circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                               param1=50, param2=50, minRadius=20, maxRadius=220)

    # Check if circles were found
    if circles is not None:
        circles = np.uint16(np.around(circles[0, :]))

        # Loop over each detected circle
        for circle in circles:
            x, y, r = circle
            # Draw the circle and its center on the image
            cv2.circle(image, (x, y), r, (0, 255, 0), 2)
            cv2.circle(image, (x, y), 2, (0, 0, 255), 3)

            # Define the ROI based on the circle's position and radius
            x1 = max(0, x - r)
            y1 = max(0, y - r)
            x2 = min(image.shape[1], x + r)
            y2 = min(image.shape[0], y + r)
            roi = image[y1:y2, x1:x2]

            # Detect QR codes within the ROI
            decoded_objects = pyzbar.decode(roi)

            # If QR codes are found, process them
            if decoded_objects:
                for obj in decoded_objects:
                    # Get QR code data
                    qr_data = obj.data.decode('utf-8')

                    # Get QR code polygon points and adjust coordinates to the original image
                    points = obj.polygon
                    points_in_image = [(p.x + x1, p.y + y1) for p in points]

                    # Calculate the center of the QR code
                    n = len(points_in_image)
                    qr_center_x = sum([p[0] for p in points_in_image]) / n
                    qr_center_y = sum([p[1] for p in points_in_image]) / n

                    # Store the QR code information
                    qr_codes_info.append({
                        'data': qr_data,
                        'center': (qr_center_x, qr_center_y),
                        'points': points_in_image
                    })

                    # Draw the QR code polygon and center on the image
                    for j in range(n):
                        pt1 = points_in_image[j]
                        pt2 = points_in_image[(j + 1) % n]
                        cv2.line(image, pt1, pt2, (255, 0, 0), 3)
                    cv2.circle(image, (int(qr_center_x), int(qr_center_y)), 5, (0, 255, 255), -1)
    else:
        print("No circles found")

    # Display the image with detected QR codes and circles
    cv2.imshow('Image with QR Codes', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Return the list of detected QR codes with their centers and shapes
    return qr_codes_info

# Example usage:
image = cv2.imread('Norbert_il_robot/images/usb_camera_image_4.jpg')
qr_codes_info = find_qr_codes_in_circles(image)

# Print the detected QR codes information
for info in qr_codes_info:
    print("QR Code Data:", info['data'])
    print("Center Coordinates:", info['center'])
    print("Shape Points:", info['points'])
