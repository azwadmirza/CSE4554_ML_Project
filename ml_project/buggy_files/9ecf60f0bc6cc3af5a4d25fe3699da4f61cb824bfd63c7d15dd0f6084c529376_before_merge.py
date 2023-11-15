def generate_sample_ep(multi=None, abd=False, sports=False, anime_type=None):
    # make a fake episode object
    ep = TVEpisode(2, 3, 3, 'Ep Name')

    # pylint: disable=protected-access
    ep.status = DOWNLOADED
    ep.quality = Quality.HDTV
    ep.airdate = datetime.date(2011, 3, 9)

    if abd:
        ep.release_name = 'Show.Name.2011.03.09.HDTV.x264-RLSGROUP'
        ep.series.air_by_date = 1
    elif sports:
        ep.release_name = 'Show.Name.2011.03.09.HDTV.x264-RLSGROUP'
        ep.series.sports = 1
    else:
        if anime_type != 3:
            ep.series.anime = 1
            ep.release_name = 'Show.Name.003.HDTV.x264-RLSGROUP'
        else:
            ep.release_name = 'Show.Name.S02E03.HDTV.x264-RLSGROUP'

    if multi is not None:
        ep.name = 'Ep Name (1)'

        if anime_type != 3:
            ep.series.anime = 1

            ep.release_name = 'Show.Name.003-004.HDTV.x264-RLSGROUP'

            secondEp = TVEpisode(2, 4, 4, 'Ep Name (2)')
            secondEp.status = DOWNLOADED
            secondEp.quality = Quality.HDTV
            secondEp.release_name = ep.release_name

            ep.related_episodes.append(secondEp)
        else:
            ep.release_name = 'Show.Name.S02E03E04E05.HDTV.x264-RLSGROUP'

            secondEp = TVEpisode(2, 4, 4, 'Ep Name (2)')
            secondEp.status = DOWNLOADED
            secondEp.quality = Quality.HDTV
            secondEp.release_name = ep.release_name

            thirdEp = TVEpisode(2, 5, 5, 'Ep Name (3)')
            thirdEp.status = DOWNLOADED
            thirdEp.quality = Quality.HDTV
            thirdEp.release_name = ep.release_name

            ep.related_episodes.append(secondEp)
            ep.related_episodes.append(thirdEp)

    return ep