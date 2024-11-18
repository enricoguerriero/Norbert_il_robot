import cv2
import sys
import time

def capture_and_save_image(camera_index=1, save_path='usb_camera_image.jpg'):
    # Initialize video capture with the specified camera index
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"Error: Could not open camera with index {camera_index}")
        sys.exit(1)

    # Optionally set the resolution (uncomment and adjust if needed)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Allow the camera to warm up
    time.sleep(1)  # Wait for 1 second

    # Capture a single frame
    ret, frame = cap.read()

    if ret:
        # Save the captured image to disk
        success = cv2.imwrite(save_path, frame)
        if success:
            print(f"Image successfully saved to {save_path}")
        else:
            print("Error: Failed to save the image")
    else:
        print("Error: Failed to capture image")
        
    # Release the camera resource
    cap.release()

    # Return the picture (maybe useless)
    return frame

if __name__ == "__main__":
    # Replace '1' with your camera index if different
    # Replace 'usb_camera_image.jpg' with your desired save path and filename
    capture_and_save_image(camera_index=1, save_path='usb_camera_image.jpg')
