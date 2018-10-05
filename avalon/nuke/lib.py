import os
import contextlib
import nuke


@contextlib.contextmanager
def maintained_selection():
    # nuke = getattr(sys.modules["__main__"], "nuke", None)
    nodes = nuke.allNodes()
    previous_selection = [n.name()
                          for n in nodes
                          if n['selected'].value() is True]
    try:
        yield
    finally:
        # unselect all selection in case there is some
        [n['selected'].setValue(False) for n in nodes]
        # and select all previously selected nodes
        if previous_selection:
            [n['selected'].setValue(True)
             for n in nodes
             if n.name() in previous_selection]


def ls_img_sequence(dirPath, one=None):
    excluding_patterns = ['_broken_', '._', '/.', '/_']
    result = {}
    sortedList = []
    files = os.listdir(dirPath)
    for file in files:
        # print file
        for ex in excluding_patterns:
            file_path = os.path.join(dirPath, file).replace('\\', '/')
            if ex in file_path:
                continue
        try:
            prefix, frame, suffix = file.split('.')

            # build a dictionary of the sequences as {name: frames, suffix}
            #
            # eg beauty.01.tif ... beauty.99.tif  will convert to
            # { beauty : [01,02,...,98,99], tif }

            try:
                result[prefix][0].append(frame)
            except KeyError:
                # we have a new file sequence, so create a new key:value pair
                result[prefix] = [[frame], suffix]
        except ValueError:
            # the file isn't in a sequence, add a dummy key:value pair
            result[file] = file

    for prefix in result:
        if result[prefix] != prefix:
            frames = result[prefix][0]
            frames.sort()

            # find gaps in sequence
            startFrame = int(frames[0])
            endFrame = int(frames[-1])
            pad = len(frames[0])
            pad_print = '#' * pad
            idealRange = set(range(startFrame, endFrame))
            realFrames = set([int(x) for x in frames])
            # sets can't be sorted, so cast to a list here
            missingFrames = list(idealRange - realFrames)
            missingFrames.sort()

            # calculate fancy ranges
            subRanges = []
            for gap in missingFrames:
                if startFrame != gap:
                    rangeStart = startFrame
                    rangeEnd = gap - 1
                    subRanges.append([rangeStart, rangeEnd])
                startFrame = gap + 1

            subRanges.append([startFrame, endFrame])
            suffix = result[prefix][1]
            sortedList.append({
                'path':
                os.path.join(dirPath, '.'.join([prefix, pad_print,
                                                suffix])).replace('\\', '/'),
                'frames':
                subRanges
            })
        else:
            sortedList.append(prefix)
    if one:
        return sortedList[0]
    else:
        return sortedList


def add_publish_knob(node):
    if "publish" not in node.knobs():
        knob = nuke.Boolean_Knob("publish", "Publish")
        knob.setValue(False)
        node.addKnob(knob)
    return node
