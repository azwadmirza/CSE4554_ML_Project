    def _get_include_path(self, arg):
        """Converts an Apache Include directive into Augeas path.

        Converts an Apache Include directive argument into an Augeas
        searchable path

        .. todo:: convert to use os.path.join()

        :param str arg: Argument of Include directive

        :returns: Augeas path string
        :rtype: str

        """
        # Check to make sure only expected characters are used <- maybe remove
        # validChars = re.compile("[a-zA-Z0-9.*?_-/]*")
        # matchObj = validChars.match(arg)
        # if matchObj.group() != arg:
        #     logger.error("Error: Invalid regexp characters in %s", arg)
        #     return []

        # Standardize the include argument based on server root
        if not arg.startswith("/"):
            # Normpath will condense ../
            arg = os.path.normpath(os.path.join(self.root, arg))

        # Attempts to add a transform to the file if one does not already exist
        if os.path.isdir(arg):
            self._parse_file(os.path.join(arg, "*"))
        else:
            self._parse_file(arg)

        # Argument represents an fnmatch regular expression, convert it
        # Split up the path and convert each into an Augeas accepted regex
        # then reassemble
        split_arg = arg.split("/")
        for idx, split in enumerate(split_arg):
            if any(char in ApacheParser.fnmatch_chars for char in split):
                # Turn it into a augeas regex
                # TODO: Can this instead be an augeas glob instead of regex
                split_arg[idx] = ("* [label()=~regexp('%s')]" %
                                  self.fnmatch_to_re(split))
        # Reassemble the argument
        # Note: This also normalizes the argument /serverroot/ -> /serverroot
        arg = "/".join(split_arg)

        return get_aug_path(arg)