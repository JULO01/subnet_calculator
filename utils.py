from typing import Tuple
import re

class NetAdressFormatError(Exception):
    def __init__(
        self,
        message="The specified net-address did not have the required format.",
    ):
        super().__init__(message)

def bit_not(n, numbits=32):
    return (1 << numbits) - 1 - n


def binary_string_to_net(binary_string: str) -> Tuple[int, int, int, int]:
    if binary_string[0:2] == "0b":
        binary_string = binary_string[2:]

    return (
        int("0b" + binary_string[0:8], 2),
        int("0b" + binary_string[8:16], 2),
        int("0b" + binary_string[16:24], 2),
        int("0b" + binary_string[24:32], 2),
    )


def integer_to_net(integer: int) -> Tuple[int, int, int, int]:
    binary_string = bin(integer)[2:]

    if len(binary_string) > 32:
        print(len(binary_string))
        raise NetAdressFormatError("Integer address is too big.")

    binary_string = binary_string.zfill(32)
    return binary_string_to_net(binary_string)


def net_to_integer(net: Tuple[int, int, int, int]) -> int:
    binary_str = ""

    for field in net:
        binary_str += bin(field)[2:].zfill(8)

    return int("0b" + binary_str, 2)


def schraeger_to_net(schraeger: int) -> Tuple[int, int, int, int]:
    if schraeger < 0 or schraeger > 32:
        raise NetAdressFormatError("Schraeger does contain invalid number.")

    binary_string = schraeger * "1" + (32 - schraeger) * "0"

    return binary_string_to_net(binary_string)


def net_to_schraeger(subnet: Tuple[int, int, int, int]) -> int:
    binary_string = ""
    for entry in subnet:
        binary_string += bin(entry)[2:].zfill(8)

    addr_regex = "1*0*$"
    addr_result = re.match(addr_regex, binary_string)

    if not addr_result:
        raise NetAdressFormatError("The subnet_mask contains leading zeros.")

    return binary_string.count("1")


def schraeger_str_or_net_str_to_schraeger(schraeger_or_subnet_mask: str) -> int:
    schraeger_ex = "[0-2][0-9]$|[3][0-2]$|[0-9]$"
    schreager_result = re.match(schraeger_ex, schraeger_or_subnet_mask)

    if schreager_result:
        return int(str(schraeger_or_subnet_mask))

    try:
        net_addr = net_str_to_net(schraeger_or_subnet_mask)
    except NetAdressFormatError:
        raise NetAdressFormatError(
            "The specified subnet_mask did not fulfill the net-address format."
        )

    return net_to_schraeger(net_addr)


def schraeger_str_or_net_str_to_net(
    schraeger_or_subnet_mask: str,
) -> Tuple[int, int, int, int]:
    schraeger = schraeger_str_or_net_str_to_schraeger(schraeger_or_subnet_mask)
    return schraeger_to_net(schraeger)


def net_to_net_str(subnet: Tuple[int, int, int, int]):
    subnet_str = ""
    for i in range(0, 4):
        subnet_str += str(subnet[i])
        if i < 3:
            subnet_str += "."

    return subnet_str


def net_str_to_net(address: str) -> Tuple[int, int, int, int]:
    number_ex = "([0-1][0-9][0-9]|[2][0-4][0-9]|[2][5][0-5]|[0-9][0-9]?)"
    regex = f"{number_ex}\.{number_ex}\.{number_ex}\.{number_ex}$"

    regex_result = re.match(regex, address)
    if not regex_result:
        raise NetAdressFormatError()

    return (
        int(regex_result.group(1)),
        int(regex_result.group(2)),
        int(regex_result.group(3)),
        int(regex_result.group(4)),
    )
