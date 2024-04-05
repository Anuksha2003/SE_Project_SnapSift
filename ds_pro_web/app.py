from flask import Flask, render_template, request
import os
import shutil
import face_recognition
from werkzeug.utils import secure_filename
import mysql.connector

app = Flask(__name__, static_folder='static')

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL Configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Pm@035393',
    'database': 'se_pro'
}

# Function to establish a connection to MySQL
def get_mysql_connection():
    return mysql.connector.connect(**mysql_config)

# Function to create the table if not exists
def create_table():
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS uploaded_files
                     (id INT AUTO_INCREMENT PRIMARY KEY,
                      filename VARCHAR(255) NOT NULL,
                      uploader VARCHAR(255) NOT NULL,
                      upload_time DATETIME NOT NULL)''')
    conn.commit()
    conn.close()

# Function to insert uploaded file information into MySQL
def insert_uploaded_file(filename, uploader):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO uploaded_files (filename, uploader, upload_time) VALUES (%s, %s, NOW())", (filename, uploader))
    conn.commit()
    conn.close()

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
            person_dir = os.path.join(app.config['UPLOAD_FOLDER'], person_name)
            if not os.path.exists(person_dir):
                os.makedirs(person_dir)
            shutil.copy(group_photo_path, os.path.join(person_dir, original_filename))

# Function to get individual photos dynamically from the images folder
def get_individual_photos():
    individual_photos = []
    images_folder = 'images'  # Assuming your images folder is named 'images'

    for root, dirs, files in os.walk(images_folder):
        for filename in files:
            if filename.endswith('.jpeg') or filename.endswith('.jpg') or filename.endswith('.png'):
                name = os.path.splitext(filename)[0]  # Get the name without the file extension
                path = os.path.join(root, filename)
                individual_photos.append({"name": name, "path": path})

    return individual_photos

# Function to get the list of created folders along with their content
def get_folder_contents():
    folder_contents = {}
    for root, dirs, files in os.walk(UPLOAD_FOLDER):
        for folder_name in dirs:
            folder_path = os.path.join(root, folder_name)
            folder_contents[folder_name] = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return folder_contents

@app.route('/', methods=['GET', 'POST'])
def upload_group_photo():
    create_table()  # Ensure table exists
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

            # Insert uploaded file information into MySQL
            insert_uploaded_file(filename, "Uploader Name")

            # Load individual photos dynamically from the images folder
            individual_photos = get_individual_photos()

            # Copy group photo to folders of detected persons
            copy_group_photo_to_detected_person_folders(file_path, individual_photos, filename)

    # Get the list of created folders along with their content
    folder_contents = get_folder_contents()

    return render_template('index.html', folder_contents=folder_contents, UPLOAD_FOLDER=UPLOAD_FOLDER)

if __name__ == '__main__':
    app.run(debug=True)