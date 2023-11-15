def get_arguments(raw_args=None, to_group=True, to_merge=True):
    parser = argparse.ArgumentParser(
        description='Download and convert songs from Spotify, Youtube etc.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    if to_merge:
        config_file = os.path.join(sys.path[0], 'config.yml')
        config = merge(default_conf['spotify-downloader'], get_config(config_file))
    else:
        config = default_conf['spotify-downloader']

    if to_group:
        group = parser.add_mutually_exclusive_group(required=True)

        group.add_argument(
            '-s', '--song', help='download song by spotify link or name')
        group.add_argument(
            '-l', '--list', help='download songs from a file')
        group.add_argument(
            '-p', '--playlist', help='load songs from playlist URL into <playlist_name>.txt')
        group.add_argument(
            '-b', '--album', help='load songs from album URL into <album_name>.txt')
        group.add_argument(
            '-u', '--username',
            help="load songs from user's playlist into <playlist_name>.txt")

    parser.add_argument(
        '-m', '--manual', default=config['manual'],
        help='choose the song to download manually', action='store_true')
    parser.add_argument(
        '-nm', '--no-metadata', default=config['no-metadata'],
        help='do not embed metadata in songs', action='store_true')
    parser.add_argument(
        '-a', '--avconv', default=config['avconv'],
        help='Use avconv for conversion otherwise set defaults to ffmpeg',
        action='store_true')
    parser.add_argument(
        '-f', '--folder', default=os.path.relpath(config['folder'], os.getcwd()),
        help='path to folder where files will be stored in')
    parser.add_argument(
        '--overwrite', default=config['overwrite'],
        help='change the overwrite policy',
        choices={'prompt', 'force', 'skip'})
    parser.add_argument(
        '-i', '--input-ext', default=config['input-ext'],
        help='prefered input format .m4a or .webm (Opus)')
    parser.add_argument(
        '-o', '--output-ext', default=config['output-ext'],
        help='prefered output extension .mp3 or .m4a (AAC)')
    parser.add_argument(
        '-ff', '--file-format', default=config['file-format'],
        help='File format to save the downloaded song with, each tag '
             'is surrounded by curly braces. Possible formats: '
             '{}'.format([internals.formats[x] for x in internals.formats]),
        action='store_true')
    parser.add_argument(
        '-dm', '--download-only-metadata', default=config['download-only-metadata'],
        help='download songs for which metadata is found',
        action='store_true')
    parser.add_argument(
        '-d', '--dry-run', default=config['dry-run'],
        help='Show only track title and YouTube URL',
        action='store_true')
    parser.add_argument(
        '-mo', '--music-videos-only', default=config['music-videos-only'],
        help='Search only for music on Youtube',
        action='store_true')
    parser.add_argument(
        '-ns', '--no-spaces', default=config['no-spaces'],
        help='Replace spaces with underscores in file names',
        action='store_true')
    parser.add_argument(
        '-ll', '--log-level', default=config['log-level'],
        choices=_LOG_LEVELS_STR,
        type=str.upper,
        help='set log verbosity')
    parser.add_argument(
        '-c', '--config', default=None,
        help='Replace with custom config.yml file')    

    parsed = parser.parse_args(raw_args)

    if parsed.config is not None and to_merge:
        parsed = override_config(parsed.config,parser)
        
    parsed.log_level = log_leveller(parsed.log_level)
    
    return parsed