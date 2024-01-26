#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import time


# In[3]:


def capture_image():
    import time
    camera = cv2.VideoCapture(0)
    for i in range(5):
        return_value, image = camera.read()
        cv2.imwrite('src\\current_user_images\\opencv'+str(i)+'.png', image)
        time.sleep(2)
    del(camera)


# In[2]:


def convertToRGB(img): 
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


# In[3]:


#face detector 
#function to detect face using OpenCV
def detect_face(img):
    #convert the test image to gray scale as opencv face detector expects gray images
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
 
    #load OpenCV face detector, I am using LBP which is fast
    #there is also a more accurate but slow: Haar classifier
#     face_cascade = cv2.CascadeClassifier('opencv-files/lbpcascade_frontalface.xml')
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')

    #let's detect multiscale images(some images may be closer to camera than others)
    #result is a list of faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5);

    #if no faces are detected then return original img
    if (len(faces) == 0):
        return None, None
    
    #go over list of faces and draw them as rectangles on original colored
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    #convert image to RGB and show image
    plt.imshow(convertToRGB(img))

    #under the assumption that there will be only one face,
    #extract the face area
    (x, y, w, h) = faces[0]

    #return only the face part of the image
    return gray[y:y+w, x:x+h], faces[0]


# In[6]:


def prepare_training_data(data_folder_path):
    labels = []
    faces = []
#     print("hi")
    dirs = os.listdir(data_folder_path)
    print(dirs)
    #let's go through each directory and read images within it
    for dir_name in dirs:        
        #our subject directories start with letter 's' so
        #ignore any non-relevant directories if any
        if not dir_name.startswith("s"):
            continue
        print(f"Now in directory {dir_name}...")
        #extract label number of subject from dir_name
        #format of dir name = slabel
        #, so removing letter 's' from dir_name will give us label
        label = int(dir_name.replace("s", ""))

        #build path of directory containing images for current subject 
        #sample subject_dir_path = "training-data/s1"
        subject_dir_path = data_folder_path + "/" + dir_name

        #get the images names that are inside the given subject directory
        subject_images_names = os.listdir(subject_dir_path)
    #     print(subject_images_names)

        #go through each image name, read image, 
        #detect face and add face to list of faces
        for image_name in subject_images_names:
            
            #ignore system files like .DS_Store
            if image_name.startswith("."):
                continue
            print(f"Now on image {image_name}...")
            #build image path
            #sample image path = training-data/s1/1.pgm
            image_path = subject_dir_path + "/" + image_name

            #read image
            image = cv2.imread(image_path)

            #display an image window to show the image 
            cv2.imshow("Training on image...", image)
            cv2.waitKey(100)

            #detect face
            face, rect = detect_face(image)

            #for the purpose of this tutorial
            #we will ignore faces that are not detected
            if face is not None:
            #add face to list of faces
                faces.append(face)
                #add label for this face
                labels.append(label)

                cv2.destroyAllWindows()
                cv2.waitKey(1)
                cv2.destroyAllWindows()
            else:
                print("Face not found!!")

    return faces, labels


# In[ ]:


def train_model(faces, labels):
    #create our LBPH face recognizer 
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.train(faces, np.array(labels))
    return face_recognizer


# In[6]:


def draw_rectangle(img, rect):
    (x, y, w, h) = rect
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)


# In[7]:


#function to draw text on give image starting from
#passed (x, y) coordinates. 
def draw_text(img, text, x, y):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)


# In[7]:


#this function recognizes the person in image passed
#and draws a rectangle around detected face with name of the 
#subject
def predict(test_img, face_recognizer, subjects):
    #make a copy of the image as we don't want to change original image
    img = test_img.copy()
    #detect face from the image
    face, rect = detect_face(img)

    #predict the image using our face recognizer 
    label, conf = face_recognizer.predict(face)
    print("label:", label)
    print("conf: ", conf)
    
    #get name of respective label returned by face recognizer
    if(conf < 65):
        label_text = subjects[label] ###
    else:
        label_text = "Unknown Person"

    #draw a rectangle around face detected
    draw_rectangle(img, rect)
    #draw name of predicted person
    draw_text(img, label_text, rect[0], rect[1]-5)

    return img, label_text, label


# In[5]:


# def __main__():
#     print("Preparing data...")
#     faces, labels = prepare_training_data("./captured_images")
#     print("Data prepared")

#     #print total faces and labels
#     print("Total faces: ", len(faces))
#     print("Total labels: ", len(labels))


# In[ ]:




