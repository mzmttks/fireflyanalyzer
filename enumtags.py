import glob
import sys

for pickle in sorted(glob.glob(sys.argv[1] + "/timeseries_bin*.pickle")):
    print "python ViewResults.py",
    print sys.argv[1] + "/",
    print pickle.split("bin")[1].split(".pickle")[0]


for pickle in sorted(glob.glob(sys.argv[1] + "/ledmask*.pickle")):
    if "-mod" in pickle:
        continue
    print "python EditMask.py",
    print pickle.split("ledmask")[1].split(".pickle")[0]
