import socket
import select
import threading
import time
import json
import signal
from enum import Enum

IP = "localhost" # "127.0.0.1"
PORT = 8980

## commands
END = "0"       #
MSG = "1"
TXT = "2"
HOGA = "10"     # hoga  
BUY = "11"
SELL = "12"
STAY = "13"   

# protocol...
PROTO_CMD = 'cmd'
PROTO_MSG = 'msg'
PROTO_TXT = 'text'
PROTO_VALUE = 'price'
PROTO_COUNT = 'cnt'

##############################################
class tcp_socket():
    def __init__(self, conn = None, recv_size= 10240):
        self.socket = conn
        self.th = None
        self._is_connected = True if conn is not None else False
        self.recv_size = recv_size

    @property
    def is_connected(self):
        return True if self.socket is not None and self._is_connected else False
    
    @is_connected.setter
    def is_connected(self, value):
        self._is_connected = value

    def connect(self, ip = IP, port = PORT, user_callback = None):
        ret = True
        try: 
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip,port))
            self._is_connected = True

            self.th = self.recv_thread(self, user_callback)
        except:
            ret = False
            self._is_connected = False

        return ret


    def close(self, th = None):
        """
        소켓 닫기 
        """
        self.is_connected = False
        if self.socket is not None:
            self.socket.close()

        # thread out
        if self.th is not None:
            if self.th.is_alive():
                self.th.join()
        # clear ...
        self.th = None
        self.socket = None

    ################### transfer thread #####################

    def recv_thread(self, conn, callback_func, wait=False):
        th = threading.Thread(target=self.__recv_thread, args=(conn, callback_func), daemon=True)
        th.start()

        if wait:
            # 접속 종료 때 까지 기다린다.
            while th.is_alive():
                try:
                    time.sleep(0.1)
                except:
                    break
            th.join()

        return th

    def __recv_thread(self, conn, callback_func):
        """
        데이터 수신
        """
        while conn.is_connected:
            try:
                data = conn.recv(self.recv_size)
                if (len(data) > 0):     #  and (type(data) is bytes):
                    u = json.loads(data.decode("utf-8"))
                    
                    # check data format
                    if PROTO_CMD in u:
                        if u[PROTO_CMD] == END:
                            break
                        else:
                            if callback_func is not None:
                                callback_func(conn, u)
                    else:
                        print('unknown format : ', u)
            except OSError as err:
                print('os except : ', err)
                break
            except ValueError as err:
                print('value except : ', err)
                break
            except Exception as err:
                print('except : ', err)
                break

        # auto disconnect
        if conn.th is None:         
            conn.close(conn.th)
        # print('disconncted')
    ################### transfer thread #####################

    def recv(self, rsize):
        _bytes = b''
        try:
            _bytes = self.socket.recv(rsize)
        except:
            raise OSError('disconnected !')
        return _bytes
    
    def send(self, cmd, msg = '', text = '', value = 0.0, count = 0.0, wait = 0.001):
        """
        소켓 전송
        """
        bsend = False

        if self._is_connected and self.socket is not None:
            h = {
                PROTO_CMD: cmd,
                PROTO_MSG: msg
            }

            # BUY, SELL, STAY
            if (cmd == BUY) or (cmd == SELL) or (cmd == STAY):
                h[PROTO_VALUE] = value
                h[PROTO_COUNT] = count

            elif (cmd == TXT): # if (cmd == MSG) or cmd == HOGA:
                h[PROTO_TXT] = text

            try:
                self.socket.send(json.dumps(h).encode("utf-8"))
                bsend = True
                time.sleep(0.001)
            except OSError as err:
                print('os except : ', err)
                # bsend = False
            except ValueError as err:
                print('value except : ', err)
                # bsend = False
            except Exception as err:
                print('except : ', err)
                # bsend = False

        return bsend

##############################################
class tcp_server(tcp_socket):    
    def __init__(self, recv_size = 10240):
        super().__init__(None, recv_size)

    def start(self, ip=IP, port=PORT, callback_func=None):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((ip,port))
        self.socket.listen() # 1)

        while True:
            conn, addr = self.socket.accept()
            print('connected : ', addr)
        
            client = tcp_socket(conn, self.recv_size)
            self.recv_thread(client, callback_func, True)
            client.close()

##############################################
class tcp_client(tcp_socket):
    def __init__(self, recv_size = 10240):
        super().__init__(None, recv_size)
        self.ip = ''
        self.port = 0
        self.user_callback = None

    def connect(self, ip = IP, port = PORT, user_callback = None):
        """
        서버에 접속 한다.
        """
        self.ip = ip
        self.port = port
        self.user_callback = user_callback

        return super().connect(self.ip, self.port, self.user_callback)

    def reconnect(self):
        """
        자동 재접속..
        """
        self.close()
        return self.connect(self.ip, self.port, self.user_callback)
