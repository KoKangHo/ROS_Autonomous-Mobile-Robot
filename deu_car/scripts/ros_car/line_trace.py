#!/usr/bin/env python

import rospy

from drive_controller import RobotDriveController
from right_canny import Rightcanny
from left_canny import Leftcanny


class Trace:
    def __init__(self):
        self.right = Rightcanny()
        self.left = Leftcanny()
        self.drive_controller = RobotDriveController()
        self.rate = rospy.Rate(20)

    def go_line(self):
        if self.right.lines is None and self.left.lines is None:
            self.drive_controller.set_velocity(0.3)
            self.drive_controller.set_angular(0)
        elif self.right.lines is None:
            self.drive_controller.set_angular(-1)
            self.drive_controller.set_velocity(0.5)
        elif self.left.lines is None:
            self.drive_controller.set_angular(1)
            self.drive_controller.set_velocity(0.5)
        else:
            self.drive_controller.set_velocity(0.8)
            self.drive_controller.set_angular(0)
        self.drive_controller.drive()


if __name__ == '__main__':
    rospy.init_node('Tracer')
    line = Trace()
    while not rospy.is_shutdown():
        line.go_line()
        line.rate.sleep()
