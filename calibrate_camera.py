import numpy as np
import cv2 as cv
import glob
import os

def calibrate_camera(images, chessboard_size=(7, 7), square_size=1.0, display_corners=False):
    """
    Calibrate the camera using multiple images of a chessboard pattern.

    Parameters:
    - calibration_images_dir: Directory containing calibration images.
    - chessboard_size: Tuple indicating the number of inner corners per chessboard row and column (rows, columns).
    - square_size: Size of a chessboard square (arbitrary unit, e.g., centimeters).
    - display_corners: Boolean flag to display detected corners on images.

    Returns:
    - ret: RMS re-projection error.
    - camera_matrix: Camera intrinsic matrix.
    - distortion_coefficients: Distortion coefficients.
    - rotation_vectors: Rotation vectors for each image.
    - translation_vectors: Translation vectors for each image.
    - mean_error: Mean reprojection error across all images.
    """

    # Termination criteria for corner refinement
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 1e-6)

    # Prepare object points based on the actual square size
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[1], 0:chessboard_size[0]].T.reshape(-1, 2)
    objp *= square_size  # Scale object points by square size

    # Arrays to store object points and image points from all images
    objpoints = []  # 3D points in real-world space
    imgpoints = []  # 2D points in image plane

    # Process each image
    for idx, fname in enumerate(images):
        img = cv.imread(fname)
        if img is None:
            print(f"Warning: Unable to read image '{fname}'. Skipping.")
            continue

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Find the chessboard corners
        ret, corners = cv.findChessboardCorners(gray, chessboard_size, None)

        # If corners are found, refine and add to the list
        if ret:
            objpoints.append(objp)

            # Refine corner locations to sub-pixel accuracy
            corners2 = cv.cornerSubPix(gray, corners, winSize=(11, 11), zeroZone=(-1, -1), criteria=criteria)
            imgpoints.append(corners2)

            if display_corners:
                # Draw and display the corners
                cv.drawChessboardCorners(img, chessboard_size, corners2, ret)
                cv.imshow('Detected Corners', img)
                cv.waitKey(500)  # Display each image for 500 ms

            print(f"Image {idx+1}/{len(images)}: Chessboard corners detected and refined.")
        else:
            print(f"Image {idx+1}/{len(images)}: Chessboard corners NOT detected.")

    if display_corners:
        cv.destroyAllWindows()

    # Ensure that sufficient points have been collected
    if not objpoints or not imgpoints:
        print("Error: No corners were detected in any image. Calibration failed.")
        return

    # Perform camera calibration
    ret, camera_matrix, distortion_coefficients, rotation_vectors, translation_vectors = cv.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )

    print("\nCamera calibration complete.")
    print(f"RMS Re-projection Error: {ret}")

    # Calculate the total reprojection error
    mean_error = 0
    total_points = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv.projectPoints(objpoints[i], rotation_vectors[i], translation_vectors[i], camera_matrix, distortion_coefficients)
        error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)
        mean_error += error**2
        total_points += len(objpoints[i])

    mean_error = np.sqrt(mean_error / total_points)
    print(f"Mean Re-projection Error: {mean_error}")

    return ret, camera_matrix, distortion_coefficients, rotation_vectors, translation_vectors, mean_error

def save_calibration_results(filename, camera_matrix, distortion_coefficients, rotation_vectors, translation_vectors):
    """
    Save calibration results to a file using NumPy's binary format.

    Parameters:
    - filename: Path to the file where calibration data will be saved.
    - camera_matrix: Camera intrinsic matrix.
    - distortion_coefficients: Distortion coefficients.
    - rotation_vectors: Rotation vectors for each calibration image.
    - translation_vectors: Translation vectors for each calibration image.
    """
    np.savez(filename, camera_matrix=camera_matrix, distortion_coefficients=distortion_coefficients,
             rotation_vectors=rotation_vectors, translation_vectors=translation_vectors)
    print(f"Calibration results saved to '{filename}.npz'.")

def load_calibration_results(filename):
    """
    Load calibration results from a file.

    Parameters:
    - filename: Path to the file from which to load calibration data.

    Returns:
    - camera_matrix: Camera intrinsic matrix.
    - distortion_coefficients: Distortion coefficients.
    - rotation_vectors: Rotation vectors for each calibration image.
    - translation_vectors: Translation vectors for each calibration image.
    """
    with np.load(filename) as X:
        camera_matrix = X['camera_matrix']
        distortion_coefficients = X['distortion_coefficients']
        rotation_vectors = X['rotation_vectors']
        translation_vectors = X['translation_vectors']
    print(f"Calibration results loaded from '{filename}'.")
    return camera_matrix, distortion_coefficients, rotation_vectors, translation_vectors

def undistort_image(img_path, camera_matrix, distortion_coefficients, save_path=None):
    """
    Undistort an image using the provided camera matrix and distortion coefficients.

    Parameters:
    - img_path: Path to the image to undistort.
    - camera_matrix: Camera intrinsic matrix.
    - distortion_coefficients: Distortion coefficients.
    - save_path: Optional path to save the undistorted image.

    Returns:
    - undistorted_img: The undistorted image.
    """
    img = cv.imread(img_path)
    if img is None:
        print(f"Error: Unable to read image '{img_path}'.")
        return None

    undistorted_img = cv.undistort(img, camera_matrix, distortion_coefficients, None, camera_matrix)

    cv.imshow('Original Image', img)
    cv.imshow('Undistorted Image', undistorted_img)
    cv.waitKey(0)
    cv.destroyAllWindows()

    if save_path:
        cv.imwrite(save_path, undistorted_img)
        print(f"Undistorted image saved to '{save_path}'.")

    return undistorted_img

def main():
    # Parameters (modify these as needed)
    calibration_images_directory = 'Norbert_il_robot/calibration_images'  # Directory containing calibration images
    chessboard_dimensions = (7, 7)  # Number of inner corners per chessboard row and column
    chessboard_square_size = 1.0  # Define the size of a square in your chessboard (e.g., 1.0 cm)
    display_detected_corners = True  # Set to True to visualize detected corners

    # Get list of calibration images
    images = glob.glob(os.path.join(calibration_images_directory, '*.jpg'))

    if not images:
        print(f"No images found in directory: {calibration_images_directory}")
        return

    # Calibrate the camera
    calibration_result = calibrate_camera(
        images=images,
        chessboard_size=chessboard_dimensions,
        square_size=chessboard_square_size,
        display_corners=display_detected_corners
    )

    if calibration_result:
        ret, camera_matrix, distortion_coefficients, rotation_vectors, translation_vectors, mean_error = calibration_result

        # Display calibration results
        print("\nCamera Matrix:")
        print(camera_matrix)
        print("\nDistortion Coefficients:")
        print(distortion_coefficients.ravel())

        # Save calibration results
        calibration_output_file = 'camera_calibration_results'
        save_calibration_results(calibration_output_file, camera_matrix, distortion_coefficients, rotation_vectors, translation_vectors)

        # Optionally, undistort a sample image
        sample_image_path = images[0]  # Using the first calibration image as a sample
        undistorted_image_path = 'undistorted_sample.jpg'
        undistort_image(sample_image_path, camera_matrix, distortion_coefficients, save_path=undistorted_image_path)

if __name__ == "__main__":
    main()
