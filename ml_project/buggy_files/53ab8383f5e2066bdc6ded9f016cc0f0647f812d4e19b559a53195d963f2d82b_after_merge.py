  def WriteHeader(self):
    """Setup the Elasticsearch index."""
    if not self._mapping:
      self._mapping = {}

    if self._raw_fields:
      if self._doc_type not in self._mapping:
        self._mapping[self._doc_type] = {}

      _raw_field_mapping = [{
          u'strings': {
              u'match_mapping_type': u'string',
              u'mapping': {
                  u'fields': {
                      u'raw': {
                          u'type': u'string',
                          u'index': u'not_analyzed',
                          u'ignore_above': self._ELASTIC_ANALYZER_STRING_LIMIT
                      }
                  }
              }
          }
      }]
      self._mapping[self._doc_type][u'dynamic_templates'] = _raw_field_mapping

    self._elastic = ElasticSearchHelper(
        self._output_mediator, self._host, self._port, self._flush_interval,
        self._index_name, self._mapping, self._doc_type,
        elastic_password=self._elastic_password,
        elastic_user=self._elastic_user)
    logging.info(u'Adding events to Elasticsearch..')