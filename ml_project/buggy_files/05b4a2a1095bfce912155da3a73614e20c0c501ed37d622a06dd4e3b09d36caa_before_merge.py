    def do_i_hate_this(cls, task, genre_patterns, artist_patterns, 
                       album_patterns, whitelist_patterns):
        """Process group of patterns (warn or skip) and returns True if
        task is hated and not whitelisted.
        """
        hate = False
        try:
            genre = task.items[0].genre
        except:
            genre = u''
        if genre and genre_patterns:
            if cls.match_patterns(genre, genre_patterns):
                hate = True
        if not hate and task.cur_album and album_patterns:
            if cls.match_patterns(task.cur_album, album_patterns):
                hate = True
        if not hate and task.cur_artist and artist_patterns:
            if cls.match_patterns(task.cur_artist, artist_patterns):
                hate = True
        if hate and whitelist_patterns:
            if cls.match_patterns(task.cur_artist, whitelist_patterns):
                hate = False
        return hate