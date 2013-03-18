import pickle
import pylab
import skimage.feature.peak
import skimage.morphology
import skimage.draw
import numpy
import itertools
from convexhull import convex_hull


def generateLabeledMask(img, peaklist=None):
    # calc background pixel value
    occur, middle = pylab.histogram(img.flatten(), 255)
    bgcolor = middle[occur.argmax() * 2]
    img[numpy.where(img < bgcolor)] = 0

    # extract peaks
    if peaklist is None:
        peaks = skimage.feature.peak.peak_local_max(
            img, min_distance=3, threshold_abs=0)
        peaklist = sorted(map(tuple, peaks),
                          cmp=lambda a, b: cmp(a[0], b[0]))
        cog = None
    else:
        cog = numpy.copy(peaklist)

    # calc mask for each peak
    output = numpy.zeros(img.shape)
    for ip, p in enumerate(peaklist):
        output += generateMask(img.copy(), p)
    output[numpy.where(output > 0)] = 1

    # label it
    labeled = skimage.morphology.label(output, 8)

    # calc cog
    if cog is None:
        cog = []
        print labeled
        for label in range(1, labeled.max() + 1):
            x, y = numpy.where(labeled == label)
            cog.append((y.mean(), x.mean()))
        print cog
    else:
        coglabels = [labeled[c[0], c[1]] for c in cog]
        setcoglabels = set(coglabels)
        if len(coglabels) != len(setcoglabels):
            [coglabels.remove(c) for c in setcoglabels]
            coglabels = set(coglabels)

            for c in coglabels:
                labeled = separateMask(labeled, c,
                                       [tmp for tmp in cog
                                        if labeled[tmp[0], tmp[1]] == c])
    return labeled, cog


def euclid(x, y):
    return numpy.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)


def separateMask(labeled, label, poses):
    x, y = numpy.where(labeled == label)
    labeled[numpy.where(labeled > label)] += len(poses) - 1
    for mask in zip(x, y):
        newlabel = numpy.array([euclid(pos, mask) for pos in poses]).argmin()
        labeled[mask[0], mask[1]] += newlabel

    return labeled


def generateMask(img, pos):
    def recursive(img, pos, thresh):
        if img[pos] >= thresh:
            img[pos] *= -1
            for x, y in itertools.product((-1, 0, 1), (-1, 0, 1)):
                if x == y == 0:
                    continue
                if abs(img[pos]) > img[(pos[0] + x, pos[1] + y)]:
                    recursive(img, (pos[0] + x, pos[1] + y), thresh)

    occur, middle = pylab.histogram(img.flatten(), 255)
    thresh = middle[occur.argmax() * 2]
    thresh = img[pos] * 0.3

    recursive(img, pos, thresh)
    img[numpy.where(img > 0)] = 0
    img[numpy.where(img < 0)] = 1
    one = numpy.array(numpy.where(img == 1))
    if len(one[0]) > 5:
        hull = convex_hull(one)
        img[skimage.draw.polygon(numpy.array([h[0] for h in hull]),
                                 numpy.array([h[1] for h in hull]))] = 1

    return img


if __name__ == "__main__":
    filename = "/n/rd0/mizumoto/ffa3_pickle/meanframe-011013-00008-trial1.pickle"
    mean = pickle.load(open(filename))

    labeled, cog = generateLabeledMask(mean)
    pylab.imshow(labeled, interpolation="nearest")
    for c in cog:
        print c
        pylab.plot(c[0], c[1], "o")
    pylab.colorbar()
    pylab.ylim([200, 900])
    pylab.xlim([200, 1200])
    pylab.show()
