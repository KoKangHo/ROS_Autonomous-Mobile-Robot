#!/usr/bin/env python

import rospy
import cv2, cv_bridge
import numpy as np
from sensor_msgs.msg import Image


class Leftcanny:

    def __init__(self):
        self.bridge = cv_bridge.CvBridge()
        self.image_sub = rospy.Subscriber('my_left_camera/rgb/image_raw', Image, self.image_callback)
        self.lines = None

    def image_callback(self, msg):
        cv2_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        lanelines_image = cv2_img.copy()
        edge = cv2.Canny(lanelines_image, 100, 200)

        image_height = edge.shape[0]
        image_width = edge.shape[1]

        vertices = np.array([[(0, image_height),
                              (0, image_height/2+30),
                              (image_width-image_width/3, image_height/2-55),
                              (image_width-image_width/3, image_height)]])

        image_mask = np.zeros_like(edge)
        if len(edge.shape) > 2:
            color = (255, 255, 255) # white color
        else:
            color = 255

        cv2.fillPoly(image_mask, vertices, color)
        roi_conversion = cv2.bitwise_and(edge, image_mask)

        self.lines = cv2.HoughLinesP(roi_conversion, 1, np.pi / 180, 100, minLineLength=40, maxLineGap=5)
        left_fit = []
        if self.lines is not None:
            for line in self.lines:
                x1, y1, x2, y2 = line.reshape(4)
                parameter = np.polyfit((x1, x2), (y1, y2), 1)
                slope = parameter[0]
                intercept = parameter[1]
                if slope < 0:
                    left_fit.append((slope, intercept))
        else:
            pass
        left_fit_average = np.average(left_fit, axis=0)
        left_fit_average = np.round(left_fit_average, 8)

        try:
            slope, intercept = left_fit_average
        except TypeError:
            slope, intercept = 0, 0

        if slope == 0:
            slope = -0.4

        y1 = lanelines_image.shape[0]
        y2 = int(y1 * (3 / 5))
        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)

        lines_image = np.zeros_like(lanelines_image)
        if self.lines is not None:
            cv2.line(lines_image, (x1, y1), (x2, y2), (255, 0, 0), 10)


if __name__ == '__main__':
    rospy.init_node('follower_left')
    detector = Leftcanny()
    rospy.spin()
