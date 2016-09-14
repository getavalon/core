from maya import cmds


def hierarchy_from_string(hierarchy):
    parents = {}

    for line in hierarchy.split("\n"):
        if not line:
            continue

        name = line.strip()
        padding = len(line[:-len(name)])
        parents[padding] = name
    
        name = cmds.createNode("transform", name=name)
    
        for parent in sorted(parents):
            if parent < padding:
                cmds.parent(name, parents[parent])
