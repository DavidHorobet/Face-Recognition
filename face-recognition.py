import face_recognition
import cv2
import numpy as np 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
import datetime
import pygame
import time as Time


#get current date
def get_current_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')
#get current time
def get_current_time():
    return datetime.datetime.now().strftime('%H:%M:%S')

cred = credentials.Certificate("/Users/davidhorobet/PhytonProjects/face-firebase/facerecognitionsystem-ceca6-firebase-adminsdk-z7cct-37fae0dd96.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'facerecognitionsystem-ceca6.appspot.com',
    'databaseURL' : 'https://facerecognitionsystem-ceca6-default-rtdb.firebaseio.com/'
})

ref = db.reference('attendance')

def write_to_database(date, current_time,nume,user_key):
    new_entry_ref = ref.push()  # Generate a unique key for the new document
    new_entry_ref.set({
        'name' : nume,
        'date': date,
        'recognition_time': current_time,
        'face_recognized': True,
        'user_id' : user_key
    })

bucket = storage.bucket()

# List all files in the bucketz
blobs = bucket.list_blobs()

# Iterate through each blob (file) in the bucket
known_face_encodings = []
known_face_names = []

# Process images directly from Cloud Storage
for blob in blobs:
    if blob.name.endswith('.jpg') or blob.name.endswith('.jpeg'):
        # Load image from Cloud Storage
        image_bytes = blob.download_as_bytes()
        image_np = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        # Generate face encoding
        face_encoding = face_recognition.face_encodings(image)[0]  # Assuming only one face per image
        known_face_encodings.append(face_encoding)

        # Extract name from the subfolder name
        name = blob.name.split('/')[-2]  # Get the parent folder name (subfolder name)
        known_face_names.append(name)



video_capture = cv2.VideoCapture(0)

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
last_frame_time = Time.time()
fps = 0

while True:

    ret, frame = video_capture.read()
    if not ret:
        print("Error reading frame from camera")
        break  # Break the loop if frame reading fails


    length = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
   # print( length ) 
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Only process every other frame of video to save time
    if process_this_frame:
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []

        all_face_encodings = np.array(known_face_encodings)  # Convert list to numpy array for comparison

        for face_encoding in face_encodings:
            # Compare face encoding with all known face encodings
            matches = face_recognition.compare_faces(all_face_encodings, face_encoding)
            name = "Unknown"
            NameRD = "Unknown"
            user_id = 'Unknown'
            # Find the index of the first match
            match_index = next((i for i, match in enumerate(matches) if match), None)
            if match_index is not None:
                # Find the corresponding name using the match index
                name = known_face_names[match_index]
            
                user_id = known_face_names[match_index]

            #get the user name from db based on his UserID    
            NameRD =  db.reference('users').child(user_id).get()
        
            if NameRD:
                NameRD = NameRD['name']
            else:
                None

            face_names.append(name)

    process_this_frame = not process_this_frame

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        employee_id = name
        date = get_current_date()
        time = get_current_time()
        IdentificationUserKey = user_id

        if name != 'Unknown':
            write_to_database(date,time,name,IdentificationUserKey)


        # current_time = Time.time()
        # elapsed_time = current_time - last_frame_time
        # if elapsed_time > 0:
        #         fps = 1 / elapsed_time
        #         last_frame_time = current_time

    # Overlay FPS on the frame
   # cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
