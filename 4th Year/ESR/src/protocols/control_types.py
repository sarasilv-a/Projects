class MessageType:
    CONTROL = 1   # type 1 = control messages
    STREAM = 2    # type 2 = stream messages 


class ControlSubtype:
    PING = 1
    PONG = 2
    ANNOUNCE = 3
    ACTIVATE = 4
    JOIN = 5
    LEAVE = 6
    REQUEST = 8
    RESPONSE = 9
    ACK = 10
    STREAM_LIST_REQUEST = 13
    STREAM_LIST_RESPONSE = 14
    ROUTE_WITHDRAW = 15
    NACK = 16
    