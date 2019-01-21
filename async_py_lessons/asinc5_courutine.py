
#got from:
# 2015 PyCon
# Concurrency from the Ground up Live

import socket
from select import select

tasks=[]

to_read={}
to_write={}



def server():
    server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 5001))
    server_socket.listen()

    while True:
        print('before yeld in server')
        yield ('read', server_socket)
        print('imediatly after yeld server')
        client_socket, addr = server_socket.accept() #read

        print('connection from', addr)

        tasks.append(client(client_socket))
        print('added client_socket: ', client_socket)
        print('tasks: ', tasks)

def client(client_socket):
    while True:
        print('before reading client_socket')
        yield  ('read', client_socket)
        request=client_socket.recv(4096) #read
        print('resived from client: ', request)

        if not request:
            break
        else:
            response='Hello world\n'.encode()

            print('before sending response')
            yield ('write', client_socket)
            client_socket.send(response) #write
            print('imadiatly after sending response')

    print('cloasing client_socket ...')
    client_socket.close()


def event_loop():

    while any([tasks, to_read, to_write]):

        while not tasks:
            ready_to_read, ready_to_write, _ = select(to_read, to_write, [])
            print('search for ready_to_read')
            for sock in ready_to_read:
                tasks.append(to_read.pop(sock))

            print('search for ready_to_write')
            for sock in ready_to_write:
                tasks.append(to_write.pop(sock))

        try:
            print('getting task for resolve')
            task=tasks.pop(0)
            print('task is : ', task)

            reason, sock =next(task)

            if reason =='read':
                print('reason read')
                to_read[sock]=task

            if reason == 'write':
                print('reason write')
                to_write[sock]=task

        except StopIteration:
            print('Done!')

tasks.append(server())
event_loop()


