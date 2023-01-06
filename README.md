# Recipe Builder

## Run App
run
`python recipe_builder/recipe_builder.py`
from the root of this repo

## QT -> Python Conversion commands

### UI file:
run
`pyuic5 Recipe_builder_GUI.ui -o ../recipe_builder/assets/main_window.py --import-from=assets --resource-suffix=`
from the `qt` dir

### Resource files:
run
`assets/resources.qrc -o ../recipe_builder/assets/resources.py`
from the `qt` dir, for each resource file (if there end up being more than one)
