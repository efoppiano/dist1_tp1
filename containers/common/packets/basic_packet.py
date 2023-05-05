import base64
from abc import ABC
from dataclasses import dataclass
from typing import Union


@dataclass
class BasicPacket(ABC):
    def encode(self) -> bytes:
        class_fields = self.__class__.__dict__["__dataclass_fields__"]
        elements = [getattr(self, field_name) for field_name in class_fields]
        elements_bytes = [str(element).encode() for element in elements]
        return b",".join(elements_bytes)

    @classmethod
    def decode(cls, data: Union[bytes, str]) -> "BasicPacket":
        class_fields = cls.__dict__["__dataclass_fields__"]
        if isinstance(data, str):
            elements = data.split(",")
        else:
            elements_bytes = data.split(b",")
            elements = [element.decode() for element in elements_bytes]
        elements_casted = []
        for (field_name, element) in zip(class_fields, elements):
            field_type = class_fields[field_name].type
            if field_type == str:
                elements_casted.append(element)
            elif field_type == int:
                elements_casted.append(int(element))
            elif field_type == float:
                elements_casted.append(float(element))
            elif field_type == bool:
                elements_casted.append(element == "True")
            else:
                raise NotImplementedError(f"Unknown type: {field_type}")
        return cls(*elements_casted)
