# MTCFeatures

The [Meertens Tune Collections](http://www.liederenbank.nl/mtc/) incorporate various data sets with melodic data. The melodies are provided in Humdrum **kern encoding and as MIDI sequences. In many cases, a representation of the melodies as sequences of feature values is needed. `MTCFeatures` is a Python module that provides such feature sequences together with functionality for feature and object filtering and feature extraction.

One feature sequence corresponds with the sequence of notes for the given melody. Rests and grace notes are not represented. Consecutive tied notes are represented with one value. The following table presents a semi-formal description of the features that are included:

| Feature | Type | Values | Description |
| --- | --- | --- | --- |
| `pitch` | string | {'A', ..., 'G'} x {'--', '-', '', '#', '##'} x {'0', ... '8'} | Pitch of the note in string representation as used by music21. |
| `midipitch` | int | [0, ..., 108] | MIDI note number of the pitch. |
| `pitch40` | int | [0, ->) | Pitch in [base40](http://www.ccarh.org/publications/reprints/base40/) representation. |
| `contour3` | string | {'-', '=', '+'} | Contour of the pitch with respect to the previous note. |
| `contour5` | string | {'--', '-', '=', '+', '++'} | Contour of the pitch with respect to the previous note. '--' and '++' are leaps >= 3 in midipitch. |
| `diatonicinterval` | int | (<-, ->) | Diatonic interval with previous note. First note gets '0'. |
| `chromaticinterval` | int | (<-, ->) | Chromatic interval (diff of midipitch) with respect to previous note. First note gets '0'. |
| `tonic` | string | {'A', ..., 'G'} x {'-', '', '#'} | Pitch class of the tonic for the current note. |
| `mode` | string | {'major', 'minor', 'dorian', ..., 'locrian'} | Mode for the current note. |
| `scaledegree` | int | [1, ..., 7] | Scale degree of the pitch.|
| `scaledegreespecifier` | string | {'P', 'M', 'm', 'A', 'd', ...} | Specifier of the scaledegree: Perfect, Major, Minor, Augmented, Diminished, ... above the tonic. |
| `diatonicpitch` | int | [0, ->) | Diatonic pitch of the note. Tonic in octave 0 gets value 0. |
| `timesignature` | Fraction (string) | 'n/d' | Time signature for the current note. No notated time signature: '0/0' for all notes. | 
| `beatstrength` | float | (0.0, ..., 1.0] | Metric weight (beatStrength) of the onset time of the note as computed by music21. No notated time signature: 1.0 for all notes. |
| `metriccontour` | string | {'-', '=', '+'} | Contour of metric weight (beatstrength) with respect to the previous note. First note gets '+'. No notated time signature: '=' for all notes. |
| `imaweight` | float | [0.0, ..., 1.0] | Metric weight as computed by Inner Metric Analysis. |
| `imacontour` | string | {'-', '=', '+'} | Contour of metric weight (ima weight) with respect to the previous note. First note gets '+'. |
| `duration` | float | [0.0, ->) | Duration of the note. Quarter note has duration 1.0. |
| `IOR` | float | (0.0, ->) | Duration of the note with respect to the duration of the previous note. Duration is inter-onset interval. |
| `beatfraction` | Fraction (string) | {'n/d', 'n'} | Duration of the note with respect to length of the beat. No notated time signature: '0' for all notes. |
| `beat_str` | Integer (string) | {'1', ... } | Beat in the measure, the note is in. First beat is '1'. No notated time signature: '1' for all notes. |
| `beat_fraction_str` | Fraction (string) | {'n/d', 'n'} | Position of the onset time of the note relative to the beat in the measure. Note on the beat has value '0'. No notated time signature: '0' for all notes. |
| `beat` | float | [1.0, ->) | Position of the onset time of the note relative to the measure in units of the beat. First beat is 1.0. No notated time signature: 0.0 for all notes. |
| `songpos` | float | [0.0, ..., 1.0] | Onset time of the note in the song. Onset time of the first note is 0.0. Onset time of the last note is 1.0. |
| `beatinsong` | Fraction (string) | {'n/d', 'n'} | Onset time of the note in units of the beat length. First note in the first full bar has value "0". No notated time signature: '0' for all notes. |
| `phrase_ix` | int | [0, ->) | Serial number of the phrase the note is in. First phrase is 0. |
| `phrasepos` | float | [0.0, ..., 1.0] | Onset time of the note in its phrase. Onset time of the first note in the phrase is 0.0. Onset time of the last note in the phrase is 1.0. |
| `beatinphrase` | Fraction (string) | {'n/d', 'n'} | Onset time of the note in the phrase in units of the beat length. First note in the first full bar has value "0". No notated time signature: '0' for all notes. |
| `beatinphrase_end` | Fraction (string) | {'n/d', 'n'} | Onset time of the note in the phrase in units of the beat length. The last note that starts on the beat has value "0". No notated time signature: '0' for all notes. |
