#!/usr/bin/env python

import rospy
import cv2, cv_bridge
import numpy

from sensor_msgs.msg import Image
from drive_controller import RobotDriveController
from forward_canny import Forwardcanny


class StopLineDetector:
    def __init__(self):
        self.bridge = cv_bridge.CvBridge()
        self.image_sub = rospy.Subscriber('camera/rgb/image_raw', Image, self.image_callback)
        self.drive_controller = RobotDriveController()
        self.forward = Forwardcanny()
        self.detect = False
        self.counter = 0
        self.area = 0

    def image_callback(self, msg):
        image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_white = numpy.array([0, 0, 190])
        upper_white = numpy.array([0, 0, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)

        h, w = mask.shape

        mask[0: h - (h / 4), 0: w] = 0
        mask[0:h, 0:w / 3] = 0
        mask[0:h, w - (w / 3):w] = 0

        ret, thr = cv2.threshold(mask, 0, 255, 0)
        _, contours, _ = cv2.findContours(thr, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            if len(contours) <= 0:
                return  # not found
            self.area = max(list(map(lambda x: cv2.contourArea(x), contours)))
            if self.area > 7350:
                self.detect = True

    def stop_line(self):
        if (self.forward.lines is not None) and (self.forward.slp != 1):
            self.drive_controller.set_velocity(0)
            self.drive_controller.drive()
            if self.forward.slp == 0:
                self.drive_controller.set_angular(0)
            elif self.forward.slp > 0:
                self.drive_controller.set_angular(-0.3)
            elif self.forward.slp < 0:
                self.drive_controller.set_angular(0.3)
            else:
                pass
            self.drive_controller.drive()
        self.detect = False


if __name__ == '__main__':
    rospy.init_node('stop_line_finder')
    detect_stop_line = StopLineDetector()
    rospy.spin()
