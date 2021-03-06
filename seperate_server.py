from user import User
import os
from queue import Queue
from colors import color_dict
# from user import send, extract, formatmsg, split_dirtext, CLOSE_STRING, format_diroutput
from user import CLOSE_STRING, send
from messaging import *
from DFSbackend import DFShandler


def serv_processing(item):
    global seperate_server, FOLDER_PATH, dfs_handler
    # print(color_dict['red'] + f"server processing item : {item}" + color_dict['reset'])
    user_uid, user_ip, user_port, msg = extract(item)   # get the uid, ip, port, msg of the user who sent the message

    if msg == CLOSE_STRING:  # this will only matter if we want the user to be able to close the remote
        send(user_ip, int(user_port),
             formatmsg(uid=DEFAULT_UID, host_ip=user_ip, host_portnum=user_port, item=CLOSE_STRING),
             recieve=False)
        return
    curr_dir, text = split_dirtext(msg)

    # make a user-specific instance of the dfs handler (and run it in a seperate thread?)
    #  using the Users UID from the message
    FOLDER_PATH = os.getcwd().replace("\\", "/") + '/' + str(user_uid) + "_folder/"
    # print(FOLDER_PATH)
    if not os.path.isdir(FOLDER_PATH):
        os.mkdir(FOLDER_PATH, 0o777)

    dfs_handler = DFShandler(user_uid, FOLDER_PATH)
    dir_to_change, output = dfs_handler.parse(current_dirpath=curr_dir, msg=text)

    send(user_ip, int(user_port),
         formatmsg(uid=DEFAULT_UID,
                   host_portnum=seperate_server.SERVER_PORTNUM,
                   host_ip=seperate_server.HOST_IP,
                   item=format_diroutput(dir_to_change, output)),
         recieve=False)


seperate_server, FOLDER_PATH, dfs_handler, = None, None, None
DEFAULT_UID = 999  # default server UID


def main():
    global seperate_server, dfs_handler, FOLDER_PATH
    msg_q = Queue()
    seperate_server = User(client_q=msg_q, serv_q=msg_q, HOST_IP='127.0.0.1', SERVER_PORTNUM=12001, DEST_IP='127.0.0.1',
                           REMOTE_PORTNUM=9001, proc_func=serv_processing)
    serv_s, serv_c = seperate_server.start_both()
    serv_s.join()


if __name__ == '__main__':
    main()


