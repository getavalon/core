from win32com.client import Dispatch

from . import server


app = Dispatch("Photoshop.Application")


def start_server():
    server.app.start_server()



    """
