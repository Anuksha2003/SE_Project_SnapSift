import os
import cv2
import face_recognition
import shutil

# Function to process individual photos and update group photo in respective folders
def process_individual_photo(person, group_encodings):
    img = cv2.imread(person["path"])
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encoding = face_recognition.face_encodings(rgb_img)[0]

    for group_encoding in group_encodings:
        result = face_recognition.compare_faces([group_encoding], encoding)
        if result[0]:
            print("Name:", person["name"])

            # Create a folder for each person if not exists
            person_dir = os.path.join(output_dir, person["name"])
            if not os.path.exists(person_dir):
                os.makedirs(person_dir)

            # Save the group photo in the person's folder
            group_photo_output_path = os.path.join(person_dir, "virat.jpeg")
            cv2.imwrite(group_photo_output_path, group_img)
            print(f"Stored group photo in {person['name']}'s folder")

# Create a directory to store individual photos if not exists
output_dir = "output_faces"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load and encode the group photo
group_img = cv2.imread("virat.jpeg")
rgb_group_img = cv2.cvtColor(group_img, cv2.COLOR_BGR2RGB)
group_encodings = face_recognition.face_encodings(rgb_group_img)

# Load and encode individual photos
individual_photos = [
    {"name": "Virat Kohli", "path": "images/virat-kohli.jpeg"},
    {"name": "AB de Villiers", "path": "images/abd.jpeg"},
    {"name": "MS Dhoni", "path": "images/dhoni.jpeg"},
    {"name": "Rohit Sharma", "path": "images/rohit.jpeg"}
]

# Process individual photos and update group photo in respective folders
for person in individual_photos:
    process_individual_photo(person, group_encodings)

