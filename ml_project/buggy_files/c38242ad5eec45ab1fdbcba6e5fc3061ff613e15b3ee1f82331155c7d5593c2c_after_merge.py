    def _parse_error_from_body(self, response):
        xml_contents = response['body']
        root = self._parse_xml_string_to_dom(xml_contents)
        parsed = self._build_name_to_xml_node(root)
        self._replace_nodes(parsed)
        if root.tag == 'Error':
            # This is an S3 error response.  First we'll populate the
            # response metadata.
            metadata = self._populate_response_metadata(response)
            # The RequestId and the HostId are already in the
            # ResponseMetadata, but are also duplicated in the XML
            # body.  We don't need these values in both places,
            # we'll just remove them from the parsed XML body.
            parsed.pop('RequestId', '')
            parsed.pop('HostId', '')
            return {'Error': parsed, 'ResponseMetadata': metadata}
        elif 'RequestId' in parsed:
            # Other rest-xml serivces:
            parsed['ResponseMetadata'] = {'RequestId': parsed.pop('RequestId')}
        default = {'Error': {'Message': '', 'Code': ''}}
        merge_dicts(default, parsed)
        return default