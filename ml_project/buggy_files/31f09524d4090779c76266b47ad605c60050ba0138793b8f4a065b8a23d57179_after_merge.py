  def WriteHeader(self):
    """Connects to the Elasticsearch server and creates the index."""
    mappings = {}

    if self._raw_fields:
      # This cannot be static because we use the value of self._document_type
      # from arguments.
      mappings = {
          'dynamic_templates': [{
              'strings': {
                  'mapping': {
                      'fields': {
                          'raw': {
                              'ignore_above': (
                                  self._ELASTIC_ANALYZER_STRING_LIMIT),
                              'index': 'false',
                              'type': 'keyword',
                          },
                      },
                  },
                  'match_mapping_type': 'string',
              },
          }],
      }

      # TODO: Remove once Elasticsearch v6.x is deprecated.
      if self._GetClientMajorVersion() < 7:
        mappings = {self._document_type: mappings}

    self._Connect()

    self._CreateIndexIfNotExists(self._index_name, mappings)