import os
from . import app

with app.application():
    app.show(root=os.path.expanduser("~"),
             load=lambda name: None)
