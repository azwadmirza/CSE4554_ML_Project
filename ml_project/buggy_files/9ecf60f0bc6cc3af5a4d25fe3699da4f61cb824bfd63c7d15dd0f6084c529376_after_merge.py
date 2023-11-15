def generate_sample_ep(multi=None, abd=False, sports=False, anime_type=None):
    series = Series(indexer=1, indexerid=12345, lang='en')
    series.name = 'Show Name'
    series.genre = 'Comedy'
    if anime_type:
        series.anime = 1

    # make a fake episode object
    ep = Episode(series=series, season=2, episode=3)

    ep.status = DOWNLOADED
    ep.quality = Quality.HDTV
    ep.airdate = datetime.date(2011, 3, 9)
    ep.name = 'Ep Name'
    ep.absolute_number = 13
    ep.release_name = 'Show.Name.S02E03.HDTV.x264-RLSGROUP'
    ep.is_proper = True

    if abd:
        ep.release_name = 'Show.Name.2011.03.09.HDTV.x264-RLSGROUP'
        ep.series.air_by_date = 1
    elif sports:
        ep.release_name = 'Show.Name.2011.03.09.HDTV.x264-RLSGROUP'
        ep.series.sports = 1
    elif anime_type:
        ep.release_name = 'Show.Name.013.HDTV.x264-RLSGROUP'

    if multi is not None:
        ep.name = 'Ep Name (1)'
        ep.release_name = 'Show.Name.S02E03E04E05.HDTV.x264-RLSGROUP'
        if anime_type:
            ep.release_name = 'Show.Name.013-015.HDTV.x264-RLSGROUP'

        second_ep = Episode(series, 2, 4)
        second_ep.name = 'Ep Name (2)'
        second_ep.status = DOWNLOADED
        second_ep.quality = Quality.HDTV
        second_ep.absolute_number = 14
        second_ep.release_name = ep.release_name

        third_ep = Episode(series, 2, 5)
        third_ep.name = 'Ep Name (3)'
        third_ep.status = DOWNLOADED
        third_ep.quality = Quality.HDTV
        third_ep.absolute_number = 15
        third_ep.release_name = ep.release_name

        ep.related_episodes.append(second_ep)
        ep.related_episodes.append(third_ep)

    return ep