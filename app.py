import os
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

UPLOAD_FOLDER = os.path.basename('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def process_image(image_path):
    # Load image and convert to grayscale
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply bilateral filter to reduce noise while preserving edges
    gray_filtered = cv2.bilateralFilter(gray, 11, 17, 17)

    # Apply Canny edge detector to detect edges
    edged = cv2.Canny(gray_filtered, 30, 200)

    # Find contours in the edged image
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area and keep only the largest ones
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]

    # Initialize license plate contour and x, y coordinates
    lp_contour, min_x, min_y, max_x, max_y = None, np.inf, np.inf, -np.inf, -np.inf

    # Loop over contours and find the one with 4 points
    for contour in contours:
        # Approximate the contour to a polygon with 4 points
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)

        # If the polygon has 4 points, assume it is the license plate
        if len(approx) == 4:
            lp_contour = approx
            x, y, w, h = cv2.boundingRect(contour)
            min_x, min_y, max_x, max_y = min(min_x, x), min(min_y, y), max(max_x, x + w), max(max_y, y + h)
            break

    # If license plate contour is found, draw it on image and crop license plate
    if lp_contour is not None:
        cv2.drawContours(image, [lp_contour], -1, (0, 255, 0), 3)
        cropped_image = gray[min_y:max_y, min_x:max_x]
        cv2.imwrite('static/cropped_image.jpg', cropped_image)
        return True
    else:
        return False


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Check if image file was uploaded
        if 'image' not in request.files:
            return redirect(request.url)

        image = request.files['image']

        # Check if file name is not empty and is an image
        if image.filename != '' and image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            # Save image file to upload directory
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)

            # Process image and detect license plate
            if process_image(image_path):
                prediction_text = 'License plate detected!'
            else:
                prediction_text = 'License plate not found'

            # Delete image file from upload directory
            os.remove(image_path)

            # Render template with prediction results
            return render_template('index.html', prediction_text=prediction_text)
        else:
            return redirect(request.url)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
