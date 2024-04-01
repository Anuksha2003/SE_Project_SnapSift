# from flask import Flask, render_template, request
# import os
# import shutil
# import face_recognition
# from werkzeug.utils import secure_filename

# app = Flask(__name__)

# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Function to check if a person is detected in the group photo
# def is_person_detected_in_group_photo(group_photo_path, person_image_path):
#     group_image = face_recognition.load_image_file(group_photo_path)
#     person_image = face_recognition.load_image_file(person_image_path)
    
#     # Encode faces
#     group_encoding = face_recognition.face_encodings(group_image)
#     person_encoding = face_recognition.face_encodings(person_image)
    
#     # Compare face encodings
#     for encoding in group_encoding:
#         for person_encoding_single in person_encoding:
#             results = face_recognition.compare_faces([encoding], person_encoding_single)
#             if True in results:
#                 return True
#     return False

# # Function to copy group photo to folders of each person detected in the group photo
# def copy_group_photo_to_detected_person_folders(group_photo_path, individual_photos, original_filename):
#     for person in individual_photos:
#         person_name = person["name"]
#         person_image_path = person["path"]
        
#         # Check if the person is detected in the group photo
#         if is_person_detected_in_group_photo(group_photo_path, person_image_path):
#             person_dir = os.path.join(UPLOAD_FOLDER, person_name)
#             if not os.path.exists(person_dir):
#                 os.makedirs(person_dir)
#             shutil.copy(group_photo_path, os.path.join(person_dir, original_filename))

# # Route for uploading a group photo
# @app.route('/', methods=['GET', 'POST'])
# def upload_group_photo():
#     if request.method == 'POST':
#         # Check if the post request has the file part
#         if 'file' not in request.files:
#             return 'No file part'
#         file = request.files['file']
#         if file.filename == '':
#             return 'No selected file'
#         if file:
#             # Save the uploaded file with the original filename
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)

#             # Load individual photos
#             individual_photos = [
#                 {"name": "Virat Kohli", "path": "images/virat-kohli.jpeg"},
#                 {"name": "AB de Villiers", "path": "images/abd.jpeg"},
#                 {"name": "MS Dhoni", "path": "images/dhoni.jpeg"},
#                 {"name": "Rohit Sharma", "path": "images/rohit.jpeg"}
#             ]

#             # Copy group photo to folders of detected persons
#             copy_group_photo_to_detected_person_folders(file_path, individual_photos, filename)

#     return render_template('index.html')

# if __name__ == '__main__':
#     app.run(debug=True)

# -----------------------------------------------------------------folder->frontend+backend ----------------------------------
from flask import Flask, render_template, request
import os
import shutil
import face_recognition
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__, static_folder='static')

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.static_folder = 'static'
# Function to check if a person is detected in the group photo
def is_person_detected_in_group_photo(group_photo_path, person_image_path):
    group_image = face_recognition.load_image_file(group_photo_path)
    person_image = face_recognition.load_image_file(person_image_path)
    
    # Encode faces
    group_encoding = face_recognition.face_encodings(group_image)
    person_encoding = face_recognition.face_encodings(person_image)
    
    # Compare face encodings
    for encoding in group_encoding:
        for person_encoding_single in person_encoding:
            results = face_recognition.compare_faces([encoding], person_encoding_single)
            if True in results:
                return True
    return False

# Function to copy group photo to folders of each person detected in the group photo
def copy_group_photo_to_detected_person_folders(group_photo_path, individual_photos, original_filename):
    for person in individual_photos:
        person_name = person["name"]
        person_image_path = person["path"]
        
        # Check if the person is detected in the group photo
        if is_person_detected_in_group_photo(group_photo_path, person_image_path):
            person_dir = os.path.join(UPLOAD_FOLDER, person_name)
            if not os.path.exists(person_dir):
                os.makedirs(person_dir)
            shutil.copy(group_photo_path, os.path.join(person_dir, original_filename))

# Function to get the list of created folders along with their content
def get_folder_contents():
    folder_contents = {}
    for folder_name in os.listdir(UPLOAD_FOLDER):
        folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
        if os.path.isdir(folder_path):
            folder_contents[folder_name] = os.listdir(folder_path)
    return folder_contents

# Route for uploading a group photo
# Route for uploading a group photo
@app.route('/', methods=['GET', 'POST'])
def upload_group_photo():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            # Save the uploaded file with the original filename
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Load individual photos
            individual_photos = [
                {"name": "Virat Kohli", "path": "images/virat-kohli.jpeg"},
                {"name": "AB de Villiers", "path": "images/abd.jpeg"},
                {"name": "MS Dhoni", "path": "images/dhoni.jpeg"},
                {"name": "Rohit Sharma", "path": "images/rohit.jpeg"}
            ]

            # Copy group photo to folders of detected persons
            copy_group_photo_to_detected_person_folders(file_path, individual_photos, filename)

    # Get the list of created folders along with their content
    folder_contents = get_folder_contents()

    return render_template('index.html', folder_contents=folder_contents, UPLOAD_FOLDER=UPLOAD_FOLDER)

if __name__ == '__main__':
    app.run(debug=True)


# -----------------------------------------------------------------folder->frontend+backend ----------------------------------
