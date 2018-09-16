from enum import IntEnum
from datetime import datetime


class LeapIndicator(IntEnum):
    no_warning = 0
    last_minute_has_61_seconds = 1
    last_minute_has_59_seconds = 2
    alarm_condition = 3


class Mode(IntEnum):
    reserved = 0
    symmetric_active = 1
    symmetric_passive = 2
    client = 3
    server = 4
    broadcast = 5
    reserved_for_NTP_control_message = 6
    reserved_for_private_use = 7


class Message:
    EPOCH_TIME = datetime(1900, 1, 1)

    def __init__(self,
                 LI=LeapIndicator.no_warning,
                 VN: int = 4,
                 mode: Mode = Mode.reserved,
                 stratum: int = 1,
                 poll: int = 0,
                 precision: int = 0,
                 root_delay: float = 0,
                 root_dispersion: float = 0,
                 reference_identifier: str = 'GOES',
                 reference_timestamp: float = 0,
                 originate_timestamp: float = 0,
                 receive_timestamp: float = 0,
                 transmit_timestamp: float = 0):
        self.LI = LI
        self.VN = VN
        self.mode = mode
        self.stratum = stratum
        self.poll = poll
        self.precision = precision
        self.root_delay = root_delay
        self.root_dispersion = root_dispersion
        self.reference_identifier = reference_identifier
        self.reference_timestamp = reference_timestamp
        self.originate_timestamp = originate_timestamp
        self.receive_timestamp = receive_timestamp
        self.transmit_timestamp = transmit_timestamp

    @staticmethod
    def parse(data: bytes):
        first_byte = (bin(data[0])[2:]).zfill(8)

        LI = LeapIndicator(int(first_byte[0:2], 2))
        VN = int(first_byte[2:5], 2)
        mode = Mode(int(first_byte[5:8], 2))

        stratum = data[1]
        poll = data[2]
        precision = data[3]

        root_delay = Message._from_bytes(data[4:6]) + Message._from_bytes(data[6:8]) / (2 ** 16)
        root_dispersion = Message._from_bytes(data[8:10]) + Message._from_bytes(data[10:12]) / (2 ** 16)
        reference_identifier = data[12:16].decode('utf-8')

        reference_timestamp = Message._from_bytes(data[16:20]) + Message._from_bytes(data[20:24]) / 2 ** 32
        originate_timestamp = Message._from_bytes(data[24:28]) + Message._from_bytes(data[28:32]) / 2 ** 32
        receive_timestamp = Message._from_bytes(data[32:36]) + Message._from_bytes(data[36:40]) / 2 ** 32
        transmit_timestamp = Message._from_bytes(data[40:44]) + Message._from_bytes(data[44:48]) / 2 ** 32

        return Message(LI, VN, mode, stratum, poll, precision, root_delay, root_dispersion, reference_identifier,
                       reference_timestamp, originate_timestamp, receive_timestamp, transmit_timestamp)

    @staticmethod
    def _from_bytes(raw: bytes) -> int:
        return int.from_bytes(raw, byteorder='big')

    def to_bytes(self) -> bytearray:
        result = bytearray()
        first_byte = (bin(self.LI)[2:]).zfill(2) + \
                     (bin(self.VN)[2:]).zfill(3) + \
                     (bin(self.mode)[2:]).zfill(3)
        result += int(first_byte, 2).to_bytes(1, 'big')

        result += self.stratum.to_bytes(1, 'big')
        result += self.poll.to_bytes(1, 'big')
        result += self.precision.to_bytes(1, 'big')

        result += Message.encode_timestamp_format(self.root_delay, 4)
        a = Message.encode_timestamp_format(self.root_dispersion, 4)
        result += a
        print(a)
        result += self.reference_identifier.encode('utf-8')

        result += Message.encode_timestamp_format(self.reference_timestamp, 8)
        result += Message.encode_timestamp_format(self.originate_timestamp, 8)
        result += Message.encode_timestamp_format(self.receive_timestamp, 8)
        result += Message.encode_timestamp_format(self.transmit_timestamp, 8)
        # result += Message.encode_timestamp_format(Message.to_seconds(datetime.utcnow()), 8)

        return result

    @staticmethod
    def encode_timestamp_format(timestamp: float, length: int) -> bytes:
        half = length // 2
        parts = str(timestamp).split('.')
        seconds = int(parts[0])
        seconds_fractions = float('0.' + parts[1]) if len(parts) > 1 else 0
        seconds_fractions *= 2 ** (half * 8)
        return seconds.to_bytes(half, 'big') + int(seconds_fractions).to_bytes(half, 'big')

    @staticmethod
    def to_seconds(timestamp: datetime) -> float:
        return (timestamp - Message.EPOCH_TIME).total_seconds()
