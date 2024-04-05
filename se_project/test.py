from flask import Flask, render_template, request
import os
import face_recognition
from werkzeug.utils import secure_filename
from PIL import Image

def crop_faces_and_save(input_image_path, output_folder):
    # Load image
    image = face_recognition.load_image_file(input_image_path)
    
    # Find face locations
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    # Iterate through detected faces
    for i, (face_location, face_encoding) in enumerate(zip(face_locations, face_encodings)):
        # Get face coordinates
        top, right, bottom, left = face_location
        
        # Create face encoding folder name
        face_encoding_folder = os.path.join(output_folder, f"face_encoding_{i+1}")
        
         # Create folder for the new face
        new_face_folder = os.path.join(output_folder, f"face_{i+1}")
        os.makedirs(new_face_folder)
            
            # Crop face from the image
        face_image = Image.fromarray(image[top:bottom, left:right])
            
            # Save cropped face as "seed.jpg" in the new face folder
        face_image.save(os.path.join(new_face_folder, "seed.jpg"))
        print(f"New face {i+1} detected. Folder created.")
    

    existing_face_image_1 = face_recognition.load_image_file(os.path.join("./collection/face_1", "seed.jpg"))
    existing_face_encoding_1 = face_recognition.face_encodings(existing_face_image_1)[0] 

    existing_face_image_2 = face_recognition.load_image_file(os.path.join("./collection/face_2", "seed.jpg"))
    existing_face_encoding_2 = face_recognition.face_encodings(existing_face_image_2)[0]
       
    if face_recognition.compare_faces([existing_face_encoding_1],existing_face_encoding_2)[0]:
        print("True")
    else:
        print("false")
crop_faces_and_save("./static/virat_dhoni_rohit.jpeg","collection")