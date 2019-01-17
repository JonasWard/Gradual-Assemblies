'''
Created on 22.11.2016

@author: rustr, jennyd
'''
from __future__ import print_function
import time
import sys
import os

# set the paths to find library
file_dir = os.path.dirname( __file__)
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

        len_command_picking = gh.wait_for_int()             #3 client.send(MSG_INT, len_command)
        print ("3: len command list picking")
        commands_flattened_picking = gh.wait_for_float_list() #4 client.send(MSG_FLOAT_LIST, commands_flattened)
        print ("4: command list picking")

        len_command_placing = gh.wait_for_int()             #3 client.send(MSG_INT, len_command)
        print ("5: len command list placing")
        commands_flattened_placing = gh.wait_for_float_list() #4 client.send(MSG_FLOAT_LIST, commands_flattened)
        print ("6: command list placing")


        # the commands are formatted according to the sent length
        commands_picking = format_commands(commands_flattened_picking, len_command_picking)
        print("We received %i picking commands." % len(commands_picking))

        commands_placing = format_commands(commands_flattened_placing, len_command_placing)
        print("We received %i placing commands." % len(commands_placing))


        # placing path
        picking_cnt = 0
        for i in range(0, len(commands_flattened_placing), 3):

            #above picking
            placing_cmd = commands_picking[picking_cnt]
            x, y, z, ax, ay, az, speed, radius = placing_cmd
            ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)

            #picking
            placing_cmd = commands_picking[picking_cnt+1]
            x, y, z, ax, ay, az, speed, radius = placing_cmd
            ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)
            # ur.send_command_wait(1.0)

            #rotate
            placing_cmd = commands_picking[picking_cnt+2]
            x, y, z, ax, ay, az, speed, radius = placing_cmd
            ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)
            # ur.send_command_wait(1.0)

            #above picking
            placing_cmd = commands_picking[picking_cnt+3]
            x, y, z, ax, ay, az, speed, radius = placing_cmd
            ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)

            #above placing
            placing_cmd = commands_placing[i]
            x, y, z, ax, ay, az, speed, radius = placing_cmd
            ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)

            #placing
            placing_cmd = commands_placing[i+1]
            shooting_timer = .26
            x, y, z, ax, ay, az, speed, radius = placing_cmd
            ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)
            ur.send_command_wait(0.01)
            for i in range(3)
                ur.send_command_digital_out(0, True)
                ur.send_command_wait(shooting_timer)
                ur.send_command_digital_out(0, False)

            #above placing
            placing_cmd = commands_placing[i+2]
            x, y, z, ax, ay, az, speed, radius = placing_cmd
            ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)

            picking_cnt += 4
            ur.send_command_popup()

        ur.send_command_digital_out(0, True) # Turn ON piston
        ur.send_command_wait(0.01)
        ur.wait_for_ready()

        ### Out Pose ###
        #safe_out_pose_cmd = gh.wait_for_float_list() #6 client.send(MSG_FLOAT_LIST, safe_out_pose_cmd)
        #print ("6: safe out pose")
        #x, y, z, ax, ay, az, speed, acc = safe_out_pose_cmd
        #ur.send_command_movel([x, y, z, ax, ay, az], v=speed, a=acc)
        ur.send_command_wait(0.5)
        ur.wait_for_ready()

        #ur.wait_for_ready()

        print("============================================================")

    ur.quit()
    gh.quit()
    server.close()

    print("Please press a key to terminate the program.")
    junk = sys.stdin.readline()
    print("Done.")

if __name__ == "__main__":
    main()
