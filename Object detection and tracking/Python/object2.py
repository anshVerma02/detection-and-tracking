import cv2
import numpy as np
import urllib.request
import requests
import matplotlib.pyplot as plt
import time

# URLs for the video stream and servo control
url = 'http://192.168.0.103/cam-hi.jpg'
control_url = 'http://192.168.0.103/control'
servoX = 90
servoY = 90

# Defining two HSV ranges for red color
lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([160, 100, 100])
upper_red2 = np.array([180, 255, 255])

# Lists to store data for plotting
servoX_data = []
servoY_data = []
object_center_data = []

# Throttle time (in seconds) between servo commands
throttle_time = 0.1  
last_command_time = time.time()

# Deadband threshold (minimum pixel difference to trigger servo movement)
deadband_threshold = 10  

# Function to adjust the servos
def adjust_servos(x, y):
    global last_command_time

    # Checking if enough time has passed since the last command
    if time.time() - last_command_time < throttle_time:
        return

    params = {'x': x, 'y': y}
    try:
        response = requests.get(control_url, params=params)
        print(f"Adjusting servos to x: {x}, y: {y}, Response: {response.status_code}, Text: {response.text}")
    except requests.RequestException as e:
        print(f"Error sending request: {e}")

    last_command_time = time.time()

# Function to update the plot
def update_plot():
    plt.clf()  # Clear the current figure

    # Plot servo X movement
    plt.plot(servoX_data, label='Servo X', color='blue')

    # Plot servo Y movement
    plt.plot(servoY_data, label='Servo Y', color='green')

    # Plot object center movement
    plt.plot(object_center_data, label='Object Center', color='red')

    plt.legend(loc='upper right')
    plt.xlabel('Frame')
    plt.ylabel('Position')
    plt.title('Servo and Object Movement')
    plt.pause(0.001)  # Pause to update the plot

# Main detection function
def run_detection():
    global servoX, servoY

    plt.ion()  # Turn on interactive mode for real-time plotting

    while True:
        try:
            img_resp = urllib.request.urlopen(url)
            imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            im = cv2.imdecode(imgnp, -1)

            # Fixing the inverted image
            im = cv2.rotate(im, cv2.ROTATE_180)

            # Convert the image to HSV color space
            hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

            # Creating two masks for red color and combine them
            mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask_red = cv2.bitwise_or(mask_red1, mask_red2)

            # Applying morphological operations to reduce noise in the mask
            kernel = np.ones((5, 5), np.uint8)
            mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
            mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)

            # Find contours in the mask
            contours, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # Find the largest contour 
                largest_contour = max(contours, key=cv2.contourArea)

                # Filter out small contours
                min_contour_area = 500  
                if cv2.contourArea(largest_contour) > min_contour_area:
                    # Get the bounding box of the largest contour
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Calculate the center of the bounding box
                    x_center = x + w // 2
                    y_center = y + h // 2

                    # Calculate the difference between the center and the image center
                    x_diff = x_center - im.shape[1] // 2
                    y_diff = y_center - im.shape[0] // 2

                    # Applying the deadband threshold
                    if abs(x_diff) > deadband_threshold or abs(y_diff) > deadband_threshold:
                        # Updating servo positions using proportional control
                        servoX -= int(x_diff * 0.05)  
                        servoY += int(y_diff * 0.05)  

                        # Clamp the servo values to stay within valid range
                        servoX = max(0, min(180, servoX))
                        servoY = max(0, min(180, servoY))

                        # Sending the adjusted servo positions
                        adjust_servos(servoX, servoY)

                        # Append data for plotting
                        servoX_data.append(servoX)
                        servoY_data.append(servoY)
                        object_center_data.append((x_center, y_center))

                        # Update the plot
                        update_plot()

            # Draw crosshair at the center of the video stream
            im_center_x = im.shape[1] // 2
            im_center_y = im.shape[0] // 2
            cv2.drawMarker(im, (im_center_x, im_center_y), (0, 0, 0), markerType=cv2.MARKER_CROSS, 
                           markerSize=20, thickness=2, line_type=cv2.LINE_AA)

            # Displaying the resulting video
            cv2.imshow("Camera", im)
            cv2.imshow("Mask", mask_red)

            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(f"Error: {e}")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_detection()
