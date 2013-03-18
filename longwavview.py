import sys
import numpy
import matplotlib.pyplot
import matplotlib.widgets
import matplotlib.mlab
import scikits.audiolab


# parameter
filename = sys.argv[1]
width = 100
NFFT = 512
noverlap = 256

# open wav and calculate spectrogram
wav, fs, fmt = scikits.audiolab.wavread(sys.argv[1])
spec = matplotlib.mlab.specgram(wav, NFFT=NFFT, noverlap=noverlap, Fs=fs)[0]
spec = numpy.log10(numpy.flipud(spec))

# make figure
fig = matplotlib.pyplot.figure()
ax_spec = fig.add_subplot(1, 1, 1)
pl_spec = ax_spec.imshow(spec[:, 0:width], interpolation="nearest")

# make slider
axtime = matplotlib.pyplot.axes([0.1, 0.03, 0.80, 0.03])
stime = matplotlib.widgets.Slider(
    axtime, 'Time', 0, spec.shape[1] - width, valinit=0, valfmt="%d")


# update callback and registor it.
class updater:
    def __init__(self):
        self.prevtime = 0

    def update(self, val):
        time = int(stime.val)
        if time == self.prevtime:
            return
        pl_spec.set_data(spec[:, (time):(time + width - 1)])
        ax_spec.set_xticks(range(0, width, 20))
        ax_spec.set_xticklabels(range(time, (time + width + 20), 20))
        matplotlib.pyplot.draw()
        self.prevtime = time
u = updater()
stime.on_changed(u.update)

# start main loop
matplotlib.pyplot.show()
