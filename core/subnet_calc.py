from pydantic import BaseModel
from typing import Tuple, List, Literal
from rich import print
from core.utils import *


class SubnetInformationIn(BaseModel):
    host_amount: int
    name: str


class SubnetInformationOut(BaseModel):
    name: str
    number_available_hosts: int
    net_address: str
    broadcast: str
    subnet_mask: str
    schraeger: int


class NetAdress:
    def __init__(self, address: str, schraeger_or_subnet_mask: str, take_subnet_space: bool = False):
        # Verifying the string inputs
        schraeger_str_or_net_str_to_net(schraeger_or_subnet_mask)
        net_str_to_net(address)
        _address = net_to_integer(net_str_to_net(address))
        _subnet_int = net_to_integer(schraeger_str_or_net_str_to_net(schraeger_or_subnet_mask))

        if take_subnet_space and _address & bit_not(_subnet_int) != 0:
            _address = _address >> (32 - schraeger_str_or_net_str_to_schraeger(schraeger_or_subnet_mask))
            _address = _address + 1
            _address = _address << (32 - schraeger_str_or_net_str_to_schraeger(schraeger_or_subnet_mask))

            address = net_to_net_str(integer_to_net(_address))


        self.address = address
        self.schraeger_or_subnet_mask: str = schraeger_or_subnet_mask

    def get_schraeger(self):
        return schraeger_str_or_net_str_to_schraeger(
            self.schraeger_or_subnet_mask
        )

    def get_subnet_mask(self):
        return schraeger_str_or_net_str_to_net(self.schraeger_or_subnet_mask)

    def get_address_tuple(self):
        return net_str_to_net(self.address)

    def get_broadcast(self) -> Tuple[int, int, int, int]:
        net_integer = net_to_integer(self.get_address_tuple())
        subnet_integer = net_to_integer(self.get_subnet_mask())
        broadcast_integer = net_integer | bit_not(subnet_integer)
        return integer_to_net(broadcast_integer)

    def get_next_net(self) -> Tuple[int, int, int, int]:
        broadcast_integer = net_to_integer(self.get_broadcast())
        next_net_integer = broadcast_integer + 1
        return integer_to_net(next_net_integer)

    def get_available_host_addresses(self) -> int:
        return 2 ** (32 - self.get_schraeger()) - 2

    def __str__(self):
        return f"Netz-Adresse: {self.address}, Subnetz-Maske: {self.get_subnet_mask()}, Broadcast: {net_to_net_str(self.get_broadcast())}"


def calculate_subnets(
    net_address: NetAdress,
    subnets: List[SubnetInformationIn],
    sort_nets: Literal["asc"] | Literal["desc"] | None = "desc",
) -> List[SubnetInformationOut]:
    if sort_nets:
        reverse = sort_nets == "desc"
        sorted_subnets = sorted(
            subnets, key=lambda net: net.host_amount, reverse=reverse
        )
    else:
        sorted_subnets = subnets

    _net_address = net_address.address

    result_nets: List[SubnetInformationOut] = []

    for net in sorted_subnets:
        schraeger = 32
        while (net.host_amount + 2) > 2 ** (32 - schraeger):
            schraeger -= 1

        resulting_net = NetAdress(_net_address, str(schraeger), take_subnet_space=True)
        _net_address = net_to_net_str(resulting_net.get_next_net())

        net_out = SubnetInformationOut(
            net_address=resulting_net.address,
            broadcast=net_to_net_str(resulting_net.get_broadcast()),
            subnet_mask=net_to_net_str(resulting_net.get_subnet_mask()),
            schraeger=resulting_net.get_schraeger(),
            name=net.name,
            number_available_hosts=resulting_net.get_available_host_addresses(),
        )
        result_nets.insert(0, net_out)
        result_nets = sorted(result_nets, key=lambda net: net_str_to_net(net.net_address))

    return result_nets


if __name__ == "__main__":
    subnet_info_in = []
    subnets_in_received = False
    net_received = False
    mask_received = False
    sorting = None
    sorting_received = False
    host_net = ""
    schraeger_or_net_str = ""

    while not net_received:
        try:
            host_net = input("\nNetz-Adresse: ")
            net_str_to_net(host_net)

        except NetAdressFormatError as e:
            continue

        net_received = True

    while not mask_received:
        try:
            schraeger_or_net_str = input(
                f"Schraeger oder Subnetz-Maske von {host_net}: "
            )
            schraeger_str_or_net_str_to_net(schraeger_or_net_str)

        except NetAdressFormatError as e:
            continue

        mask_received = True

    print("Sortierung nach Anzahl Hosts wählen: \n")
    print("\t0: Absteigend (default, empty input works as well)")
    print("\t1: Aufsteigend")
    print("\t2: keine Sortierung\n")

    sort_input = input()

    if sort_input == "0":
        sorting = "desc"
    elif sort_input == "1":
        sorting = "asc"
    elif sort_input == "2":
        sorting = None
    else:
        sorting = "desc"

    while not subnets_in_received:
        try:
            number_nets = int(input("Wie viele Subnets? "))

            for i in range(0, number_nets):
                name = input(f"\nName des {i+1}. Subnets: ")
                n_hosts = int(
                    input(
                        f"Anzahl hosts (ohne Netz und Broadcast) in {name}: "
                    )
                )

                subnet_info_in.append(
                    SubnetInformationIn(host_amount=n_hosts, name=name)
                )

        except Exception as e:
            print("Eingaben bitte richtig machen Bro")
            continue

        subnets_in_received = True

    available_net = NetAdress(address=host_net, schraeger_or_subnet_mask=schraeger_or_net_str)
    resulting_nets = calculate_subnets(
        available_net, subnet_info_in, sort_nets=sorting
    )

    resulting_nets = sorted(resulting_nets, key=lambda net: net.schraeger)

    print(resulting_nets)

    not_assigned = 2 ** (32 - schraeger_str_or_net_str_to_schraeger(schraeger_or_net_str))
    not_assigned_string = f"2^(32-{schraeger_str_or_net_str_to_schraeger(schraeger_or_net_str)})"


    last_net_broadcast = net_to_integer(net_str_to_net(resulting_nets[0].broadcast))
    available_net_broadcast = net_to_integer(available_net.get_broadcast())

    if(last_net_broadcast > available_net_broadcast):
        print("\nWarnung: Die Subnets passen nicht in das gegebene Netz!\n")

    print("\nNicht zugeordnete IP-Adressen nach den Subnets: ")

    for net in resulting_nets:
        not_assigned_string += f" - 2^(32-{net.schraeger})"
        not_assigned -= 2 ** (32 - net.schraeger)

    not_assigned_string += f" = {not_assigned}"

    print(not_assigned_string)


"""
Eingabe:

    192.168.0.0 / 24

    4 Subnets:
        net1: 20 Clients
        net2: 22 Clients
        net3: 29 Clients
        net4: 12 Clients


    ---> 
    [{net: 192.168.0.0, subnet_mask: 255.255.255.224, broadcast: 192.168.0.31},
     {net: 192.168.0.32, subnet_mask: 255.255.255.224, broadcast: 192.168.0.63},
     {net: 192.168.0.64, subnet_mask: 255.255.255.224, broadcast: 192.168.0.95},
     {net: 192.168.0.96, subnet_mask: 255.255.255.224, broadcast: 192.168.0.127},
     ]

"""
