from mindbender import maya


class AbcLoader(maya.Loader):
    """Specific loader of Alembic for the mindbender.animation family"""

    families = ["mindbender.animation"]
    representations = ["abc"]

    def process(self, context):
        from maya import cmds

        cmds.loadPlugin("AbcImport.mll", quiet=True)

        nodes = cmds.file(
            self.fname,
            namespace=self.namespace,

            # Prevent identical alembic nodes
            # from being shared.
            sharedReferenceFile=False,

            groupReference=True,
            groupName=self.namespace + ":" + self.name,
            reference=True,
            returnNewNodes=True
        )

        return nodes


class CurvesLoader(maya.Loader):
    """Specific loader of Curves for the mindbender.animation family"""

    families = ["mindbender.animation"]
    representations = ["curves"]

    def process(self, context):
        from maya import cmds
        from mindbender import maya

        cmds.loadPlugin("atomImportExport.mll", quiet=True)

        rig = context["representation"]["dependencies"][0]
        container = maya.load(rig,
                              name=self.name,
                              namespace=self.namespace,

                              # Skip creation of Animation instance
                              post_process=False)

        try:
            control_set = next(
                node for node in cmds.sets(container, query=True)
                if node.endswith("controls_SET")
            )
        except StopIteration:
            raise TypeError("%s is missing controls_SET")

        cmds.select(control_set)
        options = ";".join([
            "",
            "",
            "targetTime=3",
            "option=insert",
            "match=hierarchy",
            "selected=selectedOnly",
            "search=",
            "replace=",
            "prefix=",
            "suffix=",
            "mapFile=",
        ])

        with maya.maintained_selection():
            cmds.select(
                control_set,
                replace=True,

                # Support controllers being embedded in
                # additional selection sets.
                noExpand=False
            )

            nodes = cmds.file(
                self.fname,
                i=True,
                type="atomImport",
                renameAll=True,
                namespace=self.namespace,
                options=options,
                returnNewNodes=True,
            )

        return nodes + [container]


class HistoryLoader(maya.Loader):
    """Specific loader of Curves for the mindbender.animation family"""

    families = ["mindbender.animation"]
    representations = ["history"]

    def process(self, context):
        raise NotImplementedError("Can't load history yet.")
