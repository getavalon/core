"""
Utility scripts to compile the qrc file. The script will
attempt to compile the qrc file using the following tools:
    - rcc
    - pyside-rcc
    - pyrcc4

Delete the compiled files that you don't want to use
manually after running this script.
"""
import os


def compile_all():
    """
    Compile style.qrc using rcc, pyside-rcc and pyrcc4
    """
    # print("Compiling for Qt: style.qrc -> style.rcc")
    # os.system("rcc style.qrc -o style.rcc")
    print("Compiling for PyQt4: style.qrc -> pyqt_style_rc.py")
    os.system("pyrcc4 -py3 style.qrc -o pyqt_style_rc.py")
    print("Compiling for PyQt5: style.qrc -> pyqt5_style_rc.py")
    os.system("pyrcc5 style.qrc -o pyqt5_style_rc.py")
    print("Compiling for PySide: style.qrc -> pyside_style_rc.py")
    os.system("pyside-rcc -py3 style.qrc -o pyside_style_rc.py")


if __name__ == "__main__":
    compile_all()
