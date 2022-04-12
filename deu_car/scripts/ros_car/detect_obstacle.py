#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
from drive_controller import RobotDriveController


class DetectObstacle:

    def __init__(self):
        self.detect_obstacle_pub = rospy.Publisher('obstacle_pub', Bool, queue_size=1)
        self.scan_sub = rospy.Subscriber('scan', LaserScan, self.scan_callback)
        self.cmd_vel_pub = rospy.Publisher('cmd_vel_mux/input/teleop', Twist, queue_size=1)
        self.twist = Twist()
        self.drive_controller = RobotDriveController()
        self.detect_obstacle = True

    def scan_callback(self, msg):
        if 0 < msg.ranges[180] < 1:
            self.detect_obstacle = False
        else:
            self.detect_obstacle = True

    def drive(self):
        if self.detect_obstacle:
            self.drive_controller.set_velocity(1)
        else:
            self.drive_controller.set_velocity(0)
        self.drive_controller.drive()


if __name__ == '__main__':
    rospy.init_node('test_node')
    detecter = DetectObstacle()
    while not rospy.is_shutdown():
        detecter.drive()
        rate = rospy.Rate(20)
        rate.sleep()
