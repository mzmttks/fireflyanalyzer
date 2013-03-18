import matplotlib.pyplot as plt
import matplotlib.cm as cm

# import matplotlib.patches as mpatches
#from matplotlib.collections import PatchCollection

import pickle
# import numpy
import sys

#import itertools
import masktest


def printObj(obj):
    for key in dir(obj):
        if key == "__doc__":
            continue
        print key, getattr(obj, key)

tag = sys.argv[1]
outdir = sys.argv[2]

# locd data
leds = pickle.load(open(outdir + "/ledmask" + tag + ".pickle"))
leds = leds["cogs"]
leds = sorted(leds, cmp=lambda a, b: cmp(-a[0] + a[1], -b[0] + b[1]))
frame = pickle.load(open(outdir + "/meanframe" + tag + ".pickle"))

print frame

# parmeters
width = 25
height = 25

fig = plt.figure()
axall = plt.subplot2grid((2, 3), (0, 0), colspan=2, rowspan=2)
axzoom = plt.subplot2grid((2, 3), (0, 2), colspan=1, rowspan=1)
axmask = plt.subplot2grid((2, 3), (1, 2), colspan=1, rowspan=1)

axall.imshow(frame, interpolation="nearest", cmap=cm.gray, aspect="auto")
pltall = axall.plot([l[0] for l in leds], [l[1] for l in leds], "wo")
axall.set_xlim([0, frame.shape[1]])
axall.set_ylim([0, frame.shape[0]])

axzoom.imshow(frame, interpolation="nearest", cmap=cm.gray, aspect="auto")
pltzoom = axzoom.plot([l[0] for l in leds], [l[1] for l in leds], "wo")
pltsel = axzoom.plot([], "ro")
axzoom.set_xlim([0, width - 1])
axzoom.set_ylim([0, height - 1])

plmask = axmask.imshow(
    frame, interpolation="nearest", cmap=cm.gray, aspect="auto")
axmask.set_xlim([0, width - 1])
axmask.set_ylim([0, height - 1])


class EventHandler:
    isChanged = True

    def __init__(self):
        self.isDragging = False

    def onpress(self, event):
        if event.inaxes == axall:
            self.isDragging = not(self.isDragging)
            if self.isDragging:
                axall.set_title("Zoomed window is moving")
            else:
                axall.set_title("Zoomed window is locked")

        elif event.inaxes == axzoom:
            self.isChanged = True
            pos = tuple(map(round, (event.xdata, event.ydata)))
            if event.button == 1:  # left click = add
                print "left:", pos
                leds.append(pos)
                for p in [pltzoom, pltall]:
                    p[0].set_xdata([l[0] for l in leds])
                    p[0].set_ydata([l[1] for l in leds])
                leds.sort(cmp=lambda a, b: cmp(-a[0] + a[1], -b[0] + b[1]))
            elif event.button == 3:  # right click == del
                print "right:", pos
                print leds
                for iled, led in enumerate(leds):
                    if abs(led[0] - pos[0]) < 2 and abs(led[1] - pos[1]) < 2:
                        del leds[iled]
                for p in [pltzoom, pltall]:
                    p[0].set_xdata([l[0] for l in leds])
                    p[0].set_ydata([l[1] for l in leds])
                print leds
                leds.sort(cmp=lambda a, b: cmp(-a[0] + a[1], -b[0] + b[1]))

            self.focusupdate(event)
        elif event.inaxes == axmask:
            # plmask.set_data(led2mask(frame, leds))
            if self.isChanged:
                self.maskUpdate()
                self.isChanged = False
            else:
                print "LEDs not changed"

        fig.canvas.draw()

    def maskUpdate(self):
        print "Generating mask ..."
        labeled, cog = masktest.generateLabeledMask(
            frame, [(l[1], l[0]) for l in leds])
        plmask.set_data(1.0 * labeled / labeled.max())
        self.labeled = labeled
        print "done!"

    def onmotion(self, event):
        if event.inaxes == axall and self.isDragging:
            axzoom.set_xlim(event.xdata - width / 2, event.xdata + width / 2)
            axzoom.set_ylim(event.ydata - width / 2, event.ydata + width / 2)
            axmask.set_xlim(event.xdata - width / 2, event.xdata + width / 2)
            axmask.set_ylim(event.ydata - width / 2, event.ydata + width / 2)
            fig.canvas.draw()

        elif event.inaxes == axzoom:
            self.focusupdate(event)
            fig.canvas.draw()

    def focusupdate(self, event):
        pos = tuple(map(round, (event.xdata, event.ydata)))
        focused = []
        for led in leds:
            if abs(led[0] - pos[0]) < 2 and abs(led[1] - pos[1]) < 2:
                focused.append(led)
        pltsel[0].set_xdata([f[0] for f in focused])
        pltsel[0].set_ydata([f[1] for f in focused])

pltred = None

event = EventHandler()
fig.canvas.mpl_connect('button_press_event', event.onpress)
fig.canvas.mpl_connect('motion_notify_event', event.onmotion)
event.maskUpdate()
plt.show()

pickle.dump({"masks": event.labeled,
             "cogs": leds}, open("pickle/ledmask-mod" + tag + ".pickle", "w"))
