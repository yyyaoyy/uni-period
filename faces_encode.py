# Import the necessory libraries and python packages that we will use here for our project.
import os
import cv2
import face_recognition
import numpy as np
import pickle
# Here is the path of folder where the face dataset is available. the faces should be in separate
#folders for separate persons with the name of folder being set as the name of person.
known_faces_path='known faces/'
# listing the input directory where there should be face folders for separate people in separate folders.
known_faces_folder = os.listdir(known_faces_path)
# Initializing the list in which we will store names of people in the dataset.
known_faces_names = []
# Initializing the list in which we will store encoded images of faces of people in the dataset.
known_faces_encoded = []
# Printing information to the user about the data being loading.
print("Loading known face image(s)")

# We apply loop to all the faces folders that are likely to be inside the directory of 'known_faces_path' specified above
for known_face in known_faces_folder:
    # To make sure that the name read is a folder and not a single file, we put a check of if there is no '.' in the folder name
    if not '.' in known_face:
        # Printing to the user about the faces images of particular person being encoded
        print('Encoding Faces of {}...'.format(known_face))
        # listing all the images inside the folder of a person's faces that is under encoding in current iteration.
        images_names = os.listdir(known_faces_path+known_face+'/')
        # the following lines will encode and save all the faces inside the folder of a particular person's faces
        for image_name in images_names:
            #loading a single image in the format that read by the face_recognition api.
            known_face_image = face_recognition.load_image_file(known_faces_path + known_face+'/'+image_name)
            # encoding the face that is loaded in preveous step using the face_recognition api.
            encoded_face = face_recognition.face_encodings(known_face_image)
            # The encoded face is append to the list of know encoded faces and hence it is stored by the machine.
            known_faces_encoded.append(encoded_face[0])
            #getting name of the person from the folder name that is read in the current loop.
            face_name = known_face
            # appending the name to the names of known persons and hence store it in the system.
            known_faces_names.append(face_name)
# After the execution of the above nested loop, each image in the dataset of input folder is now encoded and is stored in the form
#of encoded faces in the variable 'known_faces_encoded'

# The following line is creating a dictionary of the known faces encoded and known names and will store it in a data file in 'pickle' format and hence
#this will be able to read by the face recognizer to recognize face in realtime.
data = {"encodings": known_faces_encoded, "names": known_faces_names}

print('Encoding Done!')

# Making file to store the encoded faces data and names.
encoder_file = open('encoded_faces.pickle','wb')
# writing the data to the folder that is made, to save it for using with face recognizer.
encoder_file.write(pickle.dumps(data))
# closing the data file.
encoder_file.close()

# We have successfully encode the whole dataset and is stored in folder ready to be read by the face recognizer.
# So we will not need to do encoding every time we want face recognition. the encoding will be saved.
