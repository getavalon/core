import os
import string

from collections import defaultdict, namedtuple


Results = namedtuple('Results', ['sorted', 'cyclic'])


def uniqify_ordered(seq):
    """Uniqify sequence whilst preserving order.

    See: https://stackoverflow.com/questions/480214/how-do-you-remove-
         duplicates-from-a-list-in-whilst-preserving-order

    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def partial_format(s, data, missing="{{{key}}}"):
    """Return string `s` formatted by `data` allowing a partial format

    Arguments:
        s (str): The string that will be formatted
        data (dict): The dictionary used to format with.

    Example:
        >>> partial_format("{d} {a} {b} {c} {d}", {'b': "and", 'd': "left"})
        'left {a} and {c} left'
    """

    class FormatDict(dict):
        """This supports partial formatting.

        Missing keys are replaced with the return value of __missing__.

        """
        def __missing__(self, key):
            return missing.format(key=key)

    formatter = string.Formatter()
    mapping = FormatDict(**data)
    return formatter.vformat(s, (), mapping)


def topological_sort(dependency_pairs):
    """Sort values subject to dependency constraints"""
    num_heads = defaultdict(int)  # num arrows pointing in
    tails = defaultdict(list)  # list of arrows going out
    heads = []  # unique list of heads in order first seen
    for h, t in dependency_pairs:
        num_heads[t] += 1
        if h in tails:
            tails[h].append(t)
        else:
            tails[h] = [t]
            heads.append(h)

    ordered = [h for h in heads if h not in num_heads]
    for h in ordered:
        for t in tails[h]:
            num_heads[t] -= 1
            if not num_heads[t]:
                ordered.append(t)
    cyclic = [n for n, heads in num_heads.items() if heads]
    return Results(ordered, cyclic)


def append_path(self, key, path):
    """Append *path* to *key* in *self*."""
    try:
        if path not in self[key]:
            self[key] = os.pathsep.join([self[key], str(path)])
    except KeyError:
        self[key] = str(path)
