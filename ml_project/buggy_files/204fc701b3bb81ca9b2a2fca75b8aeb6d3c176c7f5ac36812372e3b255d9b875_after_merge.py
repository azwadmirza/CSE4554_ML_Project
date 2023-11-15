def refine_from_db(path, video):
    if isinstance(video, Episode):
        db = sqlite3.connect(os.path.join(args.config_dir, 'db', 'bazarr.db'), timeout=30)
        c = db.cursor()
        data = c.execute("SELECT table_shows.title, table_episodes.season, table_episodes.episode, table_episodes.title, table_shows.year, table_shows.tvdbId, table_shows.alternateTitles, table_episodes.format, table_episodes.resolution, table_episodes.video_codec, table_episodes.audio_codec FROM table_episodes INNER JOIN table_shows on table_shows.sonarrSeriesId = table_episodes.sonarrSeriesId WHERE table_episodes.path = ?", (unicode(path_replace_reverse(path)),)).fetchone()
        db.close()
        if data:
            video.series = re.sub(r'(\(\d\d\d\d\))' , '', data[0])
            video.season = int(data[1])
            video.episode = int(data[2])
            video.title = data[3]
            if data[4]:
                if int(data[4]) > 0: video.year = int(data[4])
            video.series_tvdb_id = int(data[5])
            video.alternative_series = ast.literal_eval(data[6])
            if not video.format:
                video.format = str(data[7])
            if not video.resolution:
                video.resolution = str(data[8])
            if not video.video_codec:
                if data[9]: video.video_codec = data[9]
            if not video.audio_codec:
                if data[10]: video.audio_codec = data[10]
    elif isinstance(video, Movie):
        db = sqlite3.connect(os.path.join(args.config_dir, 'db', 'bazarr.db'), timeout=30)
        c = db.cursor()
        data = c.execute("SELECT title, year, alternativeTitles, format, resolution, video_codec, audio_codec, imdbId FROM table_movies WHERE path = ?", (unicode(path_replace_reverse_movie(path)),)).fetchone()
        db.close()
        if data:
            video.title = re.sub(r'(\(\d\d\d\d\))' , '', data[0])
            if data[1]:
                if int(data[1]) > 0: video.year = int(data[1])
            if data[7]: video.imdb_id = data[7]
            video.alternative_titles = ast.literal_eval(data[2])
            if not video.format:
                if data[3]: video.format = data[3]
            if not video.resolution:
                if data[4]: video.resolution = data[4]
            if not video.video_codec:
                if data[5]: video.video_codec = data[5]
            if not video.audio_codec:
                if data[6]: video.audio_codec = data[6]

    return video