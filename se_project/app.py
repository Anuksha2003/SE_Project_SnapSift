import os
from flask import Flask, render_template, request, redirect, send_file
import shutil
import face_recognition
from PIL import Image
from werkzeug.utils import secure_filename
from typing import List, Tuple

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
            file_count = len([name for name in os.listdir("collection") if os.path.isdir(os.path.join("collection", name))])

            new_face_folder = os.path.join(output_folder, f"face_{file_count+1}")
            os.makedirs(new_face_folder)
            
            face_image = Image.fromarray(image[top:bottom, left:right])
            
            
            face_image.save(os.path.join(new_face_folder, "seed.jpg"))
            shutil.copy(input_image_path, os.path.join(new_face_folder, filename))
            print(f"New face {file_count+1} detected. Folder created.")


def find_multiples(number : int):
    multiples = set()
    for i in range(number - 1, 1, -1):
        mod = number % i
        if mod == 0:
            tup = (i, int(number / i))
            if tup not in multiples and (tup[1], tup[0]) not in multiples:
                multiples.add(tup)
                
    if len(multiples) == 0:
        mod == number % 2
        div = number // 2
        multiples.add((2, div + mod))
        
    return list(multiples)

def get_smallest_multiples(number : int, smallest_first = True) -> Tuple[int, int]:
    multiples = find_multiples(number)
    smallest_sum = number
    index = 0
    for i, m in enumerate(multiples):
        sum = m[0] + m[1]
        if sum < smallest_sum:
            smallest_sum = sum
            index = i
            
    result = list(multiples[i])
    if smallest_first:
        result.sort()
        
    return result[0], result[1]
    

def create_collage(listofimages : List[str], n_cols : int = 0, n_rows: int = 0, 
                   thumbnail_scale : float = 1.0, thumbnail_width : int = 0, thumbnail_height : int = 0):
    
    n_cols = n_cols if n_cols >= 0 else abs(n_cols)
    n_rows = n_rows if n_rows >= 0 else abs(n_rows)
    
    if n_cols == 0 and n_rows != 0:
        n_cols = len(listofimages) // n_rows
        
    if n_rows == 0 and n_cols != 0:
        n_rows = len(listofimages) // n_cols
        
    if n_rows == 0 and n_cols == 0:
        n_cols, n_rows = get_smallest_multiples(len(listofimages))
    
    thumbnail_width = 0 if thumbnail_width == 0 or n_cols == 0 else round(thumbnail_width / n_cols)
    thumbnail_height = 0 if thumbnail_height == 0 or n_rows == 0 else round(thumbnail_height/n_rows)
    
    all_thumbnails : List[Image.Image] = []
    for p in listofimages:
        thumbnail = Image.open(p)
        if thumbnail_width * thumbnail_scale < thumbnail.width:
            thumbnail_width = round(thumbnail.width * thumbnail_scale)
        if thumbnail_height * thumbnail_scale < thumbnail.height:
            thumbnail_height = round(thumbnail.height * thumbnail_scale)
        
        thumbnail.thumbnail((thumbnail_width, thumbnail_height))
        all_thumbnails.append(thumbnail)

    new_im = Image.new('RGB', (thumbnail_width * n_cols, thumbnail_height * n_rows), 'white')
    
    i, x, y = 0, 0, 0
    for col in range(n_cols):
        for row in range(n_rows):
            if i > len(all_thumbnails) - 1:
                continue
            
            print(i, x, y)
            new_im.paste(all_thumbnails[i], (x, y))
           


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

@app.route('/rename', methods=['GET'])
def rename_folder():
    old_name = request.args.get('old_name')
    new_name = request.args.get('new_name')
    old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_name)
    new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
    os.rename(old_path, new_path)
    return redirect('/')

@app.route('/create-collage', methods=['GET'])
def create_collage_endpoint():
    folder_name = request.form.get('folder_name')
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    list_of_images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    print(list_of_images)
    create_collage(list_of_images)
    collage_path = os.path.join(folder_path, 'Collage.jpg')  # Change the extension if necessary
    return send_file(collage_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
