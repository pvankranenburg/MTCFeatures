"""MTCFeatures provides melodies form the Meertens Tune Collections and ESSEN Folksong collection as sequences of features.

The [Meertens Tune Collections](http://www.liederenbank.nl/mtc/) incorporate various data sets with melodic data. The melodies are provided in Humdrum **kern encoding and as MIDI sequences. In many cases, a representation of the melodies as sequences of feature values is needed. `MTCFeatures` is a Python module that provides such feature sequences together with functionality for feature and object filtering and feature extraction.

.. moduleauthor:: Peter van Kranenburg <peter.van.kranenburg@meertens.knaw.nl>
"""

__version__ = '1.1'

from .MTCFeatureLoader import MTCFeatureLoader
from .DataLocation import DataLocation
from .DataLocation import downloadData

name = "MTCFeatures"