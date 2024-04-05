from flask import Flask, render_template, request, redirect
import os
import shutil
import face_recognition
from werkzeug.utils import secure_filename
# import mysql.connector
from PIL import Image


app = Flask(__name__, static_folder='./collection')

UPLOAD_FOLDER = './collection'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_folder_contents():
    folder_contents = {}
    for root, dirs, files in os.walk("collection"):
        for folder_name in dirs:
            folder_path = os.path.join(root, folder_name)
            folder_contents[folder_name] = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return folder_contents



@app.route('/rename', methods=['GET'])
def rename_folder():
    old_name = request.args.get('old_name')
    new_name = request.args.get('new_name')
    old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_name)
    new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
    os.rename(old_path, new_path)
    return redirect('/')


def crop_faces_and_save(input_image_path, output_folder,filename):
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
            # file_count = 0

            # for _, _, files in os.walk("collection"):
            #     file_count += len(files)
            file_count = len([name for name in os.listdir("collection") if os.path.isdir(os.path.join("collection", name))])

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


            crop_faces_and_save(file_path, "collection",filename)


    folder_contents = get_folder_contents()

    return render_template('index.html', folder_contents=folder_contents, UPLOAD_FOLDER=UPLOAD_FOLDER)

if __name__ == '__main__':
    app.run(debug=True)