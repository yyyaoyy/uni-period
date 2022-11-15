# Import the necessory libraries and python packages that we will use here for our project.
from __future__ import print_function

import pickle
import sys
from threading import Thread

import cv2
import face_recognition
import imutils

# loading the encoded faces data that has been generated and stored by the code 'faces_encode.py'.
# It will be used for comparison with faces in live camera feed.
try:
    data = pickle.loads(open('encoded_faces.pickle', 'rb').read())
except:
    data = pickle.loads(open('FR/encoded_faces.pickle', 'rb').read())
# Storing names list in separate variable and encoded faces into a separate variable.
known_faces_names = data['names']
known_faces_encoded = data['encodings']

# import the Queue class from Python 3
if sys.version_info >= (3, 0):
    pass
# otherwise, import the Queue class for Python 2.7
else:
    pass

class WebcamVideoStream:
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self
    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
    def read(self):
        # return the frame most recently read
        return self.frame
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
# Capturing the camera to be used for live feed.


def recognize(frame=None):
    print("FR Entered")
    is_detected = False

    # contenous loop
    while not is_detected:
        # Try to read the camera app, if the camera is up and running properly, it will successfully
        #read the frame, otherwise it will generate exception on which we have shown the message to
        #see camera connectivity in the next line of code. on the exception, the code will break execution.
        try:
            if __name__ == '__main__':
                ret,frame = cam.read()
            # frame = imutils.resize(frame, width=190, height = 150)
            frame = imutils.resize(frame)
        except:
            print('Please Check the Camera Connectivity and Enable it')
            break

        # The following command is just detecting faces in the input frame and storing its location if there exist faces.
        faces = face_recognition.face_locations(frame)
        # Just to put a rectangle on the faces in the frame we put a rectangle on each face by applying a loop on all faces detected.
        for face in faces:
            cv2.rectangle(frame,(face[3],face[0]),face[1:3],(100,200,0),2)

        name = 'Face Not Detected'
        # Apply check of if there are some faces. i.e. greater then zero faces. then we will go ahead to face recognisiton, otherwise will skip.
        if len(faces) > 0:
            # encoding all the facees appear in the frame and store them into faces_encode variable.
            faces_encode = face_recognition.face_encodings(frame, faces)
            # setting up face iteration to get the face id for rest of the code.
            face_itr = 0
            # applying loop to all the encoded faces that are encoded in the preveous step. this is to examing each detected face for recognition one by one.
            for face_encode in faces_encode:
                # compare and match the current encoded face to the faces that are stored in the dataset and we read them already as encoded faces.
                #if the current face is matched to any of the faces in the dataset, the match will generate True value for that face and hence this means
                #the person face is found in the dataset, so recognized as known face.
                match = face_recognition.compare_faces(known_faces_encoded, face_encode)
                # By default we say the person is unknown.
                name = 'Unknown Person'
                # See if the match gives true for any of the count in the encoded faces.
                if match.count(True) > 0:
                    # if the match has a Ture count, then it would have generated a index which will be the person
                    #whose name is on that particular indes as his face was in the encoded faces and hence the
                    #name is extracted from known names.
                    name = known_faces_names[match.index(True)]
                    #Printing that the person with name '_______' is detected
                    print("{} is detected!".format(name))
                    is_detected = True
                # Putting name of the persone above his face. it will be default name 'i.e. Unknown Person' if the person is not recognized, Not in the dataset
                cv2.putText(frame, name,(faces[face_itr][3],faces[face_itr][0]-15),cv2.FONT_HERSHEY_SIMPLEX,0.5,(100,200,0),1,cv2.LINE_AA)
                # Iterating the face number, as the face encoder is changing in the detected face.
                face_itr+=1
        if __name__ == '__main__':
            # Showing the camera feed on the screen.
            cv2.imshow('Frame',frame)
            # waiting for the 'esc' key, if the esc key is hit, the pregram will stop.
            k = cv2.waitKey(1) & 0xff
            if k == 27:
                cam.release()
                break
        else:
            return frame, name


    if __name__ == '__main__':
        # Releasing the camera and destroying all windows that were opened by the program.
        cam.release()
        cv2.destroyAllWindows()

    return frame, name

if __name__ == '__main__':
    cam = cv2.VideoCapture(0)
    recognize()