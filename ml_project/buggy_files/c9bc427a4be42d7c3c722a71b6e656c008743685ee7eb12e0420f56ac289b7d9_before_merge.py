def download(obj, provider, refiner, language, age, directory, encoding, single, force, hearing_impaired, min_score,
             max_workers, archives, verbose, path):
    """Download best subtitles.

    PATH can be an directory containing videos, a video file path or a video file name. It can be used multiple times.

    If an existing subtitle is detected (external or embedded) in the correct language, the download is skipped for
    the associated video.

    """
    # process parameters
    language = set(language)

    # scan videos
    videos = []
    ignored_videos = []
    errored_paths = []
    with click.progressbar(path, label='Collecting videos', item_show_func=lambda p: p or '') as bar:
        for p in bar:
            logger.debug('Collecting path %s', p)

            # non-existing
            if not os.path.exists(p):
                try:
                    video = Video.fromname(p)
                except:
                    logger.exception('Unexpected error while collecting non-existing path %s', p)
                    errored_paths.append(p)
                    continue
                if not force:
                    video.subtitle_languages |= set(search_external_subtitles(video.name, directory=directory).values())
                refine(video, episode_refiners=refiner, movie_refiners=refiner, embedded_subtitles=not force)
                videos.append(video)
                continue

            # directories
            if os.path.isdir(p):
                try:
                    scanned_videos = scan_videos(p, age=age, archives=archives)
                except:
                    logger.exception('Unexpected error while collecting directory path %s', p)
                    errored_paths.append(p)
                    continue
                for video in scanned_videos:
                    if not force:
                        video.subtitle_languages |= set(search_external_subtitles(video.name,
                                                                                  directory=directory).values())
                    if check_video(video, languages=language, age=age, undefined=single):
                        refine(video, episode_refiners=refiner, movie_refiners=refiner, embedded_subtitles=not force)
                        videos.append(video)
                    else:
                        ignored_videos.append(video)
                continue

            # other inputs
            try:
                video = scan_video(p)
            except:
                logger.exception('Unexpected error while collecting path %s', p)
                errored_paths.append(p)
                continue
            if not force:
                video.subtitle_languages |= set(search_external_subtitles(video.name, directory=directory).values())
            if check_video(video, languages=language, age=age, undefined=single):
                refine(video, episode_refiners=refiner, movie_refiners=refiner, embedded_subtitles=not force)
                videos.append(video)
            else:
                ignored_videos.append(video)

    # output errored paths
    if verbose > 0:
        for p in errored_paths:
            click.secho('%s errored' % p, fg='red')

    # output ignored videos
    if verbose > 1:
        for video in ignored_videos:
            click.secho('%s ignored - subtitles: %s / age: %d day%s' % (
                os.path.split(video.name)[1],
                ', '.join(str(s) for s in video.subtitle_languages) or 'none',
                video.age.days,
                's' if video.age.days > 1 else ''
            ), fg='yellow')

    # report collected videos
    click.echo('%s video%s collected / %s video%s ignored / %s error%s' % (
        click.style(str(len(videos)), bold=True, fg='green' if videos else None),
        's' if len(videos) > 1 else '',
        click.style(str(len(ignored_videos)), bold=True, fg='yellow' if ignored_videos else None),
        's' if len(ignored_videos) > 1 else '',
        click.style(str(len(errored_paths)), bold=True, fg='red' if errored_paths else None),
        's' if len(errored_paths) > 1 else '',
    ))

    # exit if no video collected
    if not videos:
        return

    # download best subtitles
    downloaded_subtitles = defaultdict(list)
    with AsyncProviderPool(max_workers=max_workers, providers=provider, provider_configs=obj['provider_configs']) as p:
        with click.progressbar(videos, label='Downloading subtitles',
                               item_show_func=lambda v: os.path.split(v.name)[1] if v is not None else '') as bar:
            for v in bar:
                scores = get_scores(v)
                subtitles = p.download_best_subtitles(p.list_subtitles(v, language - v.subtitle_languages),
                                                      v, language, min_score=scores['hash'] * min_score / 100,
                                                      hearing_impaired=hearing_impaired, only_one=single)
                downloaded_subtitles[v] = subtitles

        if p.discarded_providers:
            click.secho('Some providers have been discarded due to unexpected errors: %s' %
                        ', '.join(p.discarded_providers), fg='yellow')

    # save subtitles
    total_subtitles = 0
    for v, subtitles in downloaded_subtitles.items():
        saved_subtitles = save_subtitles(v, subtitles, single=single, directory=directory, encoding=encoding)[0]
        total_subtitles += len(saved_subtitles)

        if verbose > 0:
            click.echo('%s subtitle%s downloaded for %s' % (click.style(str(len(saved_subtitles)), bold=True),
                                                            's' if len(saved_subtitles) > 1 else '',
                                                            os.path.split(v.name)[1]))

        if verbose > 1:
            for s in saved_subtitles:
                matches = s.get_matches(v)
                score = compute_score(s, v)

                # score color
                score_color = None
                scores = get_scores(v)
                if isinstance(v, Movie):
                    if score < scores['title']:
                        score_color = 'red'
                    elif score < scores['title'] + scores['year'] + scores['release_group']:
                        score_color = 'yellow'
                    else:
                        score_color = 'green'
                elif isinstance(v, Episode):
                    if score < scores['series'] + scores['season'] + scores['episode']:
                        score_color = 'red'
                    elif score < scores['series'] + scores['season'] + scores['episode'] + scores['release_group']:
                        score_color = 'yellow'
                    else:
                        score_color = 'green'

                # scale score from 0 to 100 taking out preferences
                scaled_score = score
                if s.hearing_impaired == hearing_impaired:
                    scaled_score -= scores['hearing_impaired']
                scaled_score *= 100 / scores['hash']

                # echo some nice colored output
                click.echo('  - [{score}] {language} subtitle from {provider_name} (match on {matches})'.format(
                    score=click.style('{:5.1f}'.format(scaled_score), fg=score_color, bold=score >= scores['hash']),
                    language=s.language.name if s.language.country is None else '%s (%s)' % (s.language.name,
                                                                                             s.language.country.name),
                    provider_name=s.provider_name,
                    matches=', '.join(sorted(matches, key=scores.get, reverse=True))
                ))

    if verbose == 0:
        click.echo('Downloaded %s subtitle%s' % (click.style(str(total_subtitles), bold=True),
                                                 's' if total_subtitles > 1 else ''))