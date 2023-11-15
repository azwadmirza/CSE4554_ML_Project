    def program(self, file_or_path, file_format=None, **kwargs):
        """! @brief Program a file into flash.
        
        @param self
        @param file_or_path Either a string that is a path to a file, or a file-like object.
        @param file_format Optional file format name, one of "bin", "hex", "elf", "axf". If not provided,
            the file's extension will be used. If a file object is passed for _file_or_path_ then
            this parameter must be used to set the format.
        @param kwargs Optional keyword arguments for format-specific parameters.
        
        The only current format-specific keyword parameters are for the binary format:
        - `base_address`: Memory address at which to program the binary data. If not set, the base
            of the boot memory will be used.
        - `skip`: Number of bytes to skip at the start of the binary file. Does not affect the
            base address.
        
        @exception FileNotFoundError Provided file_or_path string does not reference a file.
        @exception ValueError Invalid argument value, for instance providing a file object but
            not setting file_format.
        """
        isPath = isinstance(file_or_path, six.string_types)
        
        # Check for valid path first.
        if isPath and not os.path.isfile(file_or_path):
            raise FileNotFoundError_(errno.ENOENT, "No such file: '{}'".format(file_or_path))
        
        # If no format provided, use the file's extension.
        if not file_format:
            if isPath:
                # Extract the extension from the path.
                file_format = os.path.splitext(file_or_path)[1][1:]
                
                # Explicitly check for no extension.
                if file_format == '':
                    raise ValueError("file path '{}' does not have an extension and "
                                        "no format is set".format(file_or_path))
            else:
                raise ValueError("file object provided but no format is set")
        
        # Check the format is one we understand.
        if file_format not in self._format_handlers:
            raise ValueError("unknown file format '%s'" % file_format)
            
        self._loader = FlashLoader(self._session,
                                    progress=self._progress,
                                    chip_erase=self._chip_erase,
                                    trust_crc=self._trust_crc)
        
        file_obj = None
        try:
            # Open the file if a path was provided.
            if isPath:
                mode = 'rb'
                if file_format == 'hex':
                    # hex file must be read as plain text file
                    mode = 'r'
                file_obj = open(file_or_path, mode)
            else:
                file_obj = file_or_path

            # Pass to the format-specific programmer.
            self._format_handlers[file_format](file_obj, **kwargs)
            self._loader.commit()
        finally:
            if isPath and file_obj is not None:
                file_obj.close()