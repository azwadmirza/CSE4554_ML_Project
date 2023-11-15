    def update_show_indexer_metadata(self, show_obj):
        if self.show_metadata and show_obj and self._has_show_metadata(show_obj):
            logger.log(
                u"Metadata provider " + self.name + " updating show indexer info metadata file for " + show_obj.name,
                logger.DEBUG)

            nfo_file_path = self.get_show_file_path(show_obj)
            assert isinstance(nfo_file_path, text_type)

            try:
                with io.open(nfo_file_path, 'rb', encoding='utf8') as xmlFileObj:
                    showXML = etree.ElementTree(file=xmlFileObj)

                indexerid = showXML.find('id')

                root = showXML.getroot()
                if indexerid is not None:
                    indexerid.text = str(show_obj.indexerid)
                else:
                    etree.SubElement(root, "id").text = str(show_obj.indexerid)

                # Make it purdy
                helpers.indentXML(root)

                showXML.write(nfo_file_path, encoding='UTF-8')
                helpers.chmodAsParent(nfo_file_path)

                return True
            except etree.ParseError as error:
                logger.log('Received an invalid XML for {show}, try again later. Error: {error_msg}'.format
                           (show=show_obj.name, error_msg=error), logger.WARNING)
            except IOError as e:
                logger.log(
                    u"Unable to write file to " + nfo_file_path + " - are you sure the folder is writable? " + ex(e),
                    logger.ERROR)