from __future__ import print_function
from threading import Thread
import threading
import numpy as np
import cv2
import sys
import datetime
import time
import Person
import math

personSize = 6000
persons = []
pid = 1
entered = 0
exited = 0


def draw_detections(img, rects, thickness=2):
    for x, y, w, h in rects:
        pad_w, pad_h = int(0.15*w), int(0.05*h)
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), thickness)


class WebcamVideoStream(object):
    def __init__(self):
        self.video = cv2.VideoCapture(
            'video2.mp4')
        self.w = self.video.get(3)  # CV_CAP_PROP_FRAME_WIDTH
        self.h = self.video.get(4)  # CV_CAP_PROP_FRAME_HEIGHT
        self.rangeLeft = int(1*(self.w/6))
        self.rangeRight = int(5*(self.w/6))
        self.midLine = int(2.5*(self.w/6))

        _, self.rawImage = self.video.read()
        self.firstFrame = cv2.cvtColor(self.rawImage, cv2.COLOR_BGR2GRAY)
        ret, jpeg = cv2.imencode('.jpg', self.rawImage)
        self.frameDetections = jpeg.tobytes()

        self.contours = []

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        self.face_cascade = cv2.CascadeClassifier(
            'haarcascade_frontalface_default.xml')

    def __del__(self):
        self.video.release()

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        # t2 = Thread(target=self.updateContours, args=())
        # t2.daemon = True
        # t2.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        count = 1
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.rawImage) = self.video.read()
            img = self.rawImage.copy()
            # draw rectangles around the people
            # draw_detections(img, self.contours)
            # visually show the counters
            # cv2.putText(img, "Entered: " + str(entered), (10, 20),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            # cv2.putText(img, "Exited: " + str(exited), (10, 50),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # img = self.find_people(img)
            self.find_faces(img)

            ret, jpeg = cv2.imencode('.jpg', img)
            self.frameDetections = jpeg.tobytes()

    def updateContours(self):
        # keep looping infinitely until the thread is stopped
        global personSize
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # get the current frame and look for people
            total = datetime.datetime.now()
            img = cv2.cvtColor(self.rawImage, cv2.COLOR_BGR2GRAY)
            total = datetime.datetime.now()
            frameDelta = cv2.absdiff(self.firstFrame, img)
            ret, thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)
            (_, allContours, _) = cv2.findContours(
                thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            personContours = []
            for c in allContours:
                # only look at contours larger than a certain size
                if cv2.contourArea(c) > personSize:
                    personContours.append(cv2.boundingRect(c))
            self.contours = personContours
            # track the people in the frame
            self.people_tracking(self.contours)

    def readDetections(self):
        # return the frame with people detections
        return self.frameDetections

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

    def inside(self, r, q):
        rx, ry, rw, rh = r
        qx, qy, qw, qh = q
        return rx > qx and ry > qy and rx + rw < qx + qw and ry + rh < qy + qh

    def find_faces(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

    def find_people(self, img):
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        if img is None:
            return None
        #  print('Failed to load image file:', fn)
        #  continue
        # except:
        #  print('loading error')
        #  continue

        found, w = hog.detectMultiScale(
            img, winStride=(10, 10), padding=(32, 32), scale=1.05)
        found_filtered = []
        for ri, r in enumerate(found):
            for qi, q in enumerate(found):
                if ri != qi and self.inside(r, q):
                    break
                else:
                    found_filtered.append(r)
                draw_detections(img, found)
                draw_detections(img, found_filtered, 3)
                print('%d (%d) found' % (len(found_filtered), len(found)))
        return img

    def people_tracking(self, rects):
        global pid
        global entered
        global exited
        for x, y, w, h in rects:
            new = True
            xCenter = x + w/2
            yCenter = y + h/2
            inActiveZone = xCenter in range(self.rangeLeft, self.rangeRight)
            for index, p in enumerate(persons):
                dist = math.sqrt((xCenter - p.getX())**2 +
                                 (yCenter - p.getY())**2)
                if dist <= w/2 and dist <= h/2:
                    if inActiveZone:
                        new = False
                        if p.getX() < self.midLine and xCenter >= self.midLine:
                            print("[INFO] person going left " + str(p.getId()))
                            entered += 1
                        if p.getX() > self.midLine and xCenter <= self.midLine:
                            print("[INFO] person going right " + str(p.getId()))
                            exited += 1
                        p.updateCoords(xCenter, yCenter)
                        break
                    else:
                        print("[INFO] person removed " + str(p.getId()))
                        persons.pop(index)
            if new == True and inActiveZone:
                print("[INFO] new person " + str(pid))
                p = Person.Person(pid, xCenter, yCenter)
                persons.append(p)
                pid += 1
