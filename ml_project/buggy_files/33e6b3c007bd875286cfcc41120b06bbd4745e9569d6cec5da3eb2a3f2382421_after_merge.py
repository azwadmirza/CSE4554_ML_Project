    def __make_file_provider(self, dirname, filename, recurse, removeself, excludekeys):
        """Change parsed FileKey to action provider"""
        regex = ''
        if recurse:
            search = 'walk.files'
            path = dirname
            if filename.startswith('*.'):
                filename = filename.replace('*.', '.')
            if filename == '.*':
                if removeself:
                    search = 'walk.all'
            else:
                import fnmatch
                regex = ' regex="%s" ' % (fnmatch.translate(filename))
        else:
            search = 'glob'
            path = os.path.join(dirname, filename)
            if path.find('*') == -1:
                search = 'file'
        excludekeysxml = ''
        if excludekeys:
            if len(excludekeys) > 1:
                # multiple
                exclude_str = '(%s)' % '|'.join(excludekeys)
            else:
                # just one
                exclude_str = excludekeys[0]
            excludekeysxml = 'nwholeregex="%s"' % xml_escape(exclude_str)
        action_str = u'<option command="delete" search="%s" path="%s" %s %s/>' % \
                     (search, xml_escape(path), regex, excludekeysxml)
        yield Delete(parseString(action_str).childNodes[0])
        if removeself:
            action_str = u'<option command="delete" search="file" path="%s"/>' % \
                         (xml_escape(dirname))
            yield Delete(parseString(action_str).childNodes[0])