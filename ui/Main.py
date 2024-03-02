from ui.Frames import GeneralInputFrame, SubnetInInfoWrapper, SubnetInfoOutWrapperFrame
from core.subnet_calc import NetAdress, SubnetInformationIn, calculate_subnets
from core.utils import *
from tkinter import *
from typing import List


class Main:
    def __init__(self, geometry: str = "800x600"):
        self.root = Tk()
        self.root.geometry(geometry)
        self.general_input = GeneralInputFrame(self.root, on_submit=self.show_net_inputs)
        self.general_input.display()
        self.net = None

        self.net_input_frames = None

    def show_net_inputs(self, net: NetAdress, number_nets: int):
        self.net = net
        self.net_input_frame_wrapper = SubnetInInfoWrapper(self.root, number_nets, self.show_result)
        self.net_input_frame_wrapper.display()

    def show_result(self, nets_in: List[SubnetInformationIn]):
        if not self.net:
            print("Net is not defined")
            return

        result = calculate_subnets(net_address=self.net, subnets=nets_in)
        result_frame = SubnetInfoOutWrapperFrame(self.root, nets_out=result)
        result_frame.display()
        pass

    def run(self):
        self.root.mainloop()
