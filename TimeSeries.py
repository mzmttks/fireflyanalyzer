import pickle
import sys

import numpy
try:
    isPylab = True
    import pylab
except:
    isPylab = False

import skimage.io
import skimage.feature

if sys.argv[1] == "demo":
    isShow = True
else:
    isShow = False

try:
    filename = sys.argv[1]
    tag = sys.argv[2]
    readframes = int(sys.argv[3])  # 70000
    starttime = int(sys.argv[4])  # 60 * 1000
    masksize = int(sys.argv[5])  # 20
    weightparam = float(sys.argv[6])  # 0.99
    gamma = float(sys.argv[7])  # 3.0
    threshold_abs = float(sys.argv[8])  # 0.3
    outputdir = sys.argv[9]
except:
    sys.stderr.writelines(
        "arguments:"
        "filename, tag, readframes, starttime, masksize"
        "weightparam, gamma, threshold_abs outputdir")

# read video and extracted LEDs
leds = pickle.load(open(outputdir + "/ledmask-mod" + tag + ".pickle"))
mean = pickle.load(open(outputdir + "/meanframe" + tag + ".pickle"))
video = skimage.io.Video(filename, backend="opencv")
video.seek_time(starttime)

labelsize = len(leds["cogs"])
labelareas = [numpy.where(leds["masks"] == led)
              for led in range(1, labelsize + 1)]
labelmean = [mean[numpy.where(leds["masks"] == led)].mean()
             for led in range(1, labelsize + 1)]
timeseries = numpy.empty((labelsize, readframes))

# sum masked values
for i in range(readframes):
    print i, readframes, video.frame_count()
    frame = video.get()
    timeseries[:, i] = [numpy.sum(
        frame[labelarea], dtype=numpy.float32) / len(labelarea[0])
        # frame[labelarea], dtype=numpy.float32) / labelmean[il]
        for il, labelarea in enumerate(labelareas)]

timeseries = numpy.array(timeseries).transpose()
pickle.dump(timeseries,
            open(outputdir + "/timeseries_raw" + tag + ".pickle", "w"))

timeseries **= gamma
timeseries -= timeseries.mean(1)[:, numpy.newaxis]
timeseries = (timeseries - timeseries.min()) / timeseries.max()


calls = skimage.feature.peak.peak_local_max(
    timeseries, min_distance=2,
    threshold_abs=threshold_abs)
timeseries_bin = numpy.zeros(timeseries.shape)
for call in calls:
    timeseries_bin[call[0], call[1]] = 1

pickle.dump(timeseries,
            open(outputdir + "/timeseries" + tag + ".pickle", "w"))
pickle.dump(timeseries_bin,
            open(outputdir + "/timeseries_bin" + tag + ".pickle", "w"))

if isPylab and isShow:
    pylab.subplot(2, 1, 1)
    pylab.imshow(timeseries, interpolation="nearest")

    pylab.subplot(2, 1, 2)
    pylab.imshow(timeseries_bin, interpolation="nearest", cmap=pylab.cm.gray)

    pylab.show()
