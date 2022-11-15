'''
mobilemws108@gmail.com



Password    @Nn123456

firebase account for project

'''
from datetime import  datetime
from random import randint

from firebase import firebase
import pyrebase
import cv2
import os
sep = os.sep

firebase_app = firebase.FirebaseApplication('https://watchdog-1bea5.firebaseio.com/', None)
config = {
    "apiKey": "AIzaSyAqw2t0b0uWncKwUGZfRihPzWrUzz855sk",
    "authDomain": "watchdog-1bea5.firebaseapp.com",
    "databaseURL": "watchdog-1bea5.firebaseio.com",
    "porjectId": "watchdog-1bea5",
    "storageBucket": "watchdog-1bea5.appspot.com",
}

pyrebase_init = pyrebase.initialize_app(config)
storage_var = pyrebase_init.storage()

def update_metadata_firebase(img_path_local, person_id):

    img_path_cloud = "images/"  + img_path_local.split(sep)[-1]
    storage_result = storage_var.child(img_path_cloud).put(img_path_local)
    # print(storage_result)

    timestamp = datetime.now().isoformat()
    member = {'timestamp': timestamp,
              'id': person_id,
              'room_num': str(randint(1, 20)),
              'picture': storage_result['name']
              }
    result = firebase_app.post('/member/', member)

if __name__ == '__main__':
    # vs = cv2.VideoCapture(0)
    #
    # _, frame = vs.read()
    #
    # img_path_local=r'output'+ sep + 'images' + sep +'test_1'+'.png'
    # print(img_path_local)
    # cv2.imwrite(img_path_local, frame)
    # id = 'Name Detected Person'
    #
    # update_metadata_firebase(img_path_local, id)

    from time import  time
    print()