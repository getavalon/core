import pyblish.api


class ValidateCurrentSaveFile(pyblish.api.ContextPlugin):
    """File must be saved before publishing"""

    label = "Validate File Saved"
    order = pyblish.api.ValidatorOrder - 0.1
    optional = True
    hosts = ["maya", "houdini"]

    def process(self, context):

        def houdini(variable):
            resitem = []
            for item in variable.split("\\"):
                resitem.append(str(item))
            resitem.reverse()
            return resitem[0]

        current_file = context.data["currentFile"]

        if "houdini" in pyblish.api.registered_hosts():
            current_file = houdini(current_file)

        unsaved_values = [
            # An unsaved file in Maya has this value.
            ".",

            # An unsaved file in Houdini has one of these values.
            "Root",
            "untitled.hip"
        ]

        is_saved = current_file not in unsaved_values

        assert is_saved, (
            "You haven't saved your file yet")
