import gzip
import json
import sys
import random
from pathlib import PurePath, Path

from collections import defaultdict
from itertools import filterfalse, groupby

__modpath = Path(__file__).resolve().parent

datapaths = {
    'MTC-ANN-2.0.1'    : PurePath(__modpath, 'data', 'MTC-ANN-2.0.1_sequences-0.9.1.jsonl.gz'),
    'MTC-FS-INST-2.0'  : PurePath(__modpath, 'data', 'MTC-FS-INST-2.0_sequences-0.9.1.jsonl.gz'),
    'ESSEN'            : PurePath(__modpath, 'data', 'essen_sequences-0.9.1.jsonl.gz')
}

class MTCFeatureLoader:
    def __init__(self, jsonpath):
        try:
            self.jsonpath = datapaths[jsonpath]
        except KeyError:
            self.jsonpath = PurePath(jsonpath)
        self.filterBank = {}  # defaultdict(lambda : False)
        self.featureExtractors = {}  # defaultdict(lambda: 0)
        self.NoneReplacers = defaultdict(lambda: lambda x:x) #default: function that returns the argument
        self.addMTCFilters()
        self.addMTCFeatureExtractors()
        self.addNoneReplacers()

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

    def head(self, n=10, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        for ix, seq in enumerate(seq_iter):
            if ix < n:
                yield seq
            else:
                continue

    #heavy on memory
    def tail(self, n=10, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        seqs = list(seq_iter)
        for ix, seq in seqs:
            if len(seqs) - ix <= n:
                yield seq
            else:
                continue
    
    #heavy on memory
    def randomSel(self, n=10, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        seqs = list(seq_iter)
        for seq in random.sample(seqs, n):
            yield seq

    def addMTCFeatureExtractors(self):
        self.registerFeatureExtractor(
            "full_beat_str",
            lambda x, y: str(x) + " " + str(y),
            ["beat_str", "beat_fraction_str"],
        )
    
    def addNoneReplacers(self):
        self.NoneReplacers.update (
            {
                'metriccontour':      lambda featseq: [("+" if ix==0 else val) for ix, val in enumerate(featseq)],
                'imacontour':         lambda featseq: [("+" if ix==0 else val) for ix, val in enumerate(featseq)],
                'contour3':           lambda featseq: [("=" if ix==0 else val) for ix, val in enumerate(featseq)],
                'contour5':           lambda featseq: [("=" if ix==0 else val) for ix, val in enumerate(featseq)],
                'IOR':                lambda featseq: [(1.0 if ix==0 else val) for ix, val in enumerate(featseq)],
                'diatonicinterval':   lambda featseq: [(0 if ix==0 else val) for ix, val in enumerate(featseq)],
                'chromaticinterval':  lambda featseq: [(0 if ix==0 else val) for ix, val in enumerate(featseq)],
                'nextisrest':         lambda featseq: [(True if ix==len(featseq)-1 else val) for ix, val in enumerate(featseq)],
                'beatfraction':       lambda featseq: [("0" if val==None else val) for val in featseq],
                'beatinsong':         lambda featseq: [("0" if val==None else val) for val in featseq],
                'beatinphrase':       lambda featseq: [("0" if val==None else val) for val in featseq],
                'beatinphrase_end':   lambda featseq: [("0" if val==None else val) for val in featseq],
                'beatstrength':       lambda featseq: [(1.0 if val==None else val) for val in featseq],
                'beat_str':           lambda featseq: [('1' if val==None else val) for val in featseq],
                'beat_fraction_str':  lambda featseq: [('0' if val==None else val) for val in featseq],
                'beat':               lambda featseq: [(0.0 if val==None else val) for val in featseq],
                'timesignature':      lambda featseq: [('0/0' if val==None else val) for val in featseq],
                'lyrics':             lambda featseq: [('' if val==None else val) for val in featseq],
                'noncontentword':     lambda featseq: [(False if val==None else val) for val in featseq],
                'wordend':            lambda featseq: [(False if val==None else val) for val in featseq],
                'phoneme':            lambda featseq: [('' if val==None else val) for val in featseq],
                'rhymes':             lambda featseq: [(False if val==None else val) for val in featseq],
                'rhymescontentwords': lambda featseq: [(False if val==None else val) for val in featseq],
                'wordstress':         lambda featseq: [(False if val==None else val) for val in featseq]
            }
        )

    def replaceNone(self, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        for seq in seq_iter:
            for featname in seq["features"].keys():
                seq["features"][featname] = self.NoneReplacers[featname](seq["features"][featname])
            yield seq

    def sequences(self):
        if self.jsonpath.suffix == ".gz":
            opener = gzip.open
        else:
            opener = open
        with opener(self.jsonpath, "r") as f:
            for line in f:
                yield json.loads(line)

    #merges features from from_file into sequeces
    #existing features will be overwritten
    def merge_sequences(self, from_file, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        #read from_sequences in memory (memory expensive, but faster)
        fl = MTCFeatureLoader(from_file)
        from_seqs = list(fl.sequences())
        #convert to dict
        from_seqs = {seq['id']: seq for seq in from_seqs}
        for seq in seq_iter:
            try:
                from_seq = from_seqs[seq['id']]
                for feat in from_seq['features'].keys():
                    seq['features'][feat] = from_seq['features'][feat]
            except KeyError as e:
                pass
            yield seq

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
    def minClassSizeFilter(self, classfeature, minsize=0, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        mem = defaultdict(list)
        for seq in seq_iter:
            mem[seq[classfeature]].append(seq)
            if len(mem[seq[classfeature]]) == minsize:
                for s in mem[seq[classfeature]]:
                    yield s
            elif len(mem[seq[classfeature]]) > minsize:
                yield seq

    # heavy on memory
    def maxClassSizeFilter(self, classfeature, maxsize=sys.maxsize, seq_iter=None):
        if seq_iter is None:
            seq_iter = self.sequences()
        seqs = sorted(list(seq_iter), key=lambda x: x[classfeature])  # Allas
        for _, gr in groupby(seqs, key=lambda x: x[classfeature]):
            group = list(gr)
            if len(group) <= maxsize:
                for g in group:
                    yield g

if __name__ == "__main__":
    pass
