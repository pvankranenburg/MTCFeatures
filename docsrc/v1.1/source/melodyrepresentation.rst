Melody Representation
---------------------

`MTCFeatures` provides a class `MTCFeatureLoader`, which offers functionality for loading and processing melodies represented as sequences of features. A `MTCFeatureLoader` object takes as source a .jsonl file (optionally gzipped), which is a text file with on each line a json object representing a melody. A melody object contains metadata fields and several sequences of feature values. As follows (here pretty printed for readibility - the entire json object for one melody should be on one line in the data file)::

	{'id': 'NLB178968_01',
	 'type': 'vocal',
	 'year': 1866,
	 'freemeter': false,
	 'tunefamily': '1302_0',
	 'tunefamily_full': 'Contre les chagrins de la vie',
	 'ann_bgcorpus': True,
	 'origin': '',
	 'features': {'pitch40': [135, 141, 147, 152, 158,	[...] 158, 135],
				  'scaledegree': [1, 2, 3, 4, 5, 1, 6,	[...] 2, 5, 1],
				  'scaledegreespecifier': ['P', 'M', 'M', [...] 'M', 'P', 'P'],

				  [...]

				  'phrasepos': [0.0, 0.071429, 0.142857,  [...] 0.833333, 1.0],
				  'songpos': [0.0, 0.007142857142857143,  [...] 1.0]}
	}

In this example the metadata fields are ``id``, ``type``, ``year``, ``tunefamily``, ``tunefamily_full``, ``freemeter``, ``ann_bgcorpus``, and ``origin``. The named object ``features`` contains several sequences of feature values.

One feature sequence corresponds with the sequence of notes in the given melody. Rests and grace notes are not represented. Consecutive tied notes are represented with one value.

The following meta data fields are included:

.. list-table:: Metadata Fields
	:widths: 30 70
	:header-rows: 1

	* - Field
	  - Description
	* - `id` (string)
	  - Identifier of the melody.
	* - `type` ({vocal, instrumental})
	  - Type of the song. ``vocal``: has lyrics, ``instrumental``: has no lyrics.
	* - `year` (int)
	  - Year of publication of the song
	* - `tunefamily` (string)
	  - Tune family identifier
	* - `tunefamily_full` (string)
	  - Full name of the tune family
	* - `freemeter` (bool)
	  - Whether the melody has a free (i.e. no notated) meter.
	* - `ann_bgcorpus` (bool)
	  - The songs in MTC-FS-INST-2.0 for which this value is True are unrelated to the songs in MTC-ANN-2.0.1.
	* - `origin` (string)
	  - The path of the \*\*kern file in the ESSEN collection, mostly indicating the geographic origin of the melody.

Melodies from the ESSEN collection have the following (fall back) values for the metadata fields:

	- `id` = basename of the \*\*kern file
	- `type` = "vocal" (but no lyrics features are present)
	- `year` = -1
	- `tunefamily` = ""
	- `tunefamily_full` = ""

For melodies from the MTC, the `origin` metadata field is empty.

Various features are represented as rational numbers. This is to avoid precision problems
that would arise with representation of certain durations as float. For example, the duration of a 
eight triplet note is precisely represented by 1/12, but it has no exact decimal representation:
0.833333333... The fractions module that is part of the standard library of Python can be used
to handle these values:

.. code-block:: python

	>>> from fractions import Fraction
	>>> triplet_eight = Fraction('1/12')
	>>> print(float(triplet_eight))
	0.0833333333333

The following table presents a semi-formal description of the features that are included for each note:

