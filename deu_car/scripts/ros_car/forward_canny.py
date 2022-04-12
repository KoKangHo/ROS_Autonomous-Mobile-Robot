#!/usr/bin/env python

import rospy
import cv2, cv_bridge
import numpy as np
from sensor_msgs.msg import Image


class Forwardcanny:

    def __init__(self):
        self.bridge = cv_bridge.CvBridge()
        self.image_sub = rospy.Subscriber('camera/rgb/image_raw', Image, self.image_callback)
        self.lines = None
        self.slp = 1

    def image_callback(self, msg):
        cv2_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        hsv = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([0, 0, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)

        lanelines_image = mask.copy()
        edge = cv2.Canny(lanelines_image, 100, 200)

        h = edge.shape[0]
        w = edge.shape[1]

        vertices = np.array([[(w/3, h-(h/9)), (w/3, h-(h/9)-80), (w-(w/3), h-(h/9)-80), (w-(w/3), h-(h/9))]])

        image_mask = np.zeros_like(edge)
        if len(edge.shape) > 2:
            color = (255,255,255)
        else:
            color = 255

        cv2.fillPoly(image_mask, vertices, color)
        roi_conversion = cv2.bitwise_and(edge, image_mask)
        self.lines = cv2.HoughLinesP(roi_conversion, 1, np.pi / 180, 100, minLineLength=20, maxLineGap=5)
        forword_fit = []
        if self.lines is not None:
            for line in self.lines:
                x1, y1, x2, y2 = line.reshape(4)
                parameter = np.polyfit((x1, x2), (y1, y2), 1)
                slope = parameter[0]
                intercept = parameter[1]
                forword_fit.append((slope, intercept))
        else:
            pass
        forword_fit_average = np.average(forword_fit, axis=0)
        forword_fit_average = np.round(forword_fit_average, 4)

        try:
            slope, intercept = forword_fit_average
        except TypeError:
            slope = 1
        if slope == -0.0 or slope == 0.0:
            self.slp = 0
        else:
            self.slp = slope


if __name__ == '__main__':
    rospy.init_node('forcanny')
    detector = Forwardcanny()
    rospy.spin()