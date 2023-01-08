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

    Cycle_Time: int = 170 #Restarts cycle when timer reaches this value
    ProductQty: int = 360 #Usually the number of pulses for a Tornado screw
    Product_Start: int = 45 #Used to trigger tornado, feeder or scale
    Belts_Start: int = 1 # Not to be changed, start of cycle, 0 value cause issue in the PLC
    Bag_Length: int = 250  #Bag length in pulses, triggers encoder stop command from PLC to drive,doesnt account for decel, 
    Jaws_Open: int = 160 #Triggers valve to open the jaws
    Jaws_Close: int = 70 #Triggers valve to close the jaws
    Knife_Advance: int = 150 #No longer need to be set, PLC uses sensor feedback to trigger knife, may need to be brought back later
    Vertical_Start: int = 80 #Triggers valve for vertical sealing bar closing
    Vertical_End: int = 155 #Triggers valve for vertical sealing bar opening
    Waiting_Time: int = 0  #Used in special recipes with batches, wont be configured in this app, set 0
    HmiAgitatorOption: int = 2
    Film_Unwind_Deriction: int = 0 #Sets the direction of the unwind motor, wont be configured in this app, set 0
    Photo_Registartion_On_Off: int = 0 #Decides wether the film will stop by encoder or photo cell, set from prompt on GUI
    Speed_Agitateur: int = 3000 #Sends speed to tornado agitator drive via modbus, wont be configured in this app, set to 3000
    Speed_VIS: int = 3000   #Sends speed to tornado screw drive via modbus, wont be configured in this app, set to 3000
    Delay_Start_Feeder: int = 1 #delays the start of feeders into tornados from level sensors, not set in this app for now, set to 1
    Delay_Stop_Feeder: int = 1000 #delays the stop of feeders into tornados from level sensors, not set in this app for now, set to 1
    ProductQty: int = 360
    Product_Start: int = 45
    Printer1_Start: int = 0 #Send the start printing command will use the printer 1 for intermittent printers
    Feeder_On_Off: int = 0 #Toggle Feeders on and off
    Printer2_Start: int = 0 #Send the start printing command will use the printer 2 for continous printers
    Ticketer_start: int = 0 #Trigger start of labeler/ticketer
    GAS_FLUSH_START: int = 0  #Trigger start of the flow of gas
    GAS_FLUSH_END: int = 0    #Trigger end of the flow of gas
    PRINTER1_ON_OFF: int = 0  #Toggle printer 1 on and off
    PRINTER2_ON_OFF: int = 0  #Toggle printer 2 on and off  
    TICKETER_ON_OFF: int = 0  #Toggle ticketer/labeler 1 on and off
    GASFLUSH_ON_OFF: int = 0
    Film_Unwind_Deriction: int = 0
    Alarm_Set_Jaws_Do_Not_Close: int = 50
    Alarm_Set_Bag_Too_Long: int = 160
    Alarm_Set_End_Of_Roll: int = 8
    Alarm_Set_Film_Unwind: int = 160
    Dump_Time: int = 30
    Delay_Start_PERFORATOR: int = 100 #Trigger valve for needle perforator
    Delay_Stop_PERFORATOR: int = 110 #Trigger valve for pulling needle perforator back
    Delay_Start_PUNCH: int = 100 #Trigger valve for hole punch perforator
    Delay_Stop_PUNCH: int = 110 #Trigger valve for pulling hole punch perforator back  


def cycle_calculator():
    recipe = Recipe()

    Jaws_Close_Delay = 15  # this will change based on the speed slider on gui
    Vertical_Start_Delay = 15  # this will change based on the speed slider on gui
    jaws_dwell = APP.ui.slider_dwell_time.value() #jaw dwell time will be adjusted as a function of the dwell slider
    vertical_dwell= APP.ui.slider_dwell_time.value() #vertical seal dwell time will be adjusted as a function of dwell slider
    total_cycle_delay = 15  # allow an end of cycle delay/physically for the jaws to move out of the way before cycle start

    Bag_Length_mm = APP.ui.input_bag_length.value()
    recipe.Bag_Length = int(Bag_Length_mm * 2)  # convert from input in mm to pulses used by plc

    belts_end = ((recipe.Bag_Length / V_MAX) + 0.5 * T_A) + 0.5 + T_D  # predict belt end time

    recipe.Jaws_Close = int(belts_end + Jaws_Close_Delay) 
    recipe.Jaws_Open = int(recipe.Jaws_Close + jaws_dwell)
    recipe.Cycle_Time = int(recipe.Jaws_Open + total_cycle_delay)

    recipe.Vertical_Start= int(belts_end+Vertical_Start_Delay)
    recipe.Vertical_End=int(recipe.Vertical_Start+vertical_dwell)

   #Print commands only for debugging the math
   
    print("Speed slider value", APP.ui.slider_speed.value())
    print("Dwell Slider value", vertical_dwell)
    print("Bag Length (pulses)", recipe.Bag_Length)
    print("Belts End: ", belts_end)
    print("Jaws Close: ", recipe.Jaws_Close)
    print("Vertical Start",recipe.Vertical_Start)
    print("Vertical Start",recipe.Vertical_End)
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
