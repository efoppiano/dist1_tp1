from dataclasses import dataclass
from typing import Union


@dataclass
class Eof:
    city_name: Union[str, None] = None

    @classmethod
    def decode(cls, data: bytes) -> "Eof":
        if data == b'eof':
            return Eof()
        else:
            return Eof(data.decode())

    def encode(self) -> bytes:
        if self.city_name is None:
            return b'eof'
        else:
            return self.city_name.encode()
