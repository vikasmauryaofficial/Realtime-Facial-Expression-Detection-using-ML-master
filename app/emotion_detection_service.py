from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import cv2
import numpy as np
import os
import time
from orm import Image, DBSession

detection_model_path = '../haarcascade_files/haarcascade_frontalface_default.xml'
emotion_model_path = '../models/_mini_XCEPTION.102-0.66.hdf5'
face_detection = cv2.CascadeClassifier(detection_model_path)
EMOTIONS = ["angry" ,"disgust","scared", "happy", "sad", "surprised","neutral"]
emotion_classifier = load_model(emotion_model_path, compile=False)
cv2.namedWindow('face_emotion_detection')
camera = cv2.VideoCapture(0)
start_time = time.time()

DELAY_IN_SECONDS = 2

def save_image(frame, emotion, path=r'static\uploads'):
    if not os.path.exists(path):
        os.mkdir(path)
    save_path = os.path.join(path, f'{emotion}_{time.time()}.jpg')
    cv2.imwrite(save_path, frame)
    with open(os.path.join(path, 'emotion.txt'), 'a') as f:
        f.write(f'{emotion},{save_path},{time.time()}\n')

while True:
    status,frame = camera.read()
    if not status: continue
    # flip
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (300, 300))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detection.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)
    
    canvas = np.zeros((250, 300, 3), dtype="uint8")
    frameClone = frame.copy()
    if len(faces) > 0:
        faces = sorted(faces, reverse=True,
        key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
        (fX, fY, fW, fH) = faces
        roi = gray[fY:fY + fH, fX:fX + fW]
        roi = cv2.resize(roi, (64, 64))
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)
        preds = emotion_classifier.predict(roi)[0]
        emotion_probability = np.max(preds)
        label = EMOTIONS[preds.argmax()]
    else: continue
    for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds)):
        text = "{}: {:.2f}%".format(emotion, prob * 100)        
        w = int(prob * 300)
        cv2.rectangle(canvas, (7, (i * 35) + 5),(w, (i * 35) + 35), (0, 0, 255), -1)
        cv2.putText(canvas, text, (10, (i * 35) + 23),cv2.FONT_HERSHEY_SIMPLEX, 0.45,(255, 255, 255), 2)
        cv2.putText(frameClone, label, (fX, fY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
        cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH), (0, 0, 255), 2)
    # join canvas and frameClone
    canvas = cv2.resize(canvas, (300, 300))
    out = np.hstack((frameClone, canvas))
    cv2.imshow("face_emotion_detection", out)
    # save images and emotion few seconds to a folder
    if time.time() - start_time > DELAY_IN_SECONDS:
        save_image(frame, label)
        start_time = time.time()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
camera.release()
cv2.destroyAllWindows()
    
