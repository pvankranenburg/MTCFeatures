import gzip
import json
import os
from pathlib import PurePath, Path

from collections import defaultdict
from itertools import filterfalse

__modpath = Path(__file__).resolve().parent

# Example use:

# This selects songs from ANN background corpus, with year > 1850 and type 'vocal'
# and divides those in train and test set making sure the split is at the level of tunefamily

# dl = MTCDataLoader('mtcfsinst_sequences.jsonl')
# seqs = dl.applyFilters(
#    [
#        {'mfilter':'ann_bgcorpus'},
#        {'mfilter':('afteryear',1850)},
#        {'mfilter':'vocal'},
#        {'mfilter':'labeled'},
#        {'mfilter':'freemeter', 'invert':True}
#    ]
# )

def say():
    print(__modpath)

datapaths = {
    'MTC-ANN-2.0.1'    : PurePath(__modpath, 'data', 'MTC-ANN-2.0.1_sequences.jsonl.gz'),
    'MTC-FS-INST-2.0'  : PurePath(__modpath, 'data', 'MTC-FS-INST-2.0_sequences.jsonl.gz')
}

class MTCFeatureLoader:
    def __init__(self, jsonpath):
        try:
            self.jsonpath = datapaths[jsonpath]
        except KeyError:
            self.jsonpath = PurePath(jsonpath)
        self.filterBank = {}  # defaultdict(lambda : False)
        self.featureExtractors = {}  # defaultdict(lambda: 0)
        self.addMTCFilters()
        self.addMTCFeatureExtractors()

    def addMTCFilters(self):
        self.registerFilter("vocal", lambda x: x["type"] == "vocal")
        self.registerFilter("instrumental", lambda x: x["type"] == "instrumental")
        self.registerFilter("ann_bgcorpus", lambda x: x["ann_bgcorpus"] == True)
        self.registerFilter("freemeter", lambda x: x["freemeter"] == True)
        self.registerFilter("firstvoice", lambda x: x["id"][10:12] == "01")
        self.registerFilter("afteryear", lambda y: lambda x: x["year"] > y)
        self.registerFilter("beforeyear", lambda y: lambda x: x["year"] < y)
        self.registerFilter(
            "betweenyears", lambda l, h: lambda x: x["year"] > l and x["year"] < h
        )
        self.registerFilter("labeled", lambda x: x["tunefamily"] != "")
        self.registerFilter("unlabeled", lambda x: x["tunefamily"] == "")

        def inOGL(nlbid):
            rn = int(nlbid[3:9])
            return (rn >= 70000 and rn < 80250) or rn == 176897

        self.registerFilter("inOGL", lambda x: inOGL(x["id"]))
        self.registerFilter("inNLBIDs", lambda id_list: lambda x: x["id"] in id_list)
        self.registerFilter(
            "inTuneFamilies", lambda tf_list: lambda x: x["tunefamily"] in tf_list
        )
        inst_test_list = [
            "10373_0",
            "230_0",
            "4560_0",
            "5559_0",
            "3680_0",
            "1079_0",
            "288_1",
            "10075_0",
            "10121_0",
            "4652_0",
            "7016_0",
            "5542_0",
            "1324_0",
            "2566_0",
            "5448_1",
            "5389_0",
            "4756_0",
            "5293_0",
            "9353_0",
            "240_0",
            "5315_0",
            "7918_0",
            "5855_0",
            "5521_0",
            "7116_0",
            "371_0",
        ]
        self.registerFilter("inInstTest", lambda x: x["tunefamily"] in inst_test_list)
    
    def addMTCFeatureExtractors(self):
        self.registerFeatureExtractor(
            "full_beat_str",
            lambda x, y: str(x) + " " + str(y),
            ["beat_str", "beat_fraction_str"],
        )

    def sequences(self):
        if self.jsonpath.suffix == ".gz":
            opener = gzip.open
        else:
            opener = open
        with opener(self.jsonpath, "r") as f:
            for line in f:
                yield json.loads(line)

    @staticmethod
    def writeJSON(json_out_path, seq_iter):
        json_out_path = PurePath(json_out_path)
        if json_out_path.suffix == ".gz":
            opener = gzip.open
            mode = "wt"
        else:
            opener = open
            mode = "w"
        with opener(json_out_path, mode) as f:
            for seq in seq_iter:
                seq_json = json.dumps(seq)
                f.write(seq_json + "\n")

    def getFeatureNames(self):
        seqs = self.sequences()
        seq = next(seqs)  # get the names from first sequence
        return seq["features"].keys()

    def applyFilter(self, mfilter, invert=False, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        filterer = filter
        if invert:
            filterer = filterfalse
        if type(mfilter) == tuple:
            return filterer(self.filterBank[mfilter[0]](*mfilter[1:]), seq_iter)
        else:
            return filterer(self.filterBank[mfilter], seq_iter)

    def applyFilters(self, filter_list, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        for filt in filter_list:
            seq_iter = self.applyFilter(**filt, seq_iter=seq_iter)
        return seq_iter

    def registerFilter(self, name, mfilter):
        self.filterBank[name] = mfilter

    def selectFeatures(self, featlist, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        for seq in seq_iter:
            features = {k: v for k, v in seq["features"].items() if k in featlist}
            seq["features"] = features
            yield seq

    def extractFeature(self, name, func, feats, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        for seq in seq_iter:
            featvects = [seq["features"][x] for x in feats]
            args = zip(*featvects)
            newfeat = [func(*local_args) for local_args in args]
            seq["features"][name] = newfeat
            yield seq

    def registerFeatureExtractor(self, name, func, feats):
        self.featureExtractors[name] = (func, feats)

    def applyFeatureExtractor(self, name, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        func, feats = self.featureExtractors[name]
        return self.extractFeature(name, func, feats, seq_iter)

    def concatAllFeatures(self, name="concat", seq_iter=None):
        feats = self.getFeatureNames()
        return self.extractFeature(
            name,
            func=lambda *args: " ".join([str(a) for a in args]),
            feats=feats,
            seq_iter=seq_iter,
        )

    # heavy on memory
    def minClassSizeFilter(self, classfeature, mininum=0, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        mem = defaultdict(list)
        for seq in seq_iter:
            mem[seq[classfeature]].append(seq)
            if len(mem[seq[classfeature]]) == mininum:
                for s in mem[seq[classfeature]]:
                    yield s
            elif len(mem[seq[classfeature]]) > mininum:
                yield seq

    # heavy on memory
    def maxClassSizeFilter(self, classfeature, maximum=100, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        seqs = sorted(list(seq_iter), key=lambda x: x[classfeature])  # Allas
        for _, gr in groupby(seqs, key=lambda x: x[classfeature]):
            group = list(gr)
            if len(group) <= maximum:
                for g in group:
                    yield g

if __name__ == "__main__":
    pass
