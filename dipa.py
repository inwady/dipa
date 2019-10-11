# -*- coding: utf-8 -*-

import argparse
import re

from extractor import ascii_strings
from ipa_analyzer import IosIpa, print_info

parser = argparse.ArgumentParser()
parser.add_argument("ipapath", help="Absolute Path of the IPA file")

args = parser.parse_args()
ipafile_path = args.ipapath

ipa = IosIpa(ipa_path=ipafile_path)
build_info = ipa.buildInfo

print_info(build_info, ipa.name)

binary_buffer = ipa.open_binary_file().read()

print("Check binary {}".format(build_info.bundleExecutable))

path_pattern = r"^(\/Users.+\.(swift|m|c|h|cpp|hpp|jpg|png|car))$"

paths = []
for s in ascii_strings(binary_buffer, n=4):
    _, string = s.offset, s.s
    found = re.findall(path_pattern, string)
    if len(found) > 0:
        paths.append(found[0][0])


def parse_path_to_dict(paths):
    dirs = [path.split("/")[1:] for path in paths]

    root = {}
    for path_array in dirs:
        tmp = root
        for bit in path_array:
            if bit not in tmp:
                tmp[bit] = {}

            tmp = tmp[bit]

    return root


def print_tree(root, spaces=u"", isroot=True):
    for key in root:
        if len(spaces) > 6:
            print(spaces + u" ├─" + key)
            print_tree(root[key], spaces + u" │ ", isroot=False)
        elif isroot:
            print(spaces + u"├──" + key)
            print_tree(root[key], spaces + u"│ ", isroot=False)
        else:
            print(spaces + u" ──" + key)
            print_tree(root[key], spaces + u"    ", isroot=False)


root = parse_path_to_dict(paths)
print_tree(root)

ipa.delete_tmp()
