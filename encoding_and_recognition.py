import numpy as np
import cv2
import face_recognition
import imutils
import os
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cam = cv2.VideoCapture(0)



# Fetch the service account key JSON file contents
cred = credentials.Certificate("credentials.json")

# Initialize the app with a service account, granting admin privileges
app = firebase_admin.initialize_app(cred, {
    'storageBucket': '<BUCKET_NAME>.appspot.com',
}, name='storage')

bucket = storage.bucket(app=app)
blob = bucket.blob("<gs://watchdog-1bea5.appspot.com/NAIF.JPG>")

print(blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET'))





known_faces_path='gs://watchdog-1bea5.appspot.com/'
known_faces_folder = os.listdir(known_faces_path)

known_faces_names = []
known_faces_encoded = []

print("Loading known face image(s)")


for known_face in known_faces_folder:
    if not '.' in known_face:
        print('Encoding Faces of {}...'.format(known_face))
        images_names = os.listdir(known_faces_path+known_face+'/')
        for image_name in images_names:
            known_face_image = face_recognition.load_image_file(known_faces_path + known_face+'/'+image_name)
            encoded_face = face_recognition.face_encodings(known_face_image)
            known_faces_encoded.append(encoded_face[0])
            face_name = known_face
            known_faces_names.append(face_name)


while True:
    try:
        ret,frame = cam.read()
    except:
        print('Please Check the Camera Connectivity and Enable it')
        break
    faces = face_recognition.face_locations(frame)
    for face in faces:
        cv2.rectangle(frame,(face[3],face[0]),face[1:3],(100,200,0),2)
    
    if len(faces) > 0:
        faces_encode = face_recognition.face_encodings(frame, faces)
        face_itr = 0
        for face_encode in faces_encode:
            match = face_recognition.compare_faces(known_faces_encoded, face_encode)
            name = 'Unknown Person'
            if match.count(True) > 0:
                name = known_faces_names[match.index(True)]
                print("{} is detected!".format(name))
            cv2.putText(frame, name,(faces[face_itr][3],faces[face_itr][0]-15),cv2.FONT_HERSHEY_SIMPLEX,0.5,(100,200,0),1,cv2.LINE_AA)
            face_itr+=1
    cv2.imshow('Frame',frame)
    
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        cam.release()
        break

cam.release()
cv2.destroyAllWindows()
