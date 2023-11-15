  def WriteHeader(self):
    """Connects to the Elasticsearch server and creates the index."""
    mappings = {}

    if self._raw_fields:
      if self._document_type not in mappings:
        mappings[self._document_type] = {}

      mappings[self._document_type]['dynamic_templates'] = [{
          'strings': {
              'match_mapping_type': 'string',
              'mapping': {
                  'fields': {
                      'raw': {
                          'type': 'keyword',
                          'index': 'false',
                          'ignore_above': self._ELASTIC_ANALYZER_STRING_LIMIT
                      }
                  }
              }
          }
      }]

    self._Connect()

    self._CreateIndexIfNotExists(self._index_name, mappings)