    def __init__(self,
                 input_cache_dir: Text,
                 output_cache_dir: Text,
                 analyze_data_list: List[_Dataset],
                 typespecs: Mapping[Text, tf.TypeSpec],
                 preprocessing_fn: Any,
                 cache_source: beam.PTransform):
      # pyformat: enable
      self._input_cache_dir = input_cache_dir
      self._output_cache_dir = output_cache_dir
      self._analyze_data_list = analyze_data_list
      self._feature_spec_or_typespec = typespecs
      self._preprocessing_fn = preprocessing_fn
      self._cache_source = cache_source