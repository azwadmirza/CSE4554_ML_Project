    def parse_tags(self, ntags, group_name='root', group_dict={}):
        """Parse the DM file into a dictionary.

        """
        unnammed_data_tags = 0
        unnammed_group_tags = 0
        for tag in range(ntags):
            _logger.debug('Reading tag name at address: %s', self.f.tell())
            tag_header = self.parse_tag_header()
            tag_name = tag_header['tag_name']

            skip = True if (group_name == "ImageData" and
                            tag_name == "Data") else False
            _logger.debug('Tag name: %s', tag_name[:20])
            _logger.debug('Tag ID: %s', tag_header['tag_id'])

            if tag_header['tag_id'] == 21:  # it's a TagType (DATA)
                if not tag_name:
                    tag_name = 'Data%i' % unnammed_data_tags
                    unnammed_data_tags += 1

                _logger.debug('Reading data tag at address: %s', self.f.tell())

                # Start reading the data
                # Raises IOError if it is wrong
                self.check_data_tag_delimiter()
                infoarray_size = self.read_l_or_q(self.f, 'big')
                _logger.debug("Infoarray size: %s", infoarray_size)
                if infoarray_size == 1:  # Simple type
                    _logger.debug("Reading simple data")
                    etype = self.read_l_or_q(self.f, "big")
                    data = self.read_simple_data(etype)
                elif infoarray_size == 2:  # String
                    _logger.debug("Reading string")
                    enctype = self.read_l_or_q(self.f, "big")
                    if enctype != 18:
                        raise IOError("Expected 18 (string), got %i" % enctype)
                    string_length = self.parse_string_definition()
                    data = self.read_string(string_length, skip=skip)
                elif infoarray_size == 3:  # Array of simple type
                    _logger.debug("Reading simple array")
                    # Read array header
                    enctype = self.read_l_or_q(self.f, "big")
                    if enctype != 20:  # Should be 20 if it is an array
                        raise IOError("Expected 20 (string), got %i" % enctype)
                    size, enc_eltype = self.parse_array_definition()
                    data = self.read_array(size, enc_eltype, skip=skip)
                elif infoarray_size > 3:
                    enctype = self.read_l_or_q(self.f, "big")
                    if enctype == 15:  # It is a struct
                        _logger.debug("Reading struct")
                        definition = self.parse_struct_definition()
                        _logger.debug("Struct definition %s", definition)
                        data = self.read_struct(definition, skip=skip)
                    elif enctype == 20:  # It is an array of complex type
                        # Read complex array info
                        # The structure is
                        # 20 <4>, ?  <4>, enc_dtype <4>, definition <?>,
                        # size <4>
                        enc_eltype = self.read_l_or_q(self.f, "big")
                        if enc_eltype == 15:  # Array of structs
                            _logger.debug("Reading array of structs")
                            definition = self.parse_struct_definition()
                            size = self.read_l_or_q(self.f, "big")
                            _logger.debug("Struct definition: %s", definition)
                            _logger.debug("Array size: %s", size)
                            data = self.read_array(
                                size=size,
                                enc_eltype=enc_eltype,
                                extra={"definition": definition},
                                skip=skip)
                        elif enc_eltype == 18:  # Array of strings
                            _logger.debug("Reading array of strings")
                            string_length = \
                                self.parse_string_definition()
                            size = self.read_l_or_q(self.f, "big")
                            data = self.read_array(
                                size=size,
                                enc_eltype=enc_eltype,
                                extra={"length": string_length},
                                skip=skip)
                        elif enc_eltype == 20:  # Array of arrays
                            _logger.debug("Reading array of arrays")
                            el_length, enc_eltype = \
                                self.parse_array_definition()
                            size = self.read_l_or_q(self.f, "big")
                            data = self.read_array(
                                size=size,
                                enc_eltype=enc_eltype,
                                extra={"size": el_length},
                                skip=skip)

                else:  # Infoarray_size < 1
                    raise IOError("Invalided infoarray size ", infoarray_size)

                group_dict[tag_name] = data

            elif tag_header['tag_id'] == 20:  # it's a TagGroup (GROUP)
                if not tag_name:
                    tag_name = 'TagGroup%i' % unnammed_group_tags
                    unnammed_group_tags += 1
                _logger.debug(
                    'Reading Tag group at address: %s',
                    self.f.tell())
                ntags = self.parse_tag_group(size=True)[2]
                group_dict[tag_name] = {}
                self.parse_tags(
                    ntags=ntags,
                    group_name=tag_name,
                    group_dict=group_dict[tag_name])
            else:
                _logger.debug('File address:', self.f.tell())
                raise DM3TagIDError(tag_header['tag_id'])