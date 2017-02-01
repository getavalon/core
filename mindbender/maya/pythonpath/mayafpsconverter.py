def mayafpsconverter(Sfps):
    condition = 0
    if Sfps == "":
        condition = 1
        return Sfps
    if Sfps == "15":
        condition = 1
        return "game"
    if Sfps == "24":
        condition = 1
        return "film"
    if Sfps == "25":
        condition = 1
        return "pal"
    if Sfps == "30":
        condition = 1
        return "ntsc"
    if Sfps == "48":
        condition = 1
        return "show"
    if Sfps == "50":
        condition = 1
        return "palf"
    if Sfps == "60":
        condition = 1
        return "ntscf"
    ERRORSTRING = "MINDBENDER_FPS has bad value in the bat file"
    if str(Sfps).isdigit() is False:
        cmds.confirmDialog(
        title="Enviroment variable error",
        message=ERRORSTRING,
        button="",
        defaultButton="",
        cancelButton="",
        dismissString="")
        return ""
    if condition == 0:
        Sfps = str(Sfps) + "fps"
        return Sfps
