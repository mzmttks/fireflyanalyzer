import sys
import pickle
import matplotlib.pyplot as pyplot
import matplotlib.widgets
import numpy
import pylab
import scipy.ndimage
import scipy.signal

try:
    import skimage.morphology as morph
    import skimage.filter
    import skimage.feature.peak
    isSkimage = True
except:
    isSkimage = False

try:
    path = sys.argv[1] + "/"
    tag = sys.argv[2]
except:
    sys.stderr.writelines("arguments: path, tag")
    sys.exit()


class ResultContainer:
    def __init__(self, path, tag, kind):
        """
        read pickle data.
        this method ensures that the size is (A, B) where A < B.
        """
        if not(kind == ""):
            kind = "_" + kind
        self.tsname = path + "timeseries" + kind + tag + ".pickle"
        self.data = pickle.load(open(self.tsname))

        if self.data.shape[0] > self.data.shape[1]:
            self.data = self.data.transpose()

    def save(self):
        pickle.dump(self.data, open(self.tsname, "w"))

    def normalize(self):
        self.data -= self.data.min()
        self.data /= self.data.max()

    def preprocessing(self):
        self.data = self.data[:, 100:]  # remove first 100 frames.
        self.data -= self.data.mean(1)[:, numpy.newaxis]
        self.normalize()

    def enhance(self):
        self.data -= scipy.ndimage.minimum_filter(
            self.data, footprint=morph.diamond(4))

        # for i in range(self.data.shape[0]):
        #     self.data[i, :] = scipy.signal.medfilt(self.data[i, :], 5)

    def plot(self, place, peaks=None):
        self.ax = pyplot.subplot2grid((3, 3), (place, 0), colspan=2)
        self.ax.set_xlim([-0.5, width - 0.5])
        self.ax.set_ylim([-0.5, self.data.shape[0] - 0.5])

        self.axsum = pyplot.subplot2grid((3, 3), (place, 2))
        self.axsum.set_ylim([0, self.data.shape[0]])
        self.axsum.set_xlim([0, 0.5])

        self.pl = self.ax.imshow(self.data[:, 0:width],
                                 interpolation="nearest",
                                 cmap=pylab.cm.gray,
                                 aspect="auto",
                                 vmax=1, vmin=0)
        self.plsum = self.axsum.plot(self.data[:, 0:width].mean(1),
                                     range(self.data.shape[0]), "k-o")

        self.setlabel(0)

        if peaks:
            self.peaks = peaks
            peaksx, peaksy = numpy.where(peaks.data[:, 0:width] > 0)
            self.plpeak = self.ax.plot(peaksy, peaksx, "r.")

    def setlabel(self, time):
        xticks = range(0, width + 1, 20)
        xticklabels = map(lambda x: "%.1f" % x,
                          numpy.arange(time, (time + width + 20), 20) / fps)
        self.ax.set_xticks(xticks)
        self.ax.set_xticklabels(xticklabels)

    def update(self, use_range, time):
        self.pl.set_data(self.data[:, use_range])
        self.plsum[0].set_data(self.data[:, use_range].mean(1),
                               range(self.data.shape[0] - 1, -1, -1))
        self.setlabel(time)

        if hasattr(self, "peaks"):
            peaksx, peaksy = numpy.where(self.peaks.data[:, use_range] > 0)
            print peaksy
            self.plpeak[0].set_data([0, 1, 2], [0, 1, 2])

# parameter
width = 11
fps = 1.0

# open data
data_raw = ResultContainer(path, tag, "raw")
data_out = ResultContainer(path, tag, "")
data_bin = ResultContainer(path, tag, "bin")

# maip data
data_raw.preprocessing()
data_out.preprocessing()
data_bin.preprocessing()

# copy
data_out.data = data_raw.data.copy()
data_out.enhance()
data_out.normalize()

isUsePeakPicker = False
if isUsePeakPicker:
    threshold_abs = 0.30
    calls = skimage.feature.peak.peak_local_max(
        data_out.data, min_distance=3,
        threshold_abs=threshold_abs)
    data_bin.data = numpy.zeros(data_raw.data.shape)
    for call in calls:
        data_bin.data[call[0], call[1]] = data_out.data[call[0], call[1]]
else:
    winsize = 2
    data_bin.data = numpy.zeros(data_raw.data.shape)
    for x in range(winsize, data_out.data.shape[0] - winsize - 1):
        for y in range(winsize, data_out.data.shape[1] - winsize - 1):
            submat = data_out.data[(x - winsize): (x + winsize + 1),
                                   (y - winsize): (y + winsize + 1)]
            argmax = numpy.unravel_index(submat.argmax(), submat.shape)
            if argmax == (winsize, winsize):
                data_bin.data[x, y] = 1
# make figure
fig = pyplot.figure()
data_raw.plot(0)
data_out.plot(1, data_bin)
data_bin.plot(2)

# slider
axtime = pyplot.axes([0.1, 0.03, 0.80, 0.03])
stime = matplotlib.widgets.Slider(
    axtime, 'Time', 0, data_bin.data.shape[1] - width, valinit=0, valfmt="%d")


class updater:
    def __init__(self):
        self.prevtime = 0

    def update(self, val):
        time = int(stime.val)
        if time == self.prevtime:
            return

        use_range = numpy.arange(time, time + width - 1)
        data_raw.update(use_range, time)
        data_out.update(use_range, time)
        data_bin.update(use_range, time)
        pyplot.draw()
        self.prevtime = time

u = updater()
stime.on_changed(u.update)
pyplot.show()

data_bin.save()
