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
	 'features': {'pitch40': [135, 141, 147, 152, 158,    [...] 158, 135],
	              'scaledegree': [1, 2, 3, 4, 5, 1, 6,    [...] 2, 5, 1],
	              'scaledegreespecifier': ['P', 'M', 'M', [...] 'M', 'P', 'P'],

	              [...]

	              'phrasepos': [0.0, 0.071429, 0.142857,  [...] 0.833333, 1.0],
	              'songpos': [0.0, 0.007142857142857143,  [...] 1.0]}
	}

In this example the metadata fields are ``id``, ``type``, ``year``, ``tunefamily``, ``tunefamily_full``, ``freemeter``, and ``ann_bgcorpus``. The named object ``features`` contains several sequences of feature values.

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

Melodies from the ESSEN collection have the following (fall back) values for the metadata fields:

	- `id` = basename of the \*\*kern file
	- `type` = "vocal" (but no lyrics features are present)
	- `year` = -1
	- `tunefamily` = ""
	- `tunefamily_full` = ""

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
	  - {'--', '-', '=', '+', '++'}
	  - Contour of the pitch with respect to the previous note. '--' and '++' are leaps >= 3 in midipitch. First note has ``None``.
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
	  - Metric weight as computed by Inner Metric Analysis. 
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
	* - `IOR`
	  - float
	  - (0.0, ->)
	  - Duration of the note with respect to the duration of the previous note. Duration is inter-onset interval. First note has ``None``.
	* - `onsettick`
	  - int
	  - [0,->)
	  - Onset of the note in MIDI ticks. 
	* - `nextisrest`
	  - bool
	  - {true, false}
	  - Whether the note is followed by a rest. Last note has ``None``.
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
	* - `phrase_ix`
	  - int
	  - [0, ->)
	  - Serial number of the phrase the note is in. First phrase is 0. 
	* - `phrasepos`
	  - float
	  - [0.0, ..., 1.0]
	  - Onset time of the note in its phrase. Onset time of the first note in the phrase is 0.0. Onset time of the last note in the phrase is 1.0. 
	* - `phraseend`
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
	  - Onset time of the note in the phrase in units of the beat length. The last note that starts on the beat has value "0". No notated time signature: ``None`` for all notes.
	* - `melismastatus`
	  - string
	  - {'end', 'start', 'in'} 
	  - In what way the note is part of a melisma. `end`: last note of a melisma (also for syllabic lyrics). `in`: middle note. `start`: first note of a melisma. Vocal melodies only. 
	* - `lyrics`
	  - string
	  - 
	  - Lyric syllable that goes with the note. Leading `-` indicates continuation of a word. Trailing `-` indicates the word to be continued. Only at first note of melisma. Vocal melodies only. 
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

