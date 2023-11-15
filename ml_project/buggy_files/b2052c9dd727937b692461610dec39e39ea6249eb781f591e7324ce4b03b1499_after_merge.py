    def relevance_score_remote_torrent(self, torrent_name):
        """
        Calculate the relevance score of a remote torrent, based on the name and the matchinfo object
        of the last torrent from the database.
        The algorithm used is the same one as in search_in_local_torrents_db in SqliteCacheDBHandler.py.
        """
        if self.latest_matchinfo_torrent is None:
            return 0.0
        matchinfo, keywords = self.latest_matchinfo_torrent

        # Make sure the strings are utf-8 encoded
        if not isinstance(keywords, text_type):
            keywords = keywords.decode('raw_unicode_escape')
        if not isinstance(torrent_name, text_type):
            torrent_name = torrent_name.decode('raw_unicode_escape')

        num_phrases, num_cols, num_rows = unpack_from('III', matchinfo)
        unpack_str = 'I' * (3 * num_cols * num_phrases)
        matchinfo = unpack_from('I' * 9 + unpack_str, matchinfo)[9:]

        score = 0.0
        for phrase_ind in xrange(num_phrases):
            rows_with_term = matchinfo[3 * (phrase_ind * num_cols) + 2]
            term_freq = torrent_name.lower().count(keywords[phrase_ind])

            inv_doc_freq = math.log((num_rows - rows_with_term + 0.5) / (rows_with_term + 0.5), 2)
            right_side = ((term_freq * (1.2 + 1)) / (term_freq + 1.2))

            score += inv_doc_freq * right_side
        return score