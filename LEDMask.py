import pickle
import sys
import pylab
from masktest import generateLabeledMask

# If the first argument is demo, plot the result.
if "demo" in sys.argv:
    isShow = True
else:
    isShow = False

try:
    tag = sys.argv[1]
    outputdir = sys.argv[2]
except:
    sys.stderr.writelines("argument: tag outputdir")
    sys.exit(1)

mean = pickle.load(open(outputdir + "/meanframe" + tag + ".pickle"))
masks, cogs = generateLabeledMask(mean)

for icog, cog in enumerate(cogs):
    print icog, cog

pickle.dump({"masks": masks,
             "cogs": cogs},
            open(outputdir + "/ledmask" + tag + ".pickle", "w"))

if isShow:
    pylab.figure(1)
    # pylab.imshow(mean, interpolation="nearest")
    pylab.imshow(mean + masks, interpolation="nearest", cmap=pylab.cm.gray)

    for cog in cogs:
        pylab.plot(cog[0], cog[1], "o")

    pylab.xlim([0, mean.shape[1]])
    pylab.ylim([0, mean.shape[0]])

    pylab.show()
