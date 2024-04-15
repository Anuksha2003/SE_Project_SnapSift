import os
from flask import Flask, render_template, request, redirect, send_file, request, jsonify
import shutil
import face_recognition
from PIL import Image
from werkzeug.utils import secure_filename
from typing import List, Tuple

app = Flask(__name__, static_folder='./static')

UPLOAD_FOLDER = './static/collection'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_folder_contents():
    folder_contents = {}
    for root, dirs, files in os.walk("./static/collection"):
        for folder_name in dirs:
            folder_path = os.path.join(root, folder_name)
            folder_contents[folder_name] = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f != 'seed.jpg']
            # print(folder_contents)
            
    return folder_contents

def get_uploaded_images():
    """Retrieve the list of uploaded images."""
    uploaded_images = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith(('.jpg', '.png', '.jpeg')):
            uploaded_images.append(filename)
    return uploaded_images

def get_label_contents():
    folder_contents = {}
    for root, dirs, files in os.walk("./static/labels"):
        for folder_name in dirs:
            folder_path = os.path.join(root, folder_name)
            folder_contents[folder_name] = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f != 'seed.jpg']
            print(folder_contents)
            
    return folder_contents

def crop_faces_and_save(input_image_path, output_folder, filename):
    image = face_recognition.load_image_file(input_image_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    for i, (face_location, face_encoding) in enumerate(zip(face_locations, face_encodings)):
        top, right, bottom, left = face_location
        
        match_found = False
        
        for folder in os.listdir(output_folder):
            folder_path = os.path.join(output_folder, folder)
            if os.path.isdir(folder_path) and os.path.exists(os.path.join(folder_path, "seed.jpg")):
                
                existing_face_image = face_recognition.load_image_file(os.path.join(folder_path, "seed.jpg"))
                face_encodings = face_recognition.face_encodings(existing_face_image)
                if face_encodings:
                    existing_face_encoding = face_encodings[0]
                else:
                    continue
                
                if face_recognition.compare_faces([existing_face_encoding], face_encoding)[0]:
                    shutil.copy(input_image_path, os.path.join(folder_path, filename))
                    match_found = True
                    break
        
        if match_found:
            print(f"Face {i+1} matches an existing face. Skipping...")

        else:
            file_count = len([name for name in os.listdir("./static/collection") if os.path.isdir(os.path.join("collection", name))])

            new_face_folder = os.path.join(output_folder, f"face_{file_count+1}")
            os.makedirs(new_face_folder)
            
            face_image = Image.fromarray(image[top:bottom, left:right])
            
            
            face_image.save(os.path.join(new_face_folder, "seed.jpg"))
            shutil.copy(input_image_path, os.path.join(new_face_folder, filename))
            print(f"New face {file_count+1} detected. Folder created.")



@app.route('/', methods=['GET', 'POST'])
def upload_group_photo():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            crop_faces_and_save(file_path, "./static/collection",filename)

    folder_contents = get_folder_contents()
    label_contents = get_label_contents()
    uploaded_images = get_uploaded_images()
    # return render_template('index.html', folder_contents=folder_contents, UPLOAD_FOLDER=UPLOAD_FOLDER)
    return render_template('index.html', folder_contents=folder_contents, label_contents=label_contents,uploaded_images=uploaded_images, UPLOAD_FOLDER=UPLOAD_FOLDER)


@app.route('/rename', methods=['GET'])
def rename_folder():
    old_name = request.args.get('old_name')
    new_name = request.args.get('new_name')
    old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_name)
    new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
    os.rename(old_path, new_path)
    return redirect('/')

# @app.route('/create-collage', methods=['GET'])
# def create_collage_endpoint():
#     folder_name = request.form.get('folder_name')
#     folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
#     list_of_images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
#     print(list_of_images)
#     create_collage(list_of_images)
#     collage_path = os.path.join(folder_path, 'Collage.jpg')  # Change the extension if necessary
#     return send_file(collage_path, as_attachment=True)

@app.route('/submit-label', methods=['POST'])
def submit_label():
    if request.method == 'POST':
        data = request.get_json()
        folder_name = data.get('folderName')
        image_url = data.get('imageUrl')
        label = data.get('label')

        # Print the received label and image URL
        print(f"Received label '{label}' for image '{image_url}' in folder '{folder_name}'")

        # You can further process or use this data as needed
        process_label(folder_name, image_url, label)

        return jsonify({'message': 'Label submitted successfully'}), 200
    else:
        return jsonify({'error': 'Method not allowed'}), 405

def process_label(folder_name, image_url, label):
    labels_directory = './static/labels'

    if not os.path.exists(labels_directory):
        os.makedirs(labels_directory)

    # Check if the label directory exists within the labels directory
    label_directory = os.path.join(labels_directory, label)
    if not os.path.exists(label_directory):
        # If the label directory doesn't exist, create it
        os.makedirs(label_directory)

    try:
        # Extract the image file name from the image URL
        image_filename = "./static/collection/" + folder_name + "/" + image_url

        # Copy the image to the label directory
        shutil.copy(image_filename, label_directory)

        print(f"Image '{image_filename}' copied to '{label}' folder.")
    except Exception as e:
        print(f"Error copying image to label folder: {str(e)}")

    

if __name__ == '__main__':
    app.run(debug=True)
