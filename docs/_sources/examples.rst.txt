Examples
--------

Apply a filter
^^^^^^^^^^^^^^
Keep only the vocal songs (i.e., drop instrumental pieces):

.. code-block:: python

	from MTCFeatures.MTCFeatureLoader import MTCFeatureLoader
	fl = MTCFeatureLoader('MTC-FS-INST-2.0')
	seq_iter = fl.applyFilter('vocal')

	for seq in seq_iter:
		dosomething(seq)

If a filter has arguments, these sould be provided with the filtername as tuple:

.. code-block:: python

	seq_iter = fl.applyFilter( ('afteryear', 1950) )

.. code-block:: python

	seq_iter = fl.applyFilter( ('betweenyears', 1850, 1900) )

Keep only songs in tune families with more than 10 members:

.. code-block:: python

	seq_iter = fl.minClassSizeFilter('tunefamily', 10)

A filter can be inverted by setting argument invert to True:

.. code-block:: python
	
	seq_iter = fl.applyFilter( ('afteryear', 1950), invert=True )

A chain of filters can be applied with the `applyFilters` method. The filters will be applied in the order provided.

.. code-block:: python

	seq_iter = fl.applyFilters(
	    [
	        {'mfilter':'vocal'},
	        {'mfilter':'freemeter', 'invert':True},
	        {'mfilter':('afteryear',1850)}
	    ]
	)


Register a filter
^^^^^^^^^^^^^^^^^

To register a new filter, use method `registerMelodyFilter` in the `MTCFeatureLoader` class. The filter should
be a function returning True if the melody should be kept.

.. code-block:: python

	fl.registerFilter('vocal', lambda x: x['type'] == 'vocal')

Register a filter with arguments:

.. code-block:: python

	fl.registerFilter('afteryear', lambda y: lambda x: x['year'] > y )


Various Examples
^^^^^^^^^^^^^^^^

Only use the midipitch from all songs in MTC-ANN-2.0.1:

.. code-block:: python

	from MTCFeatures.MTCFeatureLoader import MTCFeatureLoader
	fl = MTCFeatureLoader('MTC-ANN-2.0.1')
	seq_iter = fl.selectFeatures(['midipitch'])

Use midipitch and duration from all songs in MTC-ANN-2.0.1:

.. code-block:: python

	fl = MTCFeatureLoader('MTC-ANN-2.0.1')
	seq_iter = fl.selectFeatures(['midipitch', 'duration'])

Use intervals and inter onset interval ratios from all songs in MTC-ANN-2.0.1 and get rid of the None values for the first note:

.. code-block:: python

	fl = MTCFeatureLoader('MTC-ANN-2.0.1')
	seq_iter = fl.selectFeatures(['chromaticinterval', 'IOR'])
	seq_iter = fl.replaceNone(seq_iter=seq_iter)

Use scale degree, metric contour and beat position from all songs in MTC-ANN-2.0.1:

.. code-block:: python

	fl = MTCFeatureLoader('MTC-ANN-2.0.1')
	seq_iter = fl.selectFeatures(['scaledegree','metriccontour','full_beat_str'])
	seq_iter = fl.applyFeatureExtractor('full_beat_str', seq_iter=seq_iter)

Get backgroundcorpus for MTC-ANN from MTC-FS-INST:

.. code-block:: python

	fl = MTCFeatureLoader('MTC-FS-INST-2.0')
	seq_iter = fl.applyFilter('ann_bgcorpus')

Get labeled songs in Onder de groene linde:

.. code-block:: python

	fl = MTCFeatureLoader('MTC-FS-INST-2.0')
	seq_iter = fl.applyFilters(
	    [
	        {'mfilter':'inOGL'},
	        {'mfilter':'labeled'}
	    ]
	)

Keep only those in tune families with more than 2 melodies:

.. code-block:: python

	seq_iter = fl.minClassSizeFilter('tunefamily', 2, seq_iter=seq_iter)

Use labeled 17th and 18th century fiddle music only:

.. code-block:: python

	fl = MTCFeatureLoader('MTC-FS-INST-2.0')
	sel_instr = fl.applyFilter('instrumental')
	sel_17th18th_c = fl.applyFilter( ('betweenyears', 1600, 1800), seq_iter=sel_instr )
	sel_labeled = fl.applyFilter('labeled', seq_iter=sel_17th18th_c)

or:

.. code-block:: python

	seq_iter = fl.applyFilters(
	    [
	        {'mfilter':'instrumental'},
	        {'mfilter':'labeled'},
	        {'mfilter':('betweenyears', 1600, 1800)}
	    ]
	)

Use big tune families (>=20 melodies):

.. code-block:: python

	fl = MTCFeatureLoader('MTC-FS-INST-2.0')
	sel_big = fl.minClassSizeFilter('tunefamily', 20)

Use small tune families (<=5 melodies) only:

.. code-block:: python

	fl = MTCFeatureLoader('MTC-FS-INST-2.0')
	sel_small = fl.maxClassSizeFilter('tunefamily', 5)

Use only melodies with given identifiers:

.. code-block:: python

	fl = MTCFeatureLoader('MTC-FS-INST-2.0')
	id_list = ['NLB125814_01','NLB125815_01','NLB125817_01','NLB125818_01','NLB125822_01','NLB125823_01']
	sel_list = fl.applyFilter( ('inNLBIDs', id_list) )

Use only instrumental melodies from tune family 2805_0:

.. code-block:: python

	fl = MTCFeatureLoader('MTC-FS-INST-2.0')
	tf_list = ['2805_0']
	sel_list = fl.applyFilter( ('inTuneFamilies', tf_list), seq_iter=fl.applyFilter('instrumental'))

Write the result to a gzipped .jsonl file:

.. code-block:: python

	fl.writeJSON('2805_0.jsonl.gz', seq_iter=sel_list)

Get vocal melodies that have a meter:

.. code-block:: python

	fl = MTCFeatureLoader('MTC-FS-INST-2.0')
	seq_iter = fl.applyFilters(
	    [
	        {'mfilter':'vocal'},
	        {'mfilter':'freemeter', 'invert':True}
	    ]
	)