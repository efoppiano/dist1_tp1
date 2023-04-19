#!/usr/bin/env python3
import logging
from typing import Union

from common.basic_filter import BasicFilter
from common.packets.prec_filter_info import PrecFilterInfo
from common.utils import initialize_log


class PrecFilter(BasicFilter):
    def handle_message(self, message: bytes) -> Union[bytes, None]:
        packet = PrecFilterInfo.decode(message)
        logging.info("prectot: {}".format(packet.prectot))
        if packet.prectot > 30:
            return message
        else:
            return None


def main():
    initialize_log(logging.DEBUG)
    filter = PrecFilter("prec_filter_in", "prec_filter_out")
    filter.start()


if __name__ == "__main__":
    main()
