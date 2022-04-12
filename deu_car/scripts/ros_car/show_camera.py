#!/usr/bin/env python
import numpy

import rospy
from sensor_msgs.msg import Image
import cv2, cv_bridge
import sys


class ScanImage:
    def __init__(self):
        self.bridge = cv_bridge.CvBridge()
        self.image_sub = None
        self.image = None

    def direction_camera(self, direction):
        if direction == 'front':
            self.image_sub = rospy.Subscriber('camera/rgb/image_raw', Image, self.front_camera)
        elif direction == 'left':
            self.image_sub = rospy.Subscriber('my_left_camera/rgb/image_raw', Image, self.left_camera)
        elif direction == 'right':
            self.image_sub = rospy.Subscriber('my_right_camera/rgb/image_raw', Image, self.right_camera)
        else:
            print "No search camera"
            sys.exit()
        return self.image_sub, self.image

    def left_camera(self, msg):
        self.image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        cv2.imshow("L", self.image)
        cv2.waitKey(3)

    def right_camera(self, msg):
        self.image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        cv2.imshow("R", self.image)
        cv2.waitKey(3)

    def front_camera(self, msg):
        self.image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        cv2.imshow("M", self.image)
        cv2.waitKey(3)


rospy.init_node('scan_image')
scanner = ScanImage()
argv_len = len(sys.argv[1:])
for i in range(argv_len):
    scanner.direction_camera(sys.argv[i+1])
rospy.spin()
