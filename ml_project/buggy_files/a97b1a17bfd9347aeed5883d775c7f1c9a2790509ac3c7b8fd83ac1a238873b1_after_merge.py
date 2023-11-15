    def to_json(self, bulk_data_element_handler,
                bulk_data_threshold, dump_handler):
        """Converts a :class:`DataElement` to JSON representation.

        Parameters
        ----------
        bulk_data_element_handler: callable or None
            Callable that accepts a bulk data element and returns the
            "BulkDataURI" for retrieving the value of the data element
            via DICOMweb WADO-RS
        bulk_data_threshold: int
            Size of base64 encoded data element above which a value will be
            provided in form of a "BulkDataURI" rather than "InlineBinary"

        Returns
        -------
        dict
            Mapping representing a JSON encoded data element

        Raises
        ------
        TypeError
            When size of encoded data element exceeds `bulk_data_threshold`
            but `bulk_data_element_handler` is ``None`` and hence not callable

        """
        json_element = {'vr': self.VR, }
        if self.VR in jsonrep.BINARY_VR_VALUES:
            if not self.is_empty:
                binary_value = self.value
                encoded_value = base64.b64encode(binary_value).decode('utf-8')
                if len(encoded_value) > bulk_data_threshold:
                    if bulk_data_element_handler is None:
                        raise TypeError(
                            'No bulk data element handler provided to '
                            'generate URL for value of data element "{}".'
                            .format(self.name)
                        )
                    json_element['BulkDataURI'] = bulk_data_element_handler(
                        self
                    )
                else:
                    logger.info(
                        'encode bulk data element "{}" inline'.format(
                            self.name
                        )
                    )
                    json_element['InlineBinary'] = encoded_value
        elif self.VR == 'SQ':
            # recursive call to co-routine to format sequence contents
            value = [
                json.loads(e.to_json(
                    bulk_data_element_handler=bulk_data_element_handler,
                    bulk_data_threshold=bulk_data_threshold,
                    dump_handler=dump_handler
                ))
                for e in self
            ]
            json_element['Value'] = value
        elif self.VR == 'PN':
            if not self.is_empty:
                elem_value = []
                if self.VM > 1:
                    value = self.value
                else:
                    value = [self.value]
                for v in value:
                    if compat.in_py2:
                        v = PersonNameUnicode(v, 'UTF8')
                    comps = {'Alphabetic': v.components[0]}
                    if len(v.components) > 1:
                        comps['Ideographic'] = v.components[1]
                    if len(v.components) > 2:
                        comps['Phonetic'] = v.components[2]
                    elem_value.append(comps)
                json_element['Value'] = elem_value
        elif self.VR == 'AT':
            if not self.is_empty:
                value = self.value
                if self.VM == 1:
                    value = [value]
                json_element['Value'] = [format(v, '08X') for v in value]
        else:
            if not self.is_empty:
                if self.VM > 1:
                    value = self.value
                else:
                    value = [self.value]
                json_element['Value'] = [v for v in value]
        if hasattr(json_element, 'Value'):
            json_element['Value'] = jsonrep.convert_to_python_number(
                json_element['Value'], self.VR
            )
        return json_element