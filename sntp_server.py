from socket import *
from datetime import datetime

from sntp_message import Message, LeapIndicator, Mode


class SNTPServer:
    def __init__(self, offset: float = 0, port: int = 123):
        self.offset = offset
        self.sock = socket(AF_INET, SOCK_DGRAM)
        try:
            self.sock.bind(('localhost', port))
        except Exception:
            print('Check that the port 123 is available')
            self.sock.close()
            exit(0)

    def start(self):
        print('Server started! He\'ll lie for {} seconds\n'.format(self.offset))
        while True:
            print('Waiting of clients...')
            request, address = self.sock.recvfrom(1024)
            if request:
                self.handle_request(request, address)

    def handle_request(self, message: bytes, address):
        receive_timestamp = datetime.utcnow()
        print('Client {} sent a request'.format(address))
        response = self.get_answer(message, receive_timestamp)
        self.sock.sendto(response, address)
        print('Reply to client sent\n')

    def get_answer(self, data: bytes, rec_ts: datetime) -> bytes:
        request = Message.parse(data)
        response = Message(LI=LeapIndicator.no_warning,
                           VN=request.VN,
                           mode=Mode.server,
                           stratum=1,
                           originate_timestamp=request.transmit_timestamp,
                           receive_timestamp=self._time_shift(Message.to_seconds(rec_ts)),
                           transmit_timestamp=self._time_shift(Message.to_seconds(datetime.utcnow()))
                           ).to_bytes()
        response[24:32] = data[40:48]
        return bytes(response)

    def _time_shift(self, time: float) -> float:
        return time + self.offset
