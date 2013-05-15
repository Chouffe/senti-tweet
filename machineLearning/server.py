import socket
import random
import predict
import struct

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

c.bind(('', 12800))

c.listen(5)

while 1:
    cc, infos = c.accept()
    print(infos)
    while 1:
        size = cc.recv(4)
        try:
            tweet = cc.recv(struct.unpack(">L", size)[0]+2)
        except:
            tweet = cc.recv(142)
        print("Received tweet: ")
        print(tweet[2:])
        res = predict.predict(tweet[2:]);
        print("Result :")
        print(res)
        cc.send(struct.pack(">L", res+1))
    cc.close()

c.close()