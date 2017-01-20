# validate_pipeline_filesaved.py
import pyblish.api

# from os.path import splitext


class ValidateCurrentSaveFile(pyblish.api.ContextPlugin):

    """
     ~ Validates if you have saved your application savefile yet ?
    """

    label = "Saved file"
    order = pyblish.api.ValidatorOrder - 0.1
    optional = True

    def process(self, context):

        def houdini(variable):
            resitem = []
            for item in variable.split("\\"):
                resitem.append(str(item))
            resitem.reverse()
            return resitem[0]

        savefileFromContext = []
        # for backward compatible reasons there are two values collected bellow
        savefileFromContext.append(str(context.data["current_file"]))
        savefileFromContext.append(str(context.data["currentFile"]))
        # for houdini sake we allter the context before use in this tool
        savefileFromContext.append(houdini(str(context.data["currentFile"])))
        # savefileFromContext.append()

        # reset if statement variable
        invalid = True

        savefilepattern = []
        # these are the patterns that are tested by the later if condition
        savefilepattern.append("Root")
        savefilepattern.append(".")
        savefilepattern.append("untitled.hip")
        # savefilepattern.append()

        # self.log.debug(invalid)
        for apppatern in savefilepattern:
            for appfile in savefileFromContext:
                if (str(appfile) == str(apppatern)):
                    invalid = False
                    # self.log.debug(str(appfile) + str(apppatern))
        # self.log.debug(invalid)
        # self.log.info(invalid)
        assert invalid, (
            "You haven't saved your file yet")
