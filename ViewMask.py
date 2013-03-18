import pylab
import sys
import pickle

tag = sys.argv[1]

leds = pickle.load(open("pickle/ledmask" + tag + ".pickle"))
frame = pickle.load(open("pickle/meanframe" + tag + ".pickle"))
frame /= frame.max()

frame **= 1.5


print leds
pylab.imshow(frame, interpolation="nearest", cmap=pylab.cm.gray)
for led in leds:
    pylab.plot(led[1], led[0], "wo")
pylab.colorbar()

pylab.xlim([0, frame.shape[1]])
pylab.ylim([0, frame.shape[0]])
pylab.show()
