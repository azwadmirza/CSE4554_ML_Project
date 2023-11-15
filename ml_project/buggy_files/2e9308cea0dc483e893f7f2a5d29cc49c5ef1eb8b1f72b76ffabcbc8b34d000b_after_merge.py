    def retrieveShowMetadata(self, folder):
        """
        Used only when mass adding Existing Shows, using previously generated Show metadata to reduce the need to query TVDB.
        """

        empty_return = (None, None, None)

        assert isinstance(folder, text_type)

        metadata_path = ek(os.path.join, folder, self._show_metadata_filename)

        if not ek(os.path.isdir, folder) or not ek(os.path.isfile, metadata_path):
            logger.log(u"Can't load the metadata file from " + metadata_path + ", it doesn't exist", logger.DEBUG)
            return empty_return

        logger.log(u"Loading show info from metadata file in " + folder, logger.DEBUG)

        try:
            with io.open(metadata_path, 'rb', encoding='utf8') as xmlFileObj:
                showXML = etree.ElementTree(file=xmlFileObj)

            if showXML.findtext('title') is None or (showXML.findtext('tvdbid') is None and showXML.findtext('id') is None):
                logger.log(u"Invalid info in tvshow.nfo (missing name or id): %s %s %s" % (showXML.findtext('title'), showXML.findtext('tvdbid'), showXML.findtext('id')))
                return empty_return

            name = showXML.findtext('title')

            if showXML.findtext('tvdbid'):
                indexer_id = int(showXML.findtext('tvdbid'))
            elif showXML.findtext('id'):
                indexer_id = int(showXML.findtext('id'))
            else:
                logger.log(u"Empty <id> or <tvdbid> field in NFO, unable to find a ID", logger.WARNING)
                return empty_return

            if indexer_id is None:
                logger.log(u"Invalid Indexer ID (" + str(indexer_id) + "), not using metadata file", logger.WARNING)
                return empty_return

            indexer = None
            if showXML.find('episodeguide/url'):
                epg_url = showXML.findtext('episodeguide/url').lower()
                if str(indexer_id) in epg_url:
                    if 'thetvdb.com' in epg_url:
                        indexer = 1
                    elif 'tvrage' in epg_url:
                        logger.log(u"Invalid Indexer ID (" + str(indexer_id) + "), not using metadata file because it has TVRage info", logger.WARNING)
                        return empty_return

        except Exception as e:
            logger.log(
                u"There was an error parsing your existing metadata file: '" + metadata_path + "' error: " + ex(e),
                logger.WARNING)
            return empty_return

        return indexer_id, name, indexer