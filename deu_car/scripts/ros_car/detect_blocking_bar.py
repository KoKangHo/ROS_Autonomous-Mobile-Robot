#!/usr/bin/env python

import cv2
import numpy
import cv_bridge
import rospy
from sensor_msgs.msg import Image
from drive_controller import RobotDriveController


class Find_Bar:

    def __init__(self):
        self.bridge = cv_bridge.CvBridge()
        self.rate = rospy.Rate(20)
        self.image_sub = rospy.Subscriber('camera/rgb/image_raw', Image, self.image_callback)
        self.drive_controller = RobotDriveController()
        self.detect = False

    def image_callback(self, msg):
        image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_red = numpy.array([0, 30, 30])
        upper_red = numpy.array([10, 255, 130])
        gray = cv2.inRange(hsv, lower_red, upper_red)
        h, w = gray.shape
        search_top = 1
        search_bot = 3 * h / 4
        gray[0:search_top, 0:w] = 0
        gray[search_bot:h, 0:w] = 0
        gray[0:h, 0:250] = 0

        M = cv2.moments(gray)
        if M['m00'] > 0:
            self.detect = False
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cv2.circle(image, (cx, cy), 10, (255, 0, 0), -1)
        else:
            self.detect = True

    def drive(self):
        if self.detect:
            self.drive_controller.set_velocity(1)
        else:
            self.drive_controller.set_velocity(0)
        self.drive_controller.drive()


if __name__ == '__main__':
    rospy.init_node('test_node')
    detecter = Find_Bar()
    while not rospy.is_shutdown():
        detecter.drive()
        detecter.rate.sleep()
