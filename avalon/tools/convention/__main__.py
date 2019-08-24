import argparse

from avalon.vendor.Qt import QtWidgets

from . import model, view

parser = argparse.ArgumentParser()
parser.add_argument("fname", help="Absolute path to CONVENTION.md")

opts = parser.parse_args()

app = QtWidgets.QApplication([])

model = model.Main()
model.reset(opts.fname)
window = view.Window(model)
window.show()

app.exec_()
