import sys
import pickle
import multiprocessing as mp

import scipy.ndimage
import pylab

import skimage
import skimage.io
import skimage.color

# If the first argument is demo, plot the result.
if sys.argv[1] == "demo":
    isShow = True
else:
    isShow = False

# Parse arguments
try:
    filename = sys.argv[1]
    starttime = int(sys.argv[2])  # 60*1000
    framesPerLoop = int(sys.argv[3])  # 10
    numOfLoops = int(sys.argv[4])  # 10
    skipframes = int(sys.argv[5])  # 100
    tag = sys.argv[6]
    outputdir = sys.argv[7]
except:
    sys.stderr.writelines(
        "arguments: filename, starttime, framesPerLoop, \n"
        "            numOfLoops, skipframes, tag, outputdir\n")
    sys.exit(1)
# Read and seek the video
video = skimage.io.Video(filename, backend="opencv")
video.seek_time(starttime)


# convert a frame to float, maximum filtered, and gray one.
def conv(frame):
    return scipy.ndimage.maximum_filter(
        skimage.color.rgb2gray(skimage.img_as_float(frame)),
        size=3)

pool = mp.Pool()

totalFrames = framesPerLoop * numOfLoops


for i in range(numOfLoops):
    print "Loop", i, "reading frames..."
    frames = [video.get_index_frame(j)
              for j in range(0, framesPerLoop * skipframes, skipframes)]
    print range(0, framesPerLoop * skipframes, skipframes)
    print "Loop", i, "converting frames..."
    frames = pool.map(conv, frames)
    print "Loop", i, "calculating mean..."
    mean = sum(frames) / totalFrames

mean /= mean.max()
pickle.dump(mean, open(outputdir + "/meanframe" + tag + ".pickle", "w"))

mean = scipy.array(255 * mean, scipy.uint16)
skimage.io.imsave(outputdir + "/meanframe" + tag + ".png", mean)

if isShow:
    pylab.imshow(mean, cmap=pylab.cm.gray)
    pylab.show()
