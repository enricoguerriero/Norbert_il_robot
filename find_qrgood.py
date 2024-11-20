import cv2
from pyzbar.pyzbar import decode
import numpy as np

def apply_perspective_transform(image):
    """
    Apply perspective transform to handle slightly rotated or skewed images
    """
    height, width = image.shape[:2]
    corners = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    new_corners = np.float32([[0, 0], [width-10, 0], [0, height-10], [width-10, height-10]])
    matrix = cv2.getPerspectiveTransform(corners, new_corners)
    return cv2.warpPerspective(image, matrix, (width, height))

def enhance_image(image):
    """
    Apply various image enhancement techniques to improve QR code detection
    """
    enhanced_versions = []
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    enhanced_versions.append(gray)
    
    # Basic thresholding variations
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    enhanced_versions.append(binary)
    
    # Multiple adaptive thresholding with different parameters
    adaptive_thresh_params = [
        (11, 2), (21, 10), (31, 15), (41, 20)
    ]
    for block_size, C in adaptive_thresh_params:
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, block_size, C
        )
        enhanced_versions.append(thresh)
    
    # Bilateral filtering with different parameters
    bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
    enhanced_versions.append(bilateral)
    
    # Multiple kernel sizes for sharpening
    sharpening_kernels = [
        np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]),
        np.array([[-2,-2,-2], [-2,17,-2], [-2,-2,-2]]) / 9
    ]
    for kernel in sharpening_kernels:
        sharpened = cv2.filter2D(bilateral, -1, kernel)
        enhanced_versions.append(sharpened)
    
    # Contrast stretching
    min_val, max_val = np.percentile(gray, (2, 98))
    contrast_stretched = np.clip((gray - min_val) * 255.0 / (max_val - min_val), 0, 255).astype(np.uint8)
    enhanced_versions.append(contrast_stretched)
    
    # Perspective transform variations
    enhanced_versions.append(apply_perspective_transform(gray))
    
    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    clahe_img = clahe.apply(gray)
    enhanced_versions.append(clahe_img)
    
    # Morphological operations
    kernel_sizes = [(3,3), (5,5)]
    for ksize in kernel_sizes:
        kernel = np.ones(ksize, np.uint8)
        # Dilated
        dilated = cv2.dilate(gray, kernel, iterations=1)
        enhanced_versions.append(dilated)
        # Eroded
        eroded = cv2.erode(gray, kernel, iterations=1)
        enhanced_versions.append(eroded)
        # Opening
        opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        enhanced_versions.append(opened)
        # Closing
        closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        enhanced_versions.append(closed)
    
    return enhanced_versions

def detect_qr_codes(original_frame):
    #original_frame = cv2.imread(image)
    results = []
    if original_frame is None:
        print("Failed to load image")
        return
    
    detected_qrs = set()
    all_polygons = []
    frame = original_frame.copy()
        
    # Get enhanced versions
    enhanced_versions = enhance_image(original_frame)
        
    # Try to detect QR codes in each enhanced version
    for idx, enhanced in enumerate(enhanced_versions):
            qr_codes = decode(enhanced)  
            for qr in qr_codes:
                qr_data = qr.data.decode('utf-8')    
                if qr_data not in detected_qrs:
                    detected_qrs.add(qr_data)
                    points = qr.polygon

                    if len(points) == 4:
                        box_points = np.array([[point.x, point.y] for point in points], dtype=np.float32)    
                        all_polygons.append(box_points)
                            
                        # Calculate and print information
                        rect = cv2.minAreaRect(box_points)
                            
                        """print(f"Found QR Code:")
                        print(f"  Data: {qr_data}")
                        print(f"  Enhancement method: {idx}")
                        print(f"  Angle: {angle:.2f}°")
                        print(f"  Center: ({center_x:.1f}, {center_y:.1f})")
                        print("-" * 50)"""
                        
                        center, size, angle = rect
                        center_x, center_y = int(center[0]), int(center[1])
                        
                        
                        results.append({
                            'center': (center_x, center_y),
                            'angle': angle,
                            'size': size,
                            'number': qr_data[-1]
                        })
                        #print(results)
    
            # Draw results on original image
            for box_points in all_polygons:
                rect = cv2.minAreaRect(box_points)
                box = cv2.boxPoints(rect)
                box = np.intp(box)
                
                # Draw bounding box
                cv2.polylines(frame, [box], True, (0, 0, 255), 2)
                
                # Draw center point
                center_x, center_y = rect[0]
                cv2.circle(frame, (int(center_x), int(center_y)), 5, (255, 0, 0), -1)
            
            #print(f"\nTotal unique QR codes detected: {len(detected_qrs)}")
            
    # Save and display results
    output_path = f"detected_qr_codes.png"
    cv2.imwrite(output_path, frame)
    print(f"Image saved as '{output_path}'")
            
    # Display results
    cv2.imshow("Detected QR Codes", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
            
    return(results)
    
def main():
    # Path to your image containing QR codes
    image_path = 'Applied-Robot-Technologies/Norbert_il_robot/images/usb_camera_image_4.jpg' 
    # Load the image using OpenCV
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Unable to load image at '{image_path}'. Please check the path.")
        return

    # Detect QR codes in the original image
    results_original = detect_qr_codes(image)

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
