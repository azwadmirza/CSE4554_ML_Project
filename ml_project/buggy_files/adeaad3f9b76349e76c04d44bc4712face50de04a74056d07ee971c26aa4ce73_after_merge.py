    def _parse_files(self, filepath, override=False):
        """Parse files from a glob

        :param str filepath: Nginx config file path
        :param bool override: Whether to parse a file that has been parsed
        :returns: list of parsed tree structures
        :rtype: list

        """
        files = glob.glob(filepath) # nginx on unix calls glob(3) for this
                                    # XXX Windows nginx uses FindFirstFile, and
                                    # should have a narrower call here
        trees = []
        for item in files:
            if item in self.parsed and not override:
                continue
            try:
                with io.open(item, "r", encoding="utf-8") as _file:
                    parsed = nginxparser.load(_file)
                    self.parsed[item] = parsed
                    trees.append(parsed)
            except IOError:
                logger.warning("Could not open file: %s", item)
            except UnicodeDecodeError:
                logger.warning("Could not read file: %s due to invalid "
                               "character. Only UTF-8 encoding is "
                               "supported.", item)
            except pyparsing.ParseException as err:
                logger.debug("Could not parse file: %s due to %s", item, err)
        return trees