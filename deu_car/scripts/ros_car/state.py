#!/usr/bin/env python

import rospy
from smach import State
from drive_controller import RobotDriveController
from detect_blocking_bar import Find_Bar
from line_trace import Trace
from detect_stop_line import StopLineDetector
from detect_stop_sign import DetectStopSign
from detect_obstacle import DetectObstacle


class ReadyToStart(State):
    def __init__(self):
        State.__init__(self, outcomes=['success'])

    def execute(self, ud):
        rospy.loginfo("loading")
        rospy.sleep(rospy.Duration(1))
        return 'success'


class DetectedBlockingBar(State):
    def __init__(self):
        State.__init__(self, outcomes=['success'])
        self.detect_blocking_bar = Find_Bar()

    def execute(self, ud):
        rospy.loginfo("blocking bar is detect")
        while not self.detect_blocking_bar.detect:
            pass
        rospy.loginfo("blocking bar is open")
        current_time = int(rospy.Time.now().to_sec())
        target_time = current_time + 7
        while target_time > int(rospy.Time.now().to_sec()):
            self.detect_blocking_bar.drive()
        return 'success'


class LineTrace(State):
    def __init__(self):
        State.__init__(self, outcomes=['success', 'detect_stop_line', 'detect_stop_sign', 'detect_obstacle'])
        self.line_trace = Trace()
        self.sign = 0
        self.signBool = False

    def execute(self, ud):
        rospy.loginfo("line trace")
        detect_stop_line = StopLineDetector()
        detect_stop_sign = DetectStopSign()
        detect_obstacle = DetectObstacle()

        while True:
            self.line_trace.go_line()
            if detect_stop_line.detect:
                return 'detect_stop_line'
            elif detect_stop_sign.detect and self.sign == 0:
                self.line_trace.go_line()
                self.sign += 1
                return 'detect_stop_sign'
            elif not detect_obstacle.detect_obstacle and self.sign == 1:
                self.signBool = True
                return 'detect_obstacle'
            elif detect_stop_sign.detect and self.signBool:
                return 'success'


class DetectedStopLine(State):
    def __init__(self):
        State.__init__(self, outcomes=['success'])
        self.drive_controller = RobotDriveController()
        self.count = 0

    def execute(self, ud):
        rospy.loginfo("stop_line detect")
        detect_stop_line = StopLineDetector()
        self.count += 1
        current_time = int(rospy.Time.now().to_sec())
        target_time = current_time + 3
        while target_time > int(rospy.Time.now().to_sec()):
            detect_stop_line.stop_line()

        if self.count == 4 or self.count == 6:
            current_time = int(rospy.Time.now().to_sec())
            target_time = current_time + 5
            while target_time > int(rospy.Time.now().to_sec()):
                self.drive_controller.set_velocity(0.8)
                self.drive_controller.drive()
        elif self.count == 7:
            self.drive_controller.set_angular(0.4)
            self.drive_controller.drive()
        current_time = int(rospy.Time.now().to_sec())
        target_time = current_time + 1
        while target_time > int(rospy.Time.now().to_sec()):
            self.drive_controller.set_velocity(0.6)
            self.drive_controller.drive()

        return 'success'


class DetectedStopSign(State):
    def __init__(self):
        State.__init__(self, outcomes=['success'])
        self.drive_controller = RobotDriveController()

    def execute(self, ud):
        rospy.loginfo("stop_sign detect")
        self.drive_controller.set_angular(0)
        self.drive_controller.drive()
        rospy.sleep(3)
        return 'success'


class DetectedObstacle(State):
    def __init__(self):
        State.__init__(self, outcomes=['success'])
        self.drive_controller = RobotDriveController()
        self.detect_obstacle = DetectObstacle()

    def execute(self, ud):
        rospy.loginfo("obstacle detect")
        while True:
            self.detect_obstacle.drive()
            if self.detect_obstacle.detect_obstacle:
                return 'success'


class End(State):
    def __init__(self):
        State.__init__(self, outcomes=['success'])
        self.drive_controller = RobotDriveController()

    def execute(self, ud):
        rospy.loginfo("End Project")
        self.drive_controller.set_velocity(0)
        self.drive_controller.drive()
        return 'success'
