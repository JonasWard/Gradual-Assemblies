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

        # placing variables
        speed_set = 2000.0
        safety_z_height = 60.0
        drill_speed_in = 2
        drill_speed_out = 20
        picking_cnt = 0
        angle = 5.0
        radAngle = 3.14 * angle / 180.0

        # # first move command
        # print ("start with the first, safety, plane")
        # x0, y0, z0, ax0, ay0, az0, speed, radius = commands_drilling[0]
        # print (commands_drilling[0])
        # ur.send_command_movel([x0, y0, safety_z_height, ax0, ay0, az0], v=speed_set, r=radius)
        # print ("done with the first, safety, plane")

        # drilling movements
        print ("\nstarting with the main loop")
        for i in range(0, len(commands_flattened_drilling) - 2, 3):
            sequence_count = round((i + 1)/2)
            print ("\tstart %i" % sequence_count)
            x1, y1, z1, ax1, ay1, az1, speed, radius = commands_drilling[i]
            x2, y2, z2, ax2, ay2, az2, speed, radius = commands_drilling[i + 1]
            x3, y3, z3, ax3, ay3, az3, speed, radius = commands_drilling[i + 2]

            # moving to start position
            ur.send_command_movel([x1, y1, z1, ax1, ay1, az1], v=speed_set, r=radius)
            # moving to safety plane
            ur.send_command_movel([x2, y2, z2, ax2, ay2, az2], v=speed_set, r=radius)
            # starting the drill
            ur.send_command_digital_out(0, True)
            # drill movement
            ur.send_command_movel([x3, y3, z3, ax3, ay3, az3], v=drill_speed_in, r=radius)
            # stop the drill
            ur.send_command_digital_out(0, False)
            # moving out
            ur.send_command_movel([x2, y2, z2, ax2, ay2, az2], v=drill_speed_out, r=radius)
            # moving back to safety plane
            ur.send_command_movel([x1, y1, z1, ax1, ay1, az1], v=speed_set, r=radius)
            # # moving back to the center position
            # ur.send_command_movel([x0, y0, safety_z_height, ax0, ay0, az0], v=speed_set, r=radius)

            print ("\tdone with sequence %i" % sequence_count)

        #moving back to the start
        print ("moving back to the start safety position")
        x0, y0, z0, ax0, ay0, az0, speed, radius = commands_drilling[0]
        print (commands_drilling[0])
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
