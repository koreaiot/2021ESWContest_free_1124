import os
from socket import *

class Connect:

    global HOST
    global PORT
    global clientSock
    global IMG_DIR
    IMG_DIR = "sendimage"
    HOST = "192.168.217.230"
    PORT = 22222

    def send_img():
        """
        Date : 21.09.16
        Function : Send pictures to the server when certain conditions are achieved.
        """
        
        try:
            if len(os.listdir(IMG_DIR)) != 0:
                img_list = os.listdir(IMG_DIR)
                print(img_list)
                #send all image
                for img in img_list:
                    clientSock = socket(AF_INET, SOCK_STREAM)
                    clientSock.connect((HOST,PORT))
                    clientSock.sendall(bytes(f"{img}", encoding = 'utf8'))
                    clientSock.sendall(bytes("\n", encoding = 'utf8'))
                    reply = clientSock.recv(1024)
                    reply = reply.decode()
                    print(reply, "\n")
                    send_img = IMG_DIR + "/" + img
                    img = open(send_img, 'rb')
                    converted_img = img.read()
                    clientSock.sendall(converted_img)
                    img.flush()
                    img.close()
                    clientSock.close()

                # send the end
                clientSock = socket(AF_INET, SOCK_STREAM)
                clientSock.connect((HOST,PORT))
                clientSock.sendall(bytes("", encoding = 'utf8'))
                clientSock.sendall(bytes("\n", encoding = 'utf8'))
                reply = clientSock.recv(1024)
                reply = reply.decode()
                if reply == "END":
                    print("connect end")
                    clientSock.close()

            else:
                print("file is not exist")
        except Exception as e:
            print(e)

    def remove_img():
        
        """
        Date : 21.09.18
        Function : Remove the pictures in the directory.
        """
   
        img_list = os.listdir(IMG_DIR)
        for img in img_list:
            remove_img = IMG_DIR + "/" + img
            os.remove(remove_img)
            print(f"{img} : delect")