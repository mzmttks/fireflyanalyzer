""" Frog Firefly Analyzer 3
  Analyzes the Firefly data
               (c) T. Mizumoto"""

import os
import exceptions


class Runner:
    params = {
        "filename": "00112.MTS",
        "outputdir": "pickle/",
        "starttime": 60 * 1000,
        "framesPerLoop": 10,
        "numOfLoops": 60,
        "skipframes": 10,
        "tag": "-20110617-frog04-00112",
        "readframes": 200,  # 70000
        "masksize": 5,
        "weightparam": 0.99,
        "gamma": 3.0,
        "threshold_abs": 0.3,
    }

    def setConfig(self, cfgname):
        for line in open(cfgname):
            if "#" in line:
                line = line[:line.find("#")]
            if len(line) <= 1:
                continue
            key, value = map(lambda x: x.strip(), line.split(":"))

            if key in self.params.keys():
                self.params[key] = type(self.params[key])(value)
            else:
                exceptions.ValueError(
                    "The type of %s must be %s (Input: %s)" % (
                        key, str(type(self.params[key])), str(type(value))
                    ))

    def __str__(self):
        out = "Configuration\n"

        for key in sorted(self.params.keys()):
            out += "\t %-20s:\t%s\n" % (key, str(self.params[key]))
        return out

    def run(self, isRun=[]):
        # MeanFrame.py
        cmd1 = "python MeanFrame.py"
        for key in ["filename", "starttime", "framesPerLoop",
                    "numOfLoops", "skipframes", "tag", "outputdir"]:
            cmd1 += " " + str(self.params[key])

        # LedMask.py
        cmd2 = "python LEDMask.py"
        for key in ["tag", "outputdir"]:
            cmd2 += " " + str(self.params[key])

        cmd5 = "python EditMask.py"
        for key in ["tag", "outputdir"]:
            cmd5 += " " + str(self.params[key])

        # TimeSeries.py
        cmd3 = "python TimeSeries.py"
        for key in ["filename", "tag", "readframes", "starttime",
                    "masksize", "weightparam", "gamma",
                    "threshold_abs", "outputdir"]:
            cmd3 += " " + str(self.params[key])

        # InteractionAnalysis.py

        # ViewResults.py
        cmd4 = "python ViewResults.py %s %s" % (
            self.params["outputdir"], self.params["tag"])

        for stage, cmd in enumerate([cmd1, cmd2, cmd5, cmd3, cmd4]):
            print cmd
            if stage + 1 in isRun:
                ret = os.system(cmd)
                if ret != 0:
                    return

if __name__ == "__main__":
    import os.path
    import sys

    # mean     : 300 frames, for each 90 frames (3 sec)
    # duration: 10 minutes = 60 * 10 * 30 = 18000[frames]
    # starttime: 0, 1, 2 [hour]

    if len(sys.argv) == 1:
        print """Frog Firefly Analyze 3 runner
usage:
    python run.py config [stage1 stage2 ...]
arguments:
    config  .cfg file that specifies the arguments.
    stage   The processing stages you want to run.
            Nothing: run all stages
            1      : mean frame calculation
            2      : LEDMask generation
            3      : Timeseries extraction
            4      : View extracted timeseries

            if you want to run only 2, run:
               > python run.py config.cfg 2
(c) T. Mizumoto
"""
        sys.exit()
    elif len(sys.argv) == 2:
        isRun = [1, 2, 3, 4, 5]
    elif len(sys.argv) > 2:
        isRun = map(int, sys.argv[2:])

    print isRun
    runner = Runner()
    runner.setConfig(sys.argv[1])
    print runner
    runner.run(isRun)

    # for d in sorted(glob.glob("/opt/frog/2013/*")):
    # # for d in sorted(glob.glob("/media/MyPass/2*")):
    #     if not(os.path.isdir(d)):
    #         continue
    #     for v in sorted(glob.glob(d + "/*.MTS")):
    #         tag = "-".join(v.split("/")[-2:]).split(".")[0]
    #         runner.params["filename"] = v

    #         for trial in range(3):
    #             starttime = trial * 60 * 60 * 30 + 60 * 30  # 1 hour
    #             runner.params["starttime"] = starttime
    #             runner.params["tag"] = "-" + tag + "-trial" + str(trial)

    #             runner.run(False)
