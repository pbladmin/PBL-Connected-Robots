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
motion_thread = None
motion_generator = None
last_target_affine = None
last_robot_mode = None

is_grasping = False

def get_robotnet_ip(robot_ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((robot_ip, 80))
    robotnet_ip = s.getsockname()[0]
    s.close()
    return robotnet_ip

def robot_run_master(serverip):
    global is_grasping, last_robot_mode
    if (robot.read_once().robot_mode != RobotMode.UserStopped):
        print("toogle to RobotMode.UserStopped")
        return

    print("gripper")
    gripper.open()
    is_grasping = False

    print("socket")
    clients = []
    sockserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sockserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockserver.setsockopt(socket.SOL_SOCKET,socket.SO_RCVTIMEO,(0).to_bytes(8, 'little') + (25000).to_bytes(8, 'little')) #listen 40 ms
    sockserver.bind((serverip, 6070))


    while not exit_event.is_set():
        #listen to clients (connecting phase)
        try:
            client_msg = sockserver.recvfrom(1024) # msg = (raw_data, address)
            for client in clients:
                if client[0] == client_msg[1][0]:
                    clients.remove(client)
                    break
            clients.append(client_msg[1])
            print(f"client [{client_msg[1]}] connected; totally {len(clients)} clients")
        except KeyboardInterrupt:
            None # KeybordInterrupt
        except BlockingIOError:
            None # timeout
            
        if exit_event.is_set():
            break

        robot_state = robot.read_once()
        cur_pose = Affine(robot_state.O_T_EE)
        #send to clients (sending phase)
        server_msg = str(cur_pose)
        server_msg += "#"
        server_msg += str(robot_state.q)

        if last_robot_mode is not None \
            and last_robot_mode == RobotMode.Guiding \
            and robot_state.robot_mode == RobotMode.UserStopped \
            and cur_pose.z < 0.05:
            if not is_grasping:
                if gripper.clamp():
                    is_grasping = True
                else:
                    gripper.open()
            else:
                is_grasping = False
                gripper.open()

        if (is_grasping):
            server_msg += "#CLAMP"
        else:
            server_msg += "#OPEN"

        for client in clients:
            sockserver.sendto(server_msg.encode(), client)
        
        last_robot_mode = robot_state.robot_mode

    sockserver.close()

def robot_run_slave(serverip):
    if robot.read_once().robot_mode == RobotMode.UserStopped:
        print("release RobotMode.UserStopped")
        return
    
    print("recover_from_errors")
    robot.recover_from_errors()
    sleep(1.0)
    
    print("jointmotion")
    home_q = [0.0, -M_PI_4, 0.0, -3 * M_PI_4, 0.0, M_PI_2, M_PI_4]
    sleep(0.005)
    robot.move(JointMotion(home_q))

    print("gripper")
    gripper.open()

    print("socket")
    sockclient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sockclient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockclient.setsockopt(socket.SOL_SOCKET,socket.SO_RCVTIMEO,(2).to_bytes(8, 'little') + (0).to_bytes(8, 'little')) #listen 3s max

    while not exit_event.is_set():
        #listen to server (listen phase)
        try:
            msg = sockclient.recvfrom(1024) # msg = (raw_data, address)
            data = msg[0].decode()
            robot_react_slave(data)
        except KeyboardInterrupt:
            None # KeybordInterrupt
        except BlockingIOError:
            # timeout
            #connect to server (sending phase)
                print("re-connect")
                sockclient.sendto("CONNECT".encode(), (serverip, 6070))
            
        if exit_event.is_set():
            break

    sockclient.close()

def robot_react_slave(data):
    global motion_thread, motion_generator, last_target_affine, is_grasping
    try:
        data = data.split("#")
        str_floats = data[0].replace("[","").replace("]","").split(",")
        target_affine = Affine(float(str_floats[0]), float(str_floats[1]), float(str_floats[2]), float(str_floats[3]), float(str_floats[4]), float(str_floats[5]))

        if (motion_thread is None or not motion_thread.is_alive()):
           
            #clean-up
            if motion_generator is not None:    motion_generator.finish()
            if motion_thread is not None:       motion_thread.join()

            #re-create thread/motion   
            robot.recover_from_errors()
            robot.set_dynamic_rel(max_dynamic_rel*0.65)

            sleep(0.005)
            str_floats = data[1].replace("[","").replace("]","").split(",")
            target_q = [float(str_floats[0]), float(str_floats[1]), float(str_floats[2]), float(str_floats[3]), float(str_floats[4]), float(str_floats[5]), float(str_floats[6])]
            cur_q = robot.read_once().q
            if      abs(cur_q[0]-target_q[0]) > 0.00025 \
                and abs(cur_q[1]-target_q[1]) > 0.00025 \
                and abs(cur_q[2]-target_q[2]) > 0.00025 \
                and abs(cur_q[3]-target_q[3]) > 0.00025 \
                and abs(cur_q[4]-target_q[4]) > 0.00025 \
                and abs(cur_q[5]-target_q[5]) > 0.00025 \
                and abs(cur_q[6]-target_q[6]) > 0.00025:
                    robot.move(JointMotion(target_q))
            
            motion_generator = WaypointMotion([Waypoint(robot.current_pose())], return_when_finished=False) 
            motion_thread = robot.move_async(motion_generator)

            robot.set_dynamic_rel(max_dynamic_rel)
        else:
            #set target affine
            if last_target_affine is None:
                motion_generator.set_next_waypoint(Waypoint(target_affine))
            else:
                point_dist = math.sqrt(math.pow(last_target_affine.x-target_affine.x,2) + math.pow(last_target_affine.y-target_affine.y,2) + math.pow(last_target_affine.z-target_affine.z,2))
                if point_dist > 0.0015: # exceed the distance [m]
                    motion_generator.set_next_waypoint(Waypoint(target_affine))
                else:
                    #position reached
                    if data[2] == "CLAMP" and not is_grasping:
                        gripper.clamp()
                        is_grasping = True
                    elif data[2] == "OPEN" and is_grasping:
                        gripper.open()
                        is_grasping = False
        
        last_target_affine = target_affine
    except:
        print("server data mismatch")
        return

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
    parser.add_argument("--masterip", default="192.168.2.10", help="master ip")
    args = parser.parse_args()

    print(args.masterip, get_robotnet_ip(args.masterip))

    # Connect to the robot
    global robot, gripper, is_master_mode
    robot = Robot(fci_ip = args.robotip, repeat_on_error = False)
    gripper = robot.get_gripper()

    robot_setup(max_dynamic_rel)

    if (get_robotnet_ip(args.masterip) == args.masterip):
        print("MASTER MODE SET")
        is_master_mode = True
        robot_run_master(args.masterip)
    else:
        print("SLAVE MODE SET")
        is_master_mode = False
        robot_run_slave(args.masterip)

    #Exit
    gripper.open()
    gripper.stop()
    robot.stop()
    print("...DONE")
