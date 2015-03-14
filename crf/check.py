# list files
# split each file to tabs and make sure it has always the same number

from os import walk

mypath = "sets/"
f = []
crf = 65
m3n = 27
num = crf
for (dirpath, dirnames, filenames) in walk(mypath):
    f.extend(filenames)
    break

for afile in f:
    for line in open(mypath+afile).readlines():
        if len(line.split("\t"))!=num:
            print "stop ", afile, len(line.split("\t"))
       