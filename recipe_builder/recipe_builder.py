"""
Recipe Builder program
"""

from dataclasses import dataclass, asdict
from os import makedirs
import sys

from mako.template import Template
from PyQt5 import QtCore, QtGui, QtWidgets

from assets.main_window import Ui_RecipeBuilder


OUTPUT_DIR = "outputs"
OUTPUT_FILE = "output.xml"

V_MAX = 2.326  # Pulse/ms
T_A = 21.03  # miliseconds (accel period)
T_D = 21.03  # milliseconds (decel, copy accel for now)


class App:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = QtWidgets.QMainWindow()
        self.ui = Ui_RecipeBuilder()
        self.ui.setupUi(self.main_window)

    def show(self):
        self.main_window.show()
        self.app.exec()


APP = App()


@dataclass
class Recipe:
    """
    Define Variables used in the cycle, these variables will eventually need to be output to the XML file
    as the finished product, the names canot be changed, this is how they are called in the PLC
    """

    Cycle_Time: int = 170
    ProductQty: int = 360
    Product_Start: int = 45
    Belts_Start: int = 1
    Bag_Length: int = 250  # 101.2 This is in pulse, required for PLC but not user input
    Jaws_Open: int = 160
    Jaws_Close: int = 70
    Knife_Advance: int = 150
    Vertical_Start: int = 80
    Vertical_End: int = 155
    Waiting_Time: int = 0
    HmiAgitatorOption: int = 2
    Film_Unwind_Deriction: int = 0
    Photo_Registartion_On_Off: int = 0
    Speed_Agitateur: int = 3000
    Speed_VIS: int = 3000
    Delay_Start_Feeder: int = 1
    Delay_Stop_Feeder: int = 1000
    ProductQty: int = 360
    Product_Start: int = 45
    Printer1_Start: int = 0
    Feeder_On_Off: int = 0
    Printer2_Start: int = 0
    Ticketer_start: int = 0
    GAS_FLUSH_START: int = 0
    GAS_FLUSH_END: int = 0
    PRINTER1_ON_OFF: int = 0
    PRINTER2_ON_OFF: int = 0
    TICKETER_ON_OFF: int = 0
    GASFLUSH_ON_OFF: int = 0
    Film_Unwind_Deriction: int = 0
    Alarm_Set_Jaws_Do_Not_Close: int = 50
    Alarm_Set_Bag_Too_Long: int = 160
    Alarm_Set_End_Of_Roll: int = 8
    Alarm_Set_Film_Unwind: int = 160
    Dump_Time: int = 30
    Delay_Start_PERFORATOR: int = 100
    Delay_Stop_PERFORATOR: int = 110
    Delay_Start_PUNCH: int = 100
    Delay_Stop_PUNCH: int = 110


def cycle_calculator():
    recipe = Recipe()

    jaws_close_delay = 15  # this will change based on the slider on gui
    Vertical_Start_Delay = 15  # this will change based on the slideron gui
    jaws_dwell = APP.ui.slider_dwell_time.value()
    total_cycle_delay = 15  # allow an end of cycle

    Bag_Length_mm = APP.ui.input_bag_length.value()
    recipe.Bag_Length = int(Bag_Length_mm * 2)  # convert from input in mm to pulses used by plc

    belts_end = ((recipe.Bag_Length / V_MAX) + 0.5 * T_A) + 0.5 + T_D  # predict belt end time

    recipe.Jaws_Close = int(belts_end + jaws_close_delay)
    recipe.Jaws_Open = int(recipe.Jaws_Close + jaws_dwell)
    recipe.Cycle_Time = int(recipe.Jaws_Open + total_cycle_delay)

    print("Belts End: ", belts_end)
    print("Jaws Close: ", recipe.Jaws_Close)
    print("Jaws Open: ", recipe.Jaws_Open)
    print("Total Cycle Time: ", recipe.Cycle_Time)

    output = Template(filename="recipe_builder/renderers/output.xml.mako").render(recipe=asdict(recipe))
    makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_DIR + "/" + OUTPUT_FILE, "w") as fd:
        fd.write(output)


def main():
    APP.ui.btn_generate.clicked.connect(cycle_calculator)
    APP.show()


if __name__ == "__main__":
    main()
