import json
from dataclasses import dataclass
from typing import Union


@dataclass
class Eof:
    city_name: Union[str, None] = None

    @classmethod
    def decode(cls, data: bytes) -> "Eof":
        decoded_data = json.loads(data)
        data = decoded_data["payload"]
        return Eof(data)

    def encode(self) -> bytes:
        if self.city_name is None:
            return json.dumps({
                "type": "eof",
                "payload": ""
            }).encode()
        else:
            return json.dumps({
                "type": "eof",
                "payload": self.city_name
            }).encode()
