    def parse_tool_output(self, text, path_list, is_album):
        """Given the  output from bs1770gain, parse the text and
        return a list of dictionaries
        containing information about each analyzed file.
        """
        per_file_gain = {}
        album_gain = {}  # mutable variable so it can be set from handlers
        parser = xml.parsers.expat.ParserCreate(encoding='utf-8')
        state = {'file': None, 'gain': None, 'peak': None}

        def start_element_handler(name, attrs):
            if name == u'track':
                state['file'] = bytestring_path(attrs[u'file'])
                if state['file'] in per_file_gain:
                    raise ReplayGainError(
                        u'duplicate filename in bs1770gain output')
            elif name == u'integrated':
                state['gain'] = float(attrs[u'lu'])
            elif name == u'sample-peak':
                state['peak'] = float(attrs[u'factor'])

        def end_element_handler(name):
            if name == u'track':
                if state['gain'] is None or state['peak'] is None:
                    raise ReplayGainError(u'could not parse gain or peak from '
                                          'the output of bs1770gain')
                per_file_gain[state['file']] = Gain(state['gain'],
                                                    state['peak'])
                state['gain'] = state['peak'] = None
            elif name == u'summary':
                if state['gain'] is None or state['peak'] is None:
                    raise ReplayGainError(u'could not parse gain or peak from '
                                          'the output of bs1770gain')
                album_gain["album"] = Gain(state['gain'], state['peak'])
                state['gain'] = state['peak'] = None
        parser.StartElementHandler = start_element_handler
        parser.EndElementHandler = end_element_handler
        parser.Parse(text, True)

        if len(per_file_gain) != len(path_list):
            raise ReplayGainError(
                u'the number of results returned by bs1770gain does not match '
                'the number of files passed to it')

        # bs1770gain does not return the analysis results in the order that
        # files are passed on the command line, because it is sorting the files
        # internally. We must recover the order from the filenames themselves.
        try:
            out = [per_file_gain[os.path.basename(p)] for p in path_list]
        except KeyError:
            raise ReplayGainError(
                u'unrecognized filename in bs1770gain output '
                '(bs1770gain can only deal with utf-8 file names)')
        if is_album:
            out.append(album_gain["album"])
        return out