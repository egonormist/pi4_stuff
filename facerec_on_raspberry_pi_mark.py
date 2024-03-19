import RPi.GPIO as GPIO
import time
import face_recognition
import picamera
import numpy as np
from gtts import gTTS
import os
import pygame

GPIO.setmode(GPIO.BCM)
pin_number = 6
GPIO.setup(pin_number, GPIO.OUT)
buzzer_pin = pin_number
# Get a reference to the Raspberry Pi camera.
camera = picamera.PiCamera()
camera.resolution = (320, 240)
output = np.empty((240, 320, 3), dtype=np.uint8)

# Define texts for each recognized person
texts = {
    "Mark Ochieng": "Hello Mark",
    "Neville": "Hi Neville",
    "Glory": "Hello Glory",
    "Jane": "Hi Jane",
    "Ian": "Hello Ian"
}

# Initialize pygame mixer
pygame.mixer.init()

# Load speech files for each recognized person
speech_files = {}
for name, text in texts.items():
    tts = gTTS(text=text, lang='en', slow=True)
    file_name = f"{name.replace(' ', '_').lower()}.mp3"
    tts.save(file_name)
    speech_files[name] = file_name

# Load known face images and encodings
print("Loading known face image(s)")
mark_image = face_recognition.load_image_file("lol.jpg")
neville_image = face_recognition.load_image_file("obama_small.jpg")
glory_image = face_recognition.load_image_file("biden.jpg")
jane_image = face_recognition.load_image_file("alex-lacamoire.png")
ian_image = face_recognition.load_image_file("lin-manuel-miranda.png")

mark_face_encoding = face_recognition.face_encodings(mark_image)[0]
neville_face_encoding = face_recognition.face_encodings(neville_image)[0]
glory_face_encoding = face_recognition.face_encodings(glory_image)[0]
jane_face_encoding = face_recognition.face_encodings(jane_image)[0]
ian_face_encoding = face_recognition.face_encodings(ian_image)[0]

# Initialize some variables
face_locations = []
face_encodings = []

while True:
    print("Capturing image.")
    # Grab a single frame of video from the RPi camera as a numpy array
    camera.capture(output, format="rgb")

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(output)
    print("Found {} faces in image.".format(len(face_locations)))
    face_encodings = face_recognition.face_encodings(output, face_locations)

    # Loop over each face found in the frame to see if it's someone we know.
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        match_mark = face_recognition.compare_faces([mark_face_encoding], face_encoding)
        match_neville = face_recognition.compare_faces([neville_face_encoding], face_encoding)
        match_glory = face_recognition.compare_faces([glory_face_encoding], face_encoding)
        match_jane = face_recognition.compare_faces([jane_face_encoding], face_encoding)
        match_ian = face_recognition.compare_faces([ian_face_encoding], face_encoding)
        name = "<Unknown Person>"
        
        if not (match_mark[0] or match_neville[0] or match_glory[0] or match_jane[0] or match_ian[0]):
            name = "Unknown"
            # Beep the buzzer
            GPIO.output(buzzer_pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(buzzer_pin, GPIO.LOW)
            time.sleep(1)
            


        if match_mark[0]:
            name = "Mark Ochieng"
        elif match_neville[0]:
            name = "Neville"
        elif match_glory[0]:
            name = "Glory"
        elif match_jane[0]:
            name = "Jane"
        elif match_ian[0]:
            name = "Ian"
            
        print("Look! It's {}!".format(name))

        # If the person is recognized, play the corresponding speech
        if name in texts:
            file_name = speech_files[name]
            pygame.mixer.music.load(file_name)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
    #GPIO.cleanup()
