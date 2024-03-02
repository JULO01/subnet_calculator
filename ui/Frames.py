from tkinter import *
from core.utils import (
    net_str_to_net,
    schraeger_str_or_net_str_to_net,
    NetAdressFormatError,
)
from core.subnet_calc import (
    NetAdress,
    SubnetInformationIn,
    SubnetInformationOut,
)
from typing import Callable, List


class GeneralInputFrame(Frame):
    """
    General input for the calculation:
    - Subnet Adress
    - Schraeger
    - Sorting
    - Number of Subnets
    """

    def __init__(
        self,
        parent: Tk,
        on_submit: Callable[[NetAdress, int], None],
        *args,
        **kwargs,
    ):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.on_submit = on_submit

        self.net_input_label = Label(
            self, text="Netz-Adresse:", font=("Arial", 12)
        )
        self.net_input_label_error = Label(
            self,
            text="Netz-Adresse ist nicht korrekt",
            font=("Arial", 12),
            fg="red",
        )
        self.net_input_entry = Entry(self, width=15, font=("Arial", 12))

        self.schraeger_label = Label(
            self, text="Schraeger:", font=("Arial", 12)
        )
        self.schraeger_label_error = Label(
            self,
            text="Schraeger ist nicht korrekt",
            font=("Arial", 12),
            fg="red",
        )
        self.schraeger_entry = Entry(self, width=15, font=("Arial", 12))

        self.sorting_label = Label(
            self, text="Sortierung:", font=("Arial", 12)
        )

        self.sorting_option = StringVar(value="desc")
        self.sorting_radio1 = Radiobutton(
            self,
            text="Absteigend",
            variable=self.sorting_option,
            value="desc",
            font=("Arial", 12),
        )
        self.sorting_radio2 = Radiobutton(
            self,
            text="Aufsteigend",
            variable=self.sorting_option,
            value="asc",
            font=("Arial", 12),
        )
        self.sorting_radio3 = Radiobutton(
            self,
            text="Keine Sortierung",
            variable=self.sorting_option,
            value="none",
            font=("Arial", 12),
        )

        self.number_of_subnets_label = Label(
            self, text="Anzahl der Subnetze:", font=("Arial", 12)
        )
        self.number_of_subnets_label_error = Label(
            self,
            text="Anzahl der Subnetze muss eine Ganzzahl sein.",
            font=("Arial", 12),
            fg="red",
        )
        self.number_of_subnets_entry = Entry(
            self, width=15, font=("Arial", 12)
        )

        self.submit_button = Button(
            self, text="Bestätigen", font=("Arial", 12), command=self.submit
        )

    def display(self):
        self.net_input_label.grid(row=0, column=0)
        self.net_input_entry.grid(row=0, column=1)

        self.schraeger_label.grid(row=2, column=0)
        self.schraeger_entry.grid(row=2, column=1)

        self.sorting_label.grid(row=5, column=0)
        self.sorting_radio1.grid(row=4, column=1, sticky=W)
        self.sorting_radio2.grid(row=5, column=1, sticky=W)
        self.sorting_radio3.grid(row=6, column=1, sticky=W)

        self.number_of_subnets_label.grid(row=7, column=0)
        self.number_of_subnets_entry.grid(row=7, column=1)

        self.submit_button.grid(row=9, column=1)

        self.pack()

    def submit(self):
        validationError = False
        try:
            net_str_to_net(self.net_input_entry.get())
            self.net_input_label_error.grid_forget()
        except NetAdressFormatError:
            self.net_input_label_error.grid(row=1, column=1)
            validationError = True

        try:
            schraeger_str_or_net_str_to_net(self.schraeger_entry.get())
            self.schraeger_label_error.grid_forget()
        except NetAdressFormatError:
            self.schraeger_label_error.grid(row=3, column=1)
            validationError = True

        try:
            numer_of_nets = int(self.number_of_subnets_entry.get())
            self.number_of_subnets_label_error.grid_forget()
        except ValueError:
            self.number_of_subnets_label_error.grid(row=8, column=1)
            return

        if validationError:
            return

        net = NetAdress(self.net_input_entry.get(), self.schraeger_entry.get())

        self.on_submit(net, numer_of_nets)
        self.destroy()


class SubnetInInfoFrame(Frame):
    """
    Class for Single Subnet Input
    - Number of hosts
    """

    def __init__(self, parent: Frame, name: str | int):
        Frame.__init__(self, parent)

        self.valid = False
        self.name = name

        self.number_hosts_label = Label(
            self, text=f"Anzahl hosts von Net {name}: ", font=("Arial", 12)
        )
        self.number_hosts_error_label = Label(
            self, text=f"Fehlerhafte eingabe. ", font=("Arial", 12), fg="red"
        )

        self.number_hosts_entry = Entry(self, width=15, font=("Arial", 12))

    def display(self):
        self.number_hosts_label.grid(row=0, column=0)
        self.number_hosts_entry.grid(row=0, column=1)

        self.pack()

    def submit(self):
        try:
            self.number_hosts = int(self.number_hosts_entry.get())
            if self.number_hosts < 1:
                raise ValueError
            self.number_hosts_error_label.grid_forget()
            self.valid = True
        except ValueError:
            self.number_hosts_error_label.grid(row=1, column=1)


class SubnetInInfoWrapper(Frame):
    def __init__(
        self,
        parent,
        number_nets: int,
        on_submit: Callable[[List[SubnetInformationIn]], None],
    ):
        Frame.__init__(self, parent)
        self.on_submit = on_submit

        self.input_frames = [
            SubnetInInfoFrame(self, i) for i in range(1, number_nets + 1)
        ]

        self.submit_button = Button(
            self, text="Bestätigen", font=("Arial", 12), command=self.submit
        )

        self.number_nets = number_nets

    def display(self):
        for frame in self.input_frames:
            frame.display()
        self.submit_button.pack()
        self.pack()

    def submit(self):
        for frame in self.input_frames:
            frame.submit()

        if False in [net.valid for net in self.input_frames]:
            return

        inputs = [
            SubnetInformationIn(
                host_amount=net.number_hosts, name=str(net.name)
            )
            for net in self.input_frames
        ]

        self.destroy()
        self.on_submit(inputs)


class SubnetInfoOutFrame(Frame):
    def __init__(self, parent, net_out: SubnetInformationOut):
        Frame.__init__(self, parent)
        self.heading = Label(
            self, text=f"Netz {net_out.name}:", font=("Arial", 16)
        )

        self.net_label = Label(self, text="Net adress: ")
        self.net = Label(self, text=net_out.net_address)
        self.mask_label = Label(self, text="Subnet Mask: ")
        self.mask = Label(self, text=net_out.subnet_mask)

    def display(self):
        self.heading.grid(row=0, column=0)

        self.net_label.grid(row=1, column=1)
        self.net.grid(row=1, column=2)

        self.mask_label.grid(row=2, column=1)
        self.mask.grid(row=2, column=2)

        self.pack()


class SubnetInfoOutWrapperFrame(Frame):
    def __init__(self, parent, nets_out: List[SubnetInformationOut]):
        Frame.__init__(self, parent)
        self.net_out_frames = [SubnetInfoOutFrame(self, n) for n in nets_out]
        pass

    def display(self):
        for net in self.net_out_frames:
            net.display()
        self.pack()
