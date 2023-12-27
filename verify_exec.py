import os
import glob
import re

files = glob.glob("*.o*")
files.sort()

for file in files:
    id = file.split(".")[2]

    success = False

    for line in open(file, "r"):
        if re.search("finished", line):
            success = True
            break

    if not success:
        print("WRONG:", id)

