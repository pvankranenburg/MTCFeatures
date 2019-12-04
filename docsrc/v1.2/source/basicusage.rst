Basic Functionality
-------------------

Basically all functionality is incorporated in the class `MTCFeatureLoader`. A `MTCFeatureLoader` object takes as
source a .jsonl file, which is a text file (optionally gzipped) with on each line a json object representing a
melody. A melody object contains metadata fields and several sequences of feature values.

Several .jsonl files are provided with the module:

- ``MTC-ANN-2.0.1`` - Feature sequences for the melodies of MTC-ANN-2.0.1.
- ``MTC-FS-INST-2.0`` - Feature sequences for the melodies of MTC-FS-INST-2.0.
- ``ESSEN`` - Feature sequences for the melodies in the ESSEN Folksong Collection.

The `MTCFeatureLoader` can be initialized either with one of these, or with a user provided .jsonl or .jsonl.gz file:

.. code-block:: python

	from MTCFeatures import MTCFeatureLoader
	fl = MTCFeatureLoader('MTC-ANN-2.0.1')
	fl = MTCFeatureLoader('MTC-FS-INST-2.0')
	fl = MTCFeatureLoader('../path/to/my/file.jsonl.gz')
	fl = MTCFeatureLoader('/path/to/my/file.jsonl')

The MTCFeatureLoader class provides various functionalities:

- Melody Filtering : select melodies according to given criteria
- Feature selection : keep subset of features
- Feature extraction : compute a new feature from existing features and add it to the object
- Replace undefined feature values (``null`` in json, ``None`` in Python) with sensible fall back values

Operations can be chained. All feature extractors, feature selectors, object filters, and NoneReplacer
return an iterator over the resulting sequences. Each has a parameter `seq_iter`. If `seq_iter` is ``None`` (default),
the .jsonl file is taken as data source and a new iterator is created. Otherwise, the provided iterator
is taken as data source. A method, `applyFilters` is available which takes a list of filter names and applies
these in the provided order.

The following filters are registered in class `MTCFeatureLoader`:

- ``vocal`` : Only keep vocal melodies
- ``instrumental`` : Only keep instrumental melodies
- ``hasFeatures(feat_list)`` : Only keep melodies that have all features which names are in feat_list.
- ``firstvoice`` : Only keep first voices/stanzas (i.e. identifier ending with _01)
- ``ann_bgcorpus`` : Only keep melodies unrelated to MTC-ANN (only applicable to MTC-FS-INST)
- ``labeled`` : Only keep melodies with a tune family label
- ``unlabeled`` : Only keep melodies without a tune family label
- ``afteryear(year)`` : Only keep melodies in sources dated later than year (year not included)
- ``beforeyear(year)`` : Only keep melodies in sources dated before year (year not included)
- ``betweenyears(year1, year2)`` : Only keep melodies in sources dated between year1 and year2 (both not included)
- ``inOGL`` : Only keep melodies that are part of Onder de Groene Linde
- ``inNLBIDs(id_list)`` : Only keep melodies with given identifiers in id_list
- ``inTuneFamilies(tf_list)`` : Only keep melodies in given tune families in tf_list
- ``inInstTest`` : Only keep melodies that are in cINST.
- ``origin(location)`` : Only keep melodies if ``location`` occurs somewhere in the origin meta data field (only for Essen).

Available as separate functions:

- `minClassSizeFilter` : Keep only melodies in tune families with >= ``minsize`` members.
- `maxClassSizeFilter` : Keep only melodies in tune families with <= ``maxsize`` members.
- `head` : Keep only first ``n`` melodies.
- `tail` : Keep only last ``n`` melodies.
- `randomSel` : Take a random sample of ``n`` melodies.
- `replaceNone` : Replace undefined feature values (``None``) with sensible fall back values.

For replacement of the None values, a separate rule is included for each of the relevant features.
The following rules are included:

- ``metriccontour``:       None -> '=' if all items in the sequence are None. None -> '+' if only the first item is None.
- ``imacontour``:          First note: None -> "+"
- ``contour3``:            First note: None -> "="
- ``contour5``:            First note: None -> "="
- ``IOR``:                 First, and possibly last notes: None -> 1.0
- ``IOR_frac``:            First, and possibly last notes: None -> "1"
- ``durationcontour``:     First note: None -> "="
- ``restduration_frac``:   None -> "0"
- ``diatonicinterval``:    First note: None -> 0
- ``chromaticinterval``:   First note: None -> 0
- ``nextisrest``:          Last note: None -> True
- ``beatfraction``:        None -> "0"
- ``beatinsong``:          None -> "0"
- ``beatinphrase``:        None -> "0"
- ``beatinphrase_end``:    None -> "0"
- ``beatstrength``:        None -> 1.0
- ``beat_str``:            None -> "1"
- ``beat_fraction_str``:   None -> "0"
- ``beat``:                None -> 0.0
- ``timesignature``:       None -> "0/0"
- ``lyrics``:              None -> ""
- ``noncontentword``:      None -> False
- ``wordend``:             None -> False
- ``phoneme``:             None -> ''
- ``rhymes``:              None -> False
- ``rhymescontentwords``:  None -> False
- ``wordstress``:          None -> False

For the different models from the literature (LBDM, GTTM, IR) no None-replacers are included.
