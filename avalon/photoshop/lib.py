import json

import requests


PHOTOSHOP_URL = "http://127.0.0.1:3000"


def send_extendscript(code):
    """
    Send some ExtendScript code to photoshop and wait for the returning value
    :param code: (str) plain text ExtendScript code
    :return: (any) depend on the returned value
    """

    # Send code to photoshop. Adding try statement to prevent error popup
    # message locking photoshop UI.
    payload = {
        "to_eval": (
            "try{\n" +
            code +
            "\n}catch(e){e.error=true;ExtendJSON.stringify(e)}"
        )
    }
    response = requests.post(PHOTOSHOP_URL, json=payload)

    # handle response
    try:
        response_decoded = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        return response.text

    # handle error from extend script
    if (isinstance(response_decoded, dict) and
            "error" in response_decoded and
            response_decoded["error"] is True):
        raise ExtendScriptError(response_decoded)

    return response_decoded


class ExtendScriptError(Exception):
    """
    Exception used to handle error object coming from a try statement in ES
    """
    def __init__(self, error_obj):
        msg = "\n{name} at line {line} : {message}".format(**error_obj)
        # add previous, current and next code line where the error is
        line = error_obj.get("line")
        source = error_obj.get("source").splitlines()
        if line != 1:
            msg += "\n {}\t{}".format(line-1, source[line-2])
        msg += "\n {}\t{}".format(line, source[line-1])
        if line != len(source):
            msg += "\n {}\t{}".format(line+1, source[line])
        # previous line
        super(ExtendScriptError, self).__init__(msg)
