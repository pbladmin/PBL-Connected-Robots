from argparse import ArgumentParser
from time import sleep
import math
import socket
import threading
import signal

from frankx import Robot, RobotMode, Affine, MotionData, Reaction, Measure, JointMotion, ImpedanceMotion, StopMotion, PathMotion, LinearMotion, WaypointMotion, Waypoint, LinearRelativeMotion

exit_event = threading.Event()

M_PI = math.pi
M_PI_2 = math.pi / 2
M_PI_4 = math.pi / 4

max_dynamic_rel = 0.4

def get_own_ip(robot_ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((robot_ip, 80))
    robotnet_ip = s.getsockname()[0]
    s.close()
    return robotnet_ip

def robot_run_give():
    print("###robot_run_give()###")
    ret = True
    is_grasp = False

    if robot.read_once().robot_mode == RobotMode.Reflex:
        print("recover_from_errors")
        robot.recover_from_errors()
        sleep(2.0)

    #print(robot.read_once().q)

    if robot.read_once().robot_mode != RobotMode.Idle:
        print("RobotMode.Idle expected - Exit...")
        return

    home_q = [0.0, -M_PI_4, 0.0, -3 * M_PI_4, 0.0, M_PI_2, M_PI_4]
    handover_q = [1.5432607582535658, -0.053226991340547036, 0.056920426644254146, -1.628625931605958, -0.013094867636109639, 1.6329807602940412, 0.7914883640236048]
    
    if ret and not exit_event.is_set():
            print("jointmotion @ home")
            robot.set_dynamic_rel(max_dynamic_rel)
            ret = robot.move(JointMotion(home_q))

    if ret and not exit_event.is_set():
        print("open @ home")
        print("...in 3s")
        sleep(1.0)
        print("...in 2s")
        sleep(1.0)
        print("...in 1s")
        sleep(1.0)
        gripper.open()

    if not ret: return
    
    while not exit_event.is_set():
        ret = True

        if robot.read_once().robot_mode == RobotMode.Reflex:
            print("recover_from_errors")
            robot.recover_from_errors()
            sleep(2.0)

        if ret and not exit_event.is_set():
            print("jointmotion @ home")
            robot.set_dynamic_rel(max_dynamic_rel)
            ret = robot.move(JointMotion(home_q))
        
        if ret and not exit_event.is_set():
            sleep(0.2)
            print("waiting for human interaction @ home")
            force_z_base = robot.read_once().O_F_ext_hat_K[2]
            while ret and not exit_event.is_set():
                sleep(0.1)
                force_z_applied = robot.read_once().O_F_ext_hat_K[2] - force_z_base
                #print(force_z_applied)
                if force_z_applied > 4.5 and not is_grasp: # force_down, open
                    sleep(0.1)
                    print("clamp @ home")
                    is_grasp = gripper.clamp(0.004)
                    if not is_grasp:
                        print("clamp failed, re-open @ home")
                        gripper.open()    
                elif force_z_applied > 4.5 and is_grasp: # force_down, clamped
                    sleep(0.1)
                    print("open @ home")
                    gripper.open()
                    is_grasp = False
                elif force_z_applied < -6.0 and is_grasp: # force_up
                    break

        if ret and not exit_event.is_set():
            print("jointmotion @ handover")
            robot.set_dynamic_rel(max_dynamic_rel)
            ret = robot.move(JointMotion(handover_q))
        
        time_left = 6.0
        if ret and not exit_event.is_set():
            sleep(0.2)
            print(f"waiting for timeout [{time_left}s] or human interaction @ handover")
            force_z_base = robot.read_once().O_F_ext_hat_K[2]
            while not exit_event.is_set() and time_left > 0.0:
                sleep(0.1)
                force_z_applied = robot.read_once().O_F_ext_hat_K[2] - force_z_base
                if force_z_applied < -6.0: # force_up
                    break
                time_left -=0.1
        
        if time_left <= 0.0:
            # handover the object
            print("LinearRelativeMotion forward detect@ handover")
            motion = LinearRelativeMotion(Affine(x=0.25))
            motiondata = MotionData().with_dynamic_rel(0.12).with_reaction(Reaction(Measure.ForceXYNorm > 40.0, LinearRelativeMotion(Affine(x=-0.003))))
            ret = robot.move(Affine(), motion, motiondata)
            
            if motiondata.did_break:
                robot.recover_from_errors()
                sleep(3.8)
                print("LinearRelativeMotion forward @ handover")
                motion = LinearRelativeMotion(Affine(x=0.05, z=0.01))
                motiondata = MotionData().with_dynamic_rel(0.1)
                ret = robot.move(Affine(), motion, motiondata)
                
                robot.recover_from_errors()
                sleep(4.0)
                print("open @ handover")
                gripper.open()

                print("LinearRelativeMotion back @ handover")
                motion = LinearRelativeMotion(Affine(x=-0.07, z=0.07))
                ret = robot.move(Affine(), motion, motiondata)

def robot_run_take():
    print("###robot_run_take()###")
    ret = True
    
    if robot.read_once().robot_mode == RobotMode.Reflex:
        print("recover_from_errors")
        robot.recover_from_errors()
        sleep(2.0)

    #print(robot.read_once().q)

    if robot.read_once().robot_mode != RobotMode.Idle:
        print("RobotMode.Idle expected - Exit...")
        return

    home_q = [0.0, -M_PI_4, 0.0, -3 * M_PI_4, 0.0, M_PI_2, M_PI_4]
    handover_q = [-1.6111038785938625, 0.407968041546109, 0.044459180466279016, -1.1473555781548463, -0.030944301343626447, 2.0695322389107256, 0.7794737119053801]

    if ret and not exit_event.is_set():
            print("jointmotion @ home")
            robot.set_dynamic_rel(max_dynamic_rel)
            ret = robot.move(JointMotion(home_q))

    if ret and not exit_event.is_set():
        print("open @ home")
        print("...in 3s")
        sleep(1.0)
        print("...in 2s")
        sleep(1.0)
        print("...in 1s")
        sleep(1.0)
        gripper.open()

    if not ret: return
    
    while not exit_event.is_set():
        ret = True

        if robot.read_once().robot_mode == RobotMode.Reflex:
            print("recover_from_errors")
            robot.recover_from_errors()
            sleep(2.0)

        if ret and not exit_event.is_set():
            print("jointmotion @ home")
            robot.set_dynamic_rel(max_dynamic_rel)
            ret = robot.move(JointMotion(home_q))
        
        if ret and not exit_event.is_set():
            sleep(0.2)
            print("waiting for human interaction @ home")
            force_z_base = robot.read_once().O_F_ext_hat_K[2]
            while ret and not exit_event.is_set():
                sleep(0.1)
                force_z_applied = robot.read_once().O_F_ext_hat_K[2] - force_z_base
                if force_z_applied > 6.0: # force_down
                    sleep(0.1)
                    print("open @ home")
                    gripper.open()
                    is_grasp = False
                elif force_z_applied < -6.0: # force_up
                    break
        
        if ret and not exit_event.is_set():
            print("jointmotion @ handover")
            robot.set_dynamic_rel(max_dynamic_rel)
            ret = robot.move(JointMotion(handover_q))

        if ret and not exit_event.is_set():
            print("close @ home")
            gripper.release(0.004)
        
        is_robot_interaction = False
        if ret and not exit_event.is_set():
            sleep(0.2)
            print("waiting for robot or human interaction @ handover")
            forces_base = robot.read_once().O_F_ext_hat_K
            print(forces_base)
            while not exit_event.is_set():
                sleep(0.1)
                forces = robot.read_once().O_F_ext_hat_K
                #print(forces)
                if forces[2] - forces_base[2] < -6.0: # force_up
                    print("human interaction")
                    break

                if (pow(forces[0] - forces_base[0],2)+pow(forces[1] - forces_base[1],2) > 30):
                    is_robot_interaction = True
                    print("robot interaction")
                    break
        
        if ret and not exit_event.is_set() and is_robot_interaction:
            robot.recover_from_errors()

            print("open @ handover")
            gripper.open()

            sleep(0.25)
            print("clamp @ handover")
            gripper.clamp(0.004)
            
            print("handover")
            sleep(10.0)

def robot_setup(dyn_rel = 0.25):
    robot.set_default_behavior()
    robot.set_EE((0.7071, -0.7071, 0.0, 0.0, -0.7071, -0.7071, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.1034, 1.0))##Gripper-Default-EE
    robot.set_load(0.73, (-0.01, 0.0, 0.03), (0.001, 0.0, 0.0, 0.0, 0.0025, 0.0, 0.0, 0.0, 0.0017)) #Gripper-Default-Load
    robot.set_dynamic_rel(dyn_rel)

def signal_handler(signum, frame):
    print("EXIT SIGNAL...")
    exit_event.set()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    parser = ArgumentParser()
    parser.add_argument("--robotip", default="192.168.1.2", help="robot ip")
    parser.add_argument("--gatewayip", default="192.168.2.1", help="gateway ip")
    args = parser.parse_args()

    own_lan_ip = get_own_ip(args.gatewayip)
    #print(f"robot_ip={args.robotip}, gateway_ip={args.gatewayip}, own_lan_ip={own_lan_ip}")

    # Connect to the robot
    global robot, gripper, is_master_mode
    robot = Robot(fci_ip = args.robotip, repeat_on_error = False)
    gripper = robot.get_gripper()
    gripper.gripper_force = 50.0

    robot_setup(max_dynamic_rel)
    
    if own_lan_ip == "192.168.2.6":
        robot_run_give()
    elif own_lan_ip == "192.168.2.16":
        robot_run_take()
    else:
        print("please run onto robot pc with ip 192.168.2.6 or 192.168.2.16")
    
    #Exit
    robot.stop()
    print("open")
    print("...in 3s")
    sleep(1.0)
    print("...in 2s")
    sleep(1.0)
    print("...in 1s")
    sleep(1.0)
    gripper.open()
    gripper.stop()
    print("...DONE")
