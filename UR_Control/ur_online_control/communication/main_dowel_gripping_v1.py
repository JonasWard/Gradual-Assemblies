'''
Created on 22.11.2016
update by JonasWard 10.01.2019

@author: rustr, jennyd, JonasWard
'''
from __future__ import print_function
# import time
import sys
import os

# set the paths to find library
file_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(file_dir, "..", ".."))
sys.path.append(file_dir)
sys.path.append(parent_dir)

import ur_online_control.communication.container as container
from ur_online_control.communication.server import Server
from ur_online_control.communication.client_wrapper import ClientWrapper
from ur_online_control.communication.formatting import format_commands

if len(sys.argv) > 1:
    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    ur_ip = sys.argv[3]
    print(sys.argv)
else:
    #server_address = "192.168.10.12"
    server_address = "127.0.0.1"
    server_port = 30003
    #ur_ip = "192.168.10.11"
    ur_ip = "127.0.0.1"

def main():

    # start the server
    server = Server(server_address, server_port)
    server.start()
    server.client_ips.update({"UR": ur_ip})

    # create client wrappers, that wrap the underlying communication to the sockets
    gh = ClientWrapper("GH")
    ur = ClientWrapper("UR")

    # wait for the clients to be connected
    gh.wait_for_connected()
    ur.wait_for_connected()

    # now enter fabrication loop
    while True: # and ur and gh connected
        # let gh control if we should continue
        continue_fabrication = gh.wait_for_int() #1 client.send(MSG_INT, int(continue_fabrication))
        print("1: continue_fabrication: %i" % continue_fabrication)
        print ("start fabrication")

        """
        if not continue_fabrication:
            break
        """

        tool_string = gh.wait_for_float_list() #2 client.send(MSG_FLOAT_LIST,tool_string_axis)
        print("2: set tool TCP")

        ur.send_command_tcp(tool_string)

        len_command_drilling = gh.wait_for_int()             #3 client.send(MSG_INT, len_command)
        print ("3: len command list drilling")
        commands_flattened_drilling = gh.wait_for_float_list() #4 client.send(MSG_FLOAT_LIST, commands_flattened)
        print ("4: command list drilling")

        # the commands are formatted according to the sent length
        commands_drilling = format_commands(commands_flattened_drilling, len_command_drilling)
        print("We received %i drilling commands." % len(commands_drilling))

        number_of_holes_list = gh.wait_for_float_list() #4 client.send(MSG_INT_LIST, number_of_holes_list)
        print ("4: number of holes list")

        print(number_of_holes_list)

        # placing variables
        speed_set = 1500.0
        safety_z_height = 100.0
        drill_speed_in = 2.0
        drill_speed_out = 80.0
        picking_cnt = 0
        angle = 5.0
        radAngle = 3.14 * angle / 180.0

        # drilling movements
        used_plane_count = 0
        print ("\nstarting with the main loop")
        
        beam_count = 0

        for number_of_holes in number_of_holes_list:

            ur.wait_for_ready()

            print('Beam count: %d' % beam_count)

            number_of_holes = int(number_of_holes)

            x1, y1, z1, ax1, ay1, az1, speed, radius = commands_drilling[used_plane_count] #picking plane

            """
            gripper off"""
            ur.send_command_digital_out(0, False)

            """
            moving to picking safety plane"""
            ur.send_command_movel([x1, y1, z1 + safety_z_height, ax1, ay1, az1], v=speed_set, r=radius)

            """"
            rotate wrist 3"""
            ur.wait_for_ready()
            joint_angles = ur.get_current_pose_joint()
            joint_angles[-1] = 0.0
            ur.send_command_movej(joint_angles, v=speed_set, r=radius)

            ur.send_command_wait(0.5)

            """
            moving to picking plane"""
            ur.send_command_movel([x1, y1, z1 + safety_z_height * 0.5, ax1, ay1, az1], v=speed_set, r=radius)

            """
            moving to picking plane"""
            ur.send_command_movel([x1, y1, z1, ax1, ay1, az1], v=speed_set, r=radius)

            ur.send_command_wait(0.5)

            
            """
            gripper on"""
            ur.send_command_digital_out(0, True)
            """
            moving to picking safety plane"""

            ur.send_command_wait(0.5)

            ur.send_command_movel([x1, y1, z1 + safety_z_height, ax1, ay1, az1], v=speed_set, r=radius)

            for j in range(number_of_holes):

                x2, y2, z2, ax2, ay2, az2, speed, radius = commands_drilling[used_plane_count + j * 3 + 1] #drilling safety plane
                x3, y3, z3, ax3, ay3, az3, speed, radius = commands_drilling[used_plane_count + j * 3 + 2] #start drilling plane
                x4, y4, z4, ax4, ay4, az4, speed, radius = commands_drilling[used_plane_count + j * 3 + 3] #end drilling plane

                """
                moving to drilling safety plane"""
                ur.send_command_movel([x2, y2, z2, ax2, ay2, az2], v=speed_set, r=radius)

                """"
                rotate wrist 3"""
                ur.wait_for_ready()
                joint_angles = ur.get_current_pose_joint()
                joint_angles[-1] = 0.0
                ur.send_command_movej(joint_angles, v=speed_set, r=radius)

                """
                moving to drilling safety plane"""
                ur.send_command_movel([x2, y2, z2, ax2, ay2, az2], v=speed_set, r=radius)

                """
                start drilling plane"""
                ur.send_command_movel([x3, y3, z3, ax3, ay3, az3], v=speed_set, r=radius)
                """
                end drilling plane"""
                ur.send_command_movel([x4, y4, z4, ax4, ay4, az4], v=drill_speed_in, r=radius)
                """
                moving to drilling safety plane"""
                ur.send_command_movel([x2, y2, z2, ax2, ay2, az2], v=drill_speed_out, r=radius)


            x5, y5, z5, ax5, ay5, az5, speed, radius = commands_drilling[used_plane_count + number_of_holes * 3 + 1] #placing plane

            """
            moving to safe placing plane"""

            ur.send_command_movel([x5, y5, z5 + safety_z_height, ax5, ay5, az5], v=speed_set, r=radius)

            """"
            rotate wrist 3"""
            ur.wait_for_ready()
            joint_angles = ur.get_current_pose_joint()
            joint_angles[-1] = 0.0
            ur.send_command_movej(joint_angles, v=speed_set, r=radius)

            """
            moving to placing plane"""

            ur.send_command_movel([x5, y5, z5, ax5, ay5, az5], v=speed_set, r=radius)

            ur.wait_for_ready()
            ur.send_command_popup(title='hello!', message='Press ok when you are ready!', blocking=True)
            ur.wait_for_ready()

            """
            gripper off"""
            ur.send_command_digital_out(0, False)

            ur.send_command_wait(1.0)

            """
            moving to safe placing plane"""

            ur.send_command_movel([x5, y5, z5 + safety_z_height, ax5, ay5, az5], v=speed_set, r=radius)


            beam_count += 1

            used_plane_count += number_of_holes * 3 + 2

        #moving back to the start
        print ("moving back to the start safety position")
        x0, y0, z0, ax0, ay0, az0, speed, radius = commands_drilling[0]

        ur.send_command_movel([x0, y0, safety_z_height, ax0, ay0, az0], v=speed_set, r=radius)
        print ("done with the last move")

        ur.wait_for_ready()

        #ur.wait_for_ready()

        print("all done!")

    ur.quit()
    gh.quit()
    server.close()

    print("Please press a key to terminate the program.")
    junk = sys.stdin.readline()
    print("Done.")

if __name__ == "__main__":
    main()
