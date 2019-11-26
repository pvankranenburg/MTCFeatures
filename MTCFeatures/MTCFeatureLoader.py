import gzip
import json
import sys
import random
from pathlib import PurePath

from collections import defaultdict
from itertools import filterfalse, groupby

from .DataLocation import DataLocation

class MTCFeatureLoader:
    """Class for loading and processing melody sequences.
    
    Parameters
    ----------
    jsonpath : string
        Either the filename of a .jsonl file containing melody sequences, or one
        of the predefined names ``'MTC-ANN-2.0.1'``, ``'MTC-FS-INST-2.0'``, or ``'ESSEN'``.
        If the filename ends with .gz, the data file is assumed to be gzipped.
    
    Attributes
    ----------
    jsonpath : string
        The filename of a .jsonl file containing melody sequences. If the filename
        ends with .gz, the file is gunzipped first.
    filterBank : dictionary
        A dictionary of (lambda) functions to be used to filter the sequences.
        The keys are the names of the filters. A filter can be applied with the
        `applyFilter` or `applyFilters` methods. The `filerBank` is initially
        populated with a number of predefined filters. A filter can be added to
        the filterBank with the `registerFilter` method.
    featureExtractors : dictionary
        A dictionary of (lambda) functions that compute new features from existing
        features.
    NoneReplacers : dictionary
        A dictionary of (lambda) functions, each taking a list of feature values
        and returning the list with all occurrences of None replaced with a
        value. The keys are names of features. The `NoneReplacers` dict is used
        by the method `replaceNone`. For each feature for which a NoneReplacer
        is present in the `NoneReplacers` dictionary, this NoneReplacer is applied.
    
    """
    
    def __init__(self, jsonpath):
        self.jsonpath = DataLocation(jsonpath).getFilePath()
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
        self.registerFilter("origin", lambda y: lambda x: y in x["origin"])
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
        """Yields the first `n` melodies.
        
        Parameters
        ----------
        n : int, default=10
            the number of sequences to yield.
        seq_iter : iterable or None, default=None
            iterable over melody sequences. If None, take the sequences from `jsonpath`.
        
        Yields
        ------
        sequence
            Melody Sequence
        
        """
        if seq_iter is None:
            seq_iter = self.sequences()
        for ix, seq in enumerate(seq_iter):
            if ix < n:
                yield seq
            else:
                continue

    #heavy on memory
    def tail(self, n=10, seq_iter=None):
        """Returns the last `n` melodies.
        
        Parameters
        ----------
        n : int, default=10
            the number of sequences to yield.
        seq_iter : iterable or None, default=None
            iterable over melody sequences. If None, take the sequences from `jsonpath`.
        
        Yields
        ------
        sequence
            Melody Sequence
        
        """
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
        """Returns a random sample of `n` melodies.
        
        Parameters
        ----------
        n : int, default=10
            the number of sequences to yield.
        seq_iter : iterable or None, default=None
            iterable over melody sequences. If None, take the sequences from `jsonpath`.
        
        Yields
        ------
        sequence
            Melody Sequence
        
        """
        if seq_iter is None:
            seq_iter = self.sequences()
        seqs = list(seq_iter)
        for seq in random.sample(seqs, n):
            yield seq

    def addMTCFeatureExtractors(self):
        self.registerFeatureExtractor(
            "full_beat_str",
            lambda x, y: str(x) + " " + str(y) if y != "0" else str(x),
            ["beat_str", "beat_fraction_str"],
        )
    
    #Not for LBDM, Frankland and Schellenberg features
    def addNoneReplacers(self):
        self.NoneReplacers.update (
            {
                'metriccontour':      lambda featseq: [("+" if ix==0 else "=" if val==None else val) for ix, val in enumerate(featseq)],
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
                'wordstress':         lambda featseq: [(False if val==None else val) for val in featseq],
                #Version 1.1
                'IOR_frac' :          lambda featseq: [("1" if ix==0 or ix==len(featseq)-1 else val) for ix, val in enumerate(featseq)],
                'durationcontour':    lambda featseq: [("=" if ix==0 else val) for ix, val in enumerate(featseq)],                
                'restduration_frac':  lambda featseq: [("0" if val==None else val) for val in featseq],
            }
        )

    def replaceNone(self, seq_iter=None):
        """Replace None values with sensible fall back values.
        
        For all features for which a NoneReplacer has been registered, replace the None values with sensible fall back values according to the NoneReplacer.
        
        Parameters
        ----------
        seq_iter : iterable or None, default=None
            iterable over melody sequences. If None, take the sequences from `jsonpath`.
            
        Yields
        ------
        sequence
            Melody Sequence with None values replaced
        """
        
        if seq_iter is None:
            seq_iter = self.sequences()
        for seq in seq_iter:
            for featname in seq["features"].keys():
                seq["features"][featname] = self.NoneReplacers[featname](seq["features"][featname])
            yield seq

    def sequences(self):
        """Yields the list of melodies from the file `jsonpath`.
        
        Yields
        ------
        sequence
            Melody Sequence
        """
        if self.jsonpath.endswith(".gz"):
            opener = gzip.open
        else:
            opener = open
        with opener(self.jsonpath, "r") as f:
            for line in f:
                yield json.loads(line)

    #merges features from from_file into sequeces
    #existing features will be overwritten
    def merge_sequences(self, from_file, seq_iter=None):
        """Merges features from provided file.
        
        Parameters
        ----------
        from_file : string
            File name of a .jsonl file from which the feature sequences will be imported.
        seq_iter : iterable or None, default=None
            iterable over melody sequences. If None, take the sequences from `jsonpath`.
            
        Yields
        ------
        sequence
            Melody Sequence with features from `from_file` included.
        """
        
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
            except KeyError:
                pass
            yield seq

    @staticmethod
    def writeJSON(json_out_path, seq_iter):
        """Writes a list of melodies to a .jsonl file
        
        Parameters
        ----------
        json_out_path : string
            Name of the file to write the json representations of the melodies. If the
            filename ends with .gz, the file is gzipped.
        seq_iter : iterable over melody sequences
            Melody sequences to write to the file.
        """
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
        """Get the names of the features present in the Melody Sequences.
        
        Returns
        -------
        featnames : list of strings
            Names of the features as present in the FIRST melody in source file `jsonpath`.
        """
        seqs = self.sequences()
        seq = next(seqs)  # get the names from first sequence
        return seq["features"].keys()

    def applyFilter(self, mfilter, invert=False, seq_iter=None):
        """Apply a melody filter. Only keep those melodies that are passed by the filter.
        
        Parameters
        ----------
        mfilter : string or tuple
            Name of the filter as registered in `filterBank`. If the filter has arguments,
            this should be a tuple of the filter name and the arguments. 
        invert : bool, default=False
            If True, invert the filter. Only keep those melodies for which the condition is False.

        seq_iter : iterable or None, default=None
            iterable over melody sequences. If None, take the sequences from `jsonpath`.
            
        Yields
        ------
        sequence
            Melody Sequence that is passed by the filter.
        """          
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
        """Apply a chain of filters. Only keep those melodies that are passed by all filters.
        
        Example
        -------
        
        .. code-block:: python

            from MTCFeatures import MTCFeatureLoader
            fsinst_dl = MTCFeatureLoader('MTC-FS-INST-2.0')
            vocal_seqs = fsinst_dl.applyFilters([
                {'mfilter':'freemeter', 'invert':True},
                {'mfilter':"vocal"},
                {'mfilter':("afteryear",1850)} ]
            )
        
        Now `vocal_seqs` is an iterator over all vocal melodies published after 1850 that do not have free meter,
        
        Parameters
        ----------
        filter_list : \*\*kwargs for `applyFilter` 
            Chains a number of `applyFilter` calls with \*\*kwargs as provided.
        seq_iter : iterable or None, default=None
            iterable over melody sequences. If None, take the sequences from `jsonpath`.
            
        Yields
        ------
        sequence
            Melody Sequence that is passed by the filter.
        """          
        if seq_iter is None:
            seq_iter = self.sequences()
        for filt in filter_list:
            seq_iter = self.applyFilter(**filt, seq_iter=seq_iter)
        return seq_iter

    def registerFilter(self, name, mfilter):
        """Store a filter in `filterBank`.
        
        Example
        -------
        .. code-block:: python

            from MTCFeatures import MTCFeatureLoader
            fsinst_dl = MTCFeatureLoader('MTC-FS-INST-2.0')
            dl.registerFilter("vocal", lambda x: x["type"] == "vocal")
            dl.registerFilter("afteryear", lambda y: lambda x: x["year"] > y)
        
        Now the filter ``vocal`` is registered that passes all melodies with type vocal.
        And filter ``afteryear`` with parameter `y` is registered that passes all melodies published after year `y`.
        The filters can be applied with the method `applyFilter`
        
        Parameters
        ----------
        name : string
            name of the filter. This will be used as key in the `filterBank` dictionary.
        mfilter : function
            Function that evaluates to True for melodies to be kept.
        """
        self.filterBank[name] = mfilter

    def selectFeatures(self, featlist, seq_iter=None):
        """Feature filter. For all melodies, keep only the indicated features.
        
        Parameters
        ----------
        featlist : list of strings
            Names of the features to keep.
        seq_iter : iterable or None, default=None
            iterable over melody sequences. If None, take the sequences from `jsonpath`.
    
        Yields
        ------
        sequence
            Melody Sequence with reduced feature set.
        """
        
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
        """Store a Feature Extractor.
        
        The feature extractor will be applied for each note separately.
        The provided ``func`` will be called with the values of the indicated
        features in ``feats`` as arguments. and the sequence of computed values
        will be stored in the ``features`` dictionary of the Melody Sequence with
        ``name`` as key. 

        Example
        -------
        .. code-block:: python

            from MTCFeatures import MTCFeatureLoader
            dl = MTCFeatureLoader('MTC-ANN-2.0.1')
            dl.registerFeatureExtractor(
                'midi8va',
                lambda x: x+12,
                ['midipitch']
            )
            seq_iter = dl.applyFeatureExtractor('midi8va')
        
        Parameters
        ----------
        name : string
            name of the feature extractor.
        func : function
            (lambda) function taking feature values for one note and computing the
            value for the new feature.
        feats : list of strings
            names of the features that are the input for ``func``.
        """
        
        self.featureExtractors[name] = (func, feats)

    def applyFeatureExtractor(self, name, seq_iter=None):
        """Apply a Feature Extractor.
        
        Parameters
        ----------
        name : string
            name with which the feature extractor was registered.
        seq_iter : iterable or None, default=None
            iterable over melody sequences. If None, take the sequences from `jsonpath`.
        
        Yields
        ------
        sequence
            Melody Sequence with extracted feature included.
        """
                
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
        """Keep only melodies in tune families with >= ``minsize`` members.
        
        Parameters
        ----------
        classfeature : string
            name of the feature that is used to group the melodies.
        minsize : int, default=0
            Minimum size of classes to keep.
        seq_iter : iterable or None, default=None
            iterable over melody sequences. If None, take the sequences from `jsonpath`.
    
        Yields
        ------
        sequence
            Melody Sequence for melody in a class with minimum size `minsize`.
        """
        
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
        """Keep only melodies in tune families with <= ``maxsize`` members.
        
        Parameters
        ----------
        classfeature : string
            name of the feature that is used to group the melodies.
        maxsize : int, default=sys.maxsize
            Maximum size of classes to keep.
        seq_iter : iterable or None, default=None
            iterable over melody sequences. If None, take the sequences from `jsonpath`.
    
        Yields
        ------
        sequence
            Melody Sequence for melody in a class with maximum size `maxsize`.
        """
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