.. list-table:: Features
	:widths: 10 10 10 70
	:header-rows: 1

	* - Feature
	  - Type
	  - Values
	  - Description 
	* - `pitch`
	  - string
	  - {'A', ..., 'G'} x {'--', '-', '', '#', '##'} x {'0', ... '8'}
	  - Pitch of the note in string representation as defined in `music21 <https://web.mit.edu/music21/>`_. 
	* - `midipitch`
	  - int
	  - [0, ..., 108]
	  - MIDI note number representing the pitch. 
	* - `pitch40`
	  - int
	  - [0, ->)
	  - Pitch in `base40 <http://www.ccarh.org/publications/reprints/base40>`_ representation. 
	* - `contour3`
	  - string
	  - {'-', '=', '+'}
	  - Contour of the pitch with respect to the previous note. First note is ``None``.
	* - `contour5`
	  - string
	  - {'-\\-', '-', '=', '+', '++'}
	  - Contour of the pitch with respect to the previous note. '-\\-' and '++' are leaps >= 3 in midipitch. First note has ``None``.
	* - `diatonicinterval`
	  - int
	  - (<-, ->)
	  - Diatonic interval with previous note. First note has ``None``.
	* - `chromaticinterval`
	  - int
	  - (<-, ->)
	  - Chromatic interval (diff of midipitch) with respect to previous note. First note has ``None``.
	* - `tonic`
	  - string
	  - {'A', ..., 'G'} x {'-', '', '#'}
	  - Pitch class of the tonic for the current note. 
	* - `mode`
	  - string
	  - {'major', 'minor', 'dorian', ..., 'locrian'}
	  - Mode for the current note. 
	* - `scaledegree`
	  - int
	  - [1, ..., 7]
	  - Scale degree of the pitch.
	* - `scaledegreespecifier`
	  - string
	  - {'P', 'M', 'm', 'A', 'd', ...}
	  - Specifier of the scaledegree: Perfect, Major, Minor, Augmented, Diminished, ... above the tonic. 
	* - `diatonicpitch`
	  - int
	  - [0, ->)
	  - Diatonic pitch of the note. Tonic in octave 0 gets value 0. 
	* - `timesignature`
	  - Fraction (string)
	  - 'n/d'
	  - Time signature for the current note. No notated time signature: ``None`` for all notes.
	* - `beatstrength`
	  - float
	  - (0.0, ..., 1.0]
	  - Metric weight (beatStrength) of the onset time of the note as computed by music21. No notated time signature: ``None`` for all notes.
	* - `metriccontour`
	  - string
	  - {'-', '=', '+'}
	  - Contour of metric weight (beatstrength) with respect to the previous note. First note has ``None``. No notated time signature: ``None`` for all notes.
	* - `imaweight`
	  - float
	  - [0.0, ..., 1.0]
	  - Metric weight as computed by Inner Metric Analysis (Nestke and Noll, 2001). 
	* - `imacontour`
	  - string
	  - {'-', '=', '+'}
	  - Contour of metric weight (ima weight) with respect to the previous note. First note has ``None``.
	* - `duration`
	  - float
	  - [0.0, ->)
	  - Duration of the (possibly tied) note. Quarter note has duration 1.0.
	* - `duration_frac`
	  - Fraction (string)
	  - {'n/d', 'n'}
	  - Quarterlength of the (possibly tied) note as fraction. 
	* - `duration_fullname`
	  - string
	  - 
	  -  Full name of the duration as generated by music21. 
	* - `durationcontour`
	  - string
	  - {'-', '=', '+'}
	  - Whether the duration of the note is shorter ``-``, equal ``=`` or longer ``+`` than the previous note. First note has ``None``.
	* - `IOI`
	  - float
	  - (0.0, ->)
	  - Length of the time interval between the onset of the note and the onset of the next note. Quarternote is 1.0. Last note has ``None`` unles a rest follows.
	* - `IOI_frac`
	  - Fraction (string)
	  - {'n/d', 'n'}
	  - IOI represented as fraction.
	* - `IOR`
	  - float
	  - (0.0, ->)
	  - IOI of the note with respect to IOI of the previous note. First note has ``None``. Last note has ``None`` unles a rest follows.
	* - `IOR_frac`
	  - Fraction (string)
	  - {'n/d', 'n'}
	  - IOR represented as fraction.
	* - `onsettick`
	  - int
	  - [0,->)
	  - Onset of the note in MIDI ticks. Onset of the first note is 0. Number of ticks per quarter note is based on greatest common divisor of all durations.
	* - `beatfraction`
	  - Fraction (string)
	  - {'n/d', 'n'}
	  - Duration of the note with respect to length of the beat. No notated time signature: ``None`` for all notes.
	* - `beat_str`
	  - Integer (string)
	  - {'1', ... }
	  - Beat in the measure, the note is in. First beat is '1'. No notated time signature: ``None`` for all notes.
	* - `beat_fraction_str`
	  - Fraction (string)
	  - {'n/d', 'n'}
	  - Position of the onset time of the note relative to the beat in the measure. Note on the beat has value '0'. No notated time signature: ``None`` for all notes.
	* - `beat`
	  - float
	  - [1.0, ->)
	  - Position of the onset time of the note relative to the measure in units of the beat. First beat is 1.0. No notated time signature: ``None`` for all notes. 
	* - `songpos`
	  - float
	  - [0.0, ..., 1.0]
	  - Onset time of the note in the song. Onset time of the first note is 0.0. Onset time of the last note is 1.0. 
	* - `beatinsong`
	  - Fraction (string)
	  - {'n/d', 'n'}
	  - Onset time of the note in units of the beat length. First note in the first full bar has value "0". No notated time signature: ``None`` for all notes. 
	* - `nextisrest`
	  - bool
	  - {true, false}
	  - Whether the note is followed by a rest. Last note has ``None``.
	* - `restduration_frac`
	  - Fraction (string)
	  - {'n/d', 'n'}
	  - Duration of the rest(s) that follow the note. As fraction. Quarterlength is 1. ``None`` if no rest follows.
	* - `phrase_ix`
	  - int
	  - [0, ->)
	  - Serial number of the phrase the note is in. First phrase is 0. 
	* - `phrasepos`
	  - float
	  - [0.0, ..., 1.0]
	  - Onset time of the note in its phrase. Onset time of the first note in the phrase is 0.0. Onset time of the last note in the phrase is 1.0. 
	* - `phrase_end`
	  - bool
	  - {true, false}
	  - Whether the note is the last in a phrase. 
	* - `beatinphrase`
	  - Fraction (string)
	  - {'n/d', 'n'}
	  - Onset time of the note in the phrase in units of the beat length. First note in the first full bar has value "0". No notated time signature: ``None`` for all notes.
	* - `beatinphrase_end`
	  - Fraction (string)
	  - {'n/d', 'n'}
	  - Onset time of the note in the phrase in units of the beat length. The note that starts on the first beat of the last measure has value "0". No notated time signature: ``None`` for all notes.
	* - `melismastatus`
	  - string
	  - {'end', 'start', 'in'} 
	  - In what way the note is part of a melisma. `end`: last note of a melisma (also for syllabic lyrics). `in`: middle note. `start`: first note of a melisma. Vocal melodies only. 
	* - `lyrics`
	  - string
	  - 
	  - Lyric syllable that goes with the note. Leading ``-`` indicates continuation of a word. Trailing ``-`` indicates the word to be continued. Only at first note of melisma. Vocal melodies only. 
	* - `noncontentword`
	  - bool
	  - {true, false} 
	  - Whether the lyric is a non content word in the Dutch language. Only at first note of melisma. Vocal melodies only. 
	* - `wordend`
	  - bool
	  - {true, false}
	  - Whether the syllable at the note is the last (or only) in the word. Only at first note of melisma. Vocal melodies only. 
	* - `wordstress`
	  - bool
	  - {true, false}
	  - Whether the syllable at the note is stressed.  Only at first note of melisma. Vocal melodies only. 
	* - `phoneme`
	  - string
	  -  
	  - Phonemic representation of the syllable at the note. Only at first note of melisma. Vocal melodies only. 
	* - `rhymes`
	  - bool
	  - {true, false}
	  - Whether the word that ends at the note rhymes with another word anywhere in the lyrics of the song. Only at first note of melisma. Vocal melodies only. 
	* - `rhymescontentwords`
	  - bool
	  - {true, false}
	  - Whether the word that ends at the note rhymes with another word (non content words excluded) anywhere in the lyrics of the song. Only at first note of melisma. Vocal melodies only. 
	* - `gpr2a_Frankland`
	  - float
	  - 
	  - Boundary strength of the boundary following the note according to Quantification of GTTM's GPR 2a by Frankland and Cohen (2004). 
	* - `gpr2b_Frankland`
	  - float
	  - 
	  - Boundary strength of the boundary following the note according to Quantification of GTTM's GPR 2b by Frankland and Cohen (2004). 
	* - `gpr3a_Frankland`
	  - float
	  - 
	  - Boundary strength of the boundary following the note according to Quantification of GTTM's GPR 3a by Frankland and Cohen (2004). 
	* - `gpr3d_Frankland`
	  - float
	  - 
	  - Boundary strength of the boundary following the note according to Quantification of GTTM's GPR 3d by Frankland and Cohen (2004).
	* - `gpr_Frankland_sum`
	  - float
	  -
	  - Sum of boundary strengths for Quantified GPRs 2a, 2b, 3a, and 3d.
	* - `lbdm_boundarystrength`
	  - float
	  -
	  - Overall Local Boundary Strength for the boundary following the note according to the Local Boundary Detection Model (Cambouropoulos, 2001).
	* - `lbdm_spitch`
	  - float
	  -
	  - Strength of the pitch boundary following the note according to the Local Boundary Detection Model (Cambouropoulos, 2001).
	* - `lbdm_sioi`
	  - float
	  -
	  - Strength of the IOI boundary following the note according to the Local Boundary Detection Model (Cambouropoulos, 2001).
	* - `lbdm_srest`
	  - float
	  -
	  - Strength of the Rest boundary following the note according to the Local Boundary Detection Model (Cambouropoulos, 2001).
	* - `lbdm_rpitch`
	  - float
	  -
	  - Degree of change for the pitch interval following the note according to the Local Boundary Detection Model (Cambouropoulos, 2001).
	* - `lbdm_rioi`
	  - float
	  -
	  - Degree of change for the inter-onset interval following the note according to the Local Boundary Detection Model (Cambouropoulos, 2001).
	* - `lbdm_rrest`
	  - float
	  -
	  - Degree of change for the rest following the note according to the Local Boundary Detection Model (Cambouropoulos, 2001).
	* - `pitchproximity`
	  - int
	  - 
	  - Expectancy of the note according to Factor 1 (pitchproximity) of the two-factor reduction of Narmour's (1990) IR by Schellenberg (1997).
	* - `pitchreversal`
	  - float
	  - 
	  - Expectancy of the note according to Factor 2 (pitchreversal) of the two-factor reduction of Narmour's (1990) IR by Schellenberg (1997).

References
^^^^^^^^^^

* Cambouropoulos, E. (2001). The Local Boundary Detection Model (LBDM) and its Application in the Study of Expressive Timing. In *Proceedings of the International Computer Music Conference,* Havana.
* Frankland, B.W. & Cohen, A.J. (2004). Parsing of Melody: Quantification and Testing of the Local Grouping Rules of Lerdahl and Jackendoff’s A Generative Theory of Tonal Music. *Music Perception,* 21(4), 499-543.
* Narmour, E. (1990). *The Analysis and Cognition of Basic Melodic Structures - The Implication-Realization Model.* Chicago and London: The University of Chicago Press.
* Nestke, A. & Noll, T. (2001). Inner Metric Analysis. In Haluska, J. (ed.), *Music and Mathematics* (91–111). Bratislava: Tatra Mountains Publications.
* Schellenberg, E.G. (1997). Simplifying the Implication-Realization Model of Melodic Expectancy. *Music Perception: An Interdisciplinary Journal* 14(3), 295-318.