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
        # TODO: Determine whether more VRs need to be converted to strings
        _VRs_TO_QUOTE = ['AT', ]
        json_element = {'vr': self.VR, }
        if self.VR in jsonrep.BINARY_VR_VALUES:
            if self.value is not None:
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
            elem_value = self.value
            if elem_value is not None:
                if compat.in_py2:
                    elem_value = PersonNameUnicode(elem_value, 'UTF8')
                if len(elem_value.components) > 2:
                    json_element['Value'] = [
                        {'Phonetic': elem_value.components[2], },
                    ]
                elif len(elem_value.components) > 1:
                    json_element['Value'] = [
                        {'Ideographic': elem_value.components[1], },
                    ]
                else:
                    json_element['Value'] = [
                        {'Alphabetic': elem_value.components[0], },
                    ]
        else:
            if self.value is not None:
                is_multivalue = isinstance(self.value, MultiValue)
                if self.VM > 1 or is_multivalue:
                    value = self.value
                else:
                    value = [self.value]
                # ensure it's a list and not another iterable
                # (e.g. tuple), which would not be JSON serializable
                if self.VR in _VRs_TO_QUOTE:
                    json_element['Value'] = [str(v) for v in value]
                else:
                    json_element['Value'] = [v for v in value]
        if hasattr(json_element, 'Value'):
            json_element['Value'] = jsonrep.convert_to_python_number(
                json_element['Value'], self.VR
            )
        return json_element