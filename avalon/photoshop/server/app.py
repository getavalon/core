import importlib

from avalon.vendor.bottle import route, template, run


@route("/")
def index():
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
    tool_module = importlib.import_module("avalon.tools." + tool_name)
    tool_module.show()

    # Required return statement.
    return "nothing"


def start_server():
    run(host="localhost", port=5000)


if __name__ == "__main__":
    start_server()
