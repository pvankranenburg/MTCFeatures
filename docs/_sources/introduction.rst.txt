Introduction
------------

The `Meertens Tune Collections <http://www.liederenbank.nl/mtc/>`_ (MTC) include various data sets with melodic data. The melodies are provided in Humdrum \*\*kern encoding and as MIDI sequences. In many cases, a representation of the melodies as sequences of feature values is needed rather than encoded scores.

`MTCFeatures` is a Python module that provides melodic data sets containing such feature sequences, and functionality for feature and object filtering and feature extraction.

The following data sets are included:

- MTC-ANN-2.0.1 - A small set of 360 richly annotated melodies from Dutch sources.
- MTC-FS-INST-2.0 - A large set of c. 18 thousand melodies from Dutch sources.
- ESSEN Folksong Collection - A set of more than 8 thousand folk song melodies mainly from Germany.

For more information on the contents of the `Meertens Tune Collections`, please visit `<http://www.liederenbank.nl/mtc/>`_.

For the Essen Folk Song Collection, the features were extracted from the \*\*kern files in the zip-archive as provided by the Center for Computer Assisted Research in the Humanities 
at Stanford University  (https://kern.humdrum.org/cgi-bin/browse?l=/essen). Some adaptations were needed:

* han0586: removed because it does not contain a melody.
* han0953 and india01: removed because the duration of groupettos does not add up.
* deut1328: removed because of encoding problems in the \*\*kern file.
* In 960 files of the han series, a byte 0xFF has been replaced with 0x20 (space). This 0xFF value disrupted the parsing process.
* All melodies with "Mixed meters" are considered as 'free meter' in MTCFeatures since the meter changes often are not exactly indicated in the \*\*kern source.