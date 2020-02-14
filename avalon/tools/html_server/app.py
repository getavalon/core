import importlib
from wsgiref.simple_server import make_server

from avalon.vendor.bottle import route, template, run, WSGIRefServer
from threading import Thread



@route("/")
def index():
    """The entry point when accessing 'http://localhost:{port}'"""

    scripts_html = ""
    buttons_html = ""
    tools = {
        "contextmanager": "context",
        "workfiles": "workfiles",
        "creator": "create...",
        "loader": "load...",
        "publish": "publish...",
        "sceneinventory": "manage...",
        "projectmanager": "project manager",
    }
    for name, label in tools.items():
        scripts_html += """
<script type=text/javascript>
        $(function() {{
          $("a#{name}-button").bind("click", function() {{
            $.getJSON("/{name}_route",
                function(data) {{
              //do nothing
            }});
            return false;
          }});
        }});
</script>
""".format(name=name)
        buttons_html += (
            "<a href=# id={0}-button><button>{1}</button></a>".format(
                name, label.title()
            )
        )

    html = """
<!DOCTYPE html>
<html>
<head>
    <style>
      button {{width: 100%;}}
      body {{margin:0; padding:0; height: 100%;}}
      html {{height: 100%;}}
    </style>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js">
    </script>
    {0}
</head>
<body>
    {1}
</body>
</html>
""".format(scripts_html, buttons_html)

    return template(html)


@route("/<tool_name>_route")
def tool_route(tool_name):
    """The address accessed when clicking on the buttons."""
    tool_module = importlib.import_module("avalon.tools." + tool_name)
    tool_module.show()

    # Required return statement.
    return "nothing"


class thread_server(WSGIRefServer):
    def run(self, app):
        self.server = make_server(self.host, self.port, app)
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


def start_server(port):
    """Starts the Bottle server at 'http://localhost:{port}'"""
    server = thread_server(host="localhost", port=port)
    Thread(target=run, kwargs={"server": server}).start()
    return server
