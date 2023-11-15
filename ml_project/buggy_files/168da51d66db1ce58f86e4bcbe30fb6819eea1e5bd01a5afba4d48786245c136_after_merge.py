def override_config(config_file, parser, raw_args=None):
    """ Override default dict with config dict passed as comamnd line argument. """
    config_file = os.path.realpath(config_file)
    config = merge(default_conf['spotify-downloader'], get_config(config_file))

    parser.set_defaults(manual=config['manual'])
    parser.set_defaults(no_metadata=config['no-metadata'])
    parser.set_defaults(avconv=config['avconv'])
    parser.set_defaults(folder=os.path.relpath(config['folder'], os.getcwd()))
    parser.set_defaults(overwrite=config['overwrite'])
    parser.set_defaults(input_ext=config['input-ext'])
    parser.set_defaults(output_ext=config['output-ext'])
    parser.set_defaults(download_only_metadata=config['download-only-metadata'])
    parser.set_defaults(dry_run=config['dry-run'])
    parser.set_defaults(music_videos_only=config['music-videos-only'])
    parser.set_defaults(no_spaces=config['no-spaces'])
    parser.set_defaults(file_format=config['file-format'])
    parser.set_defaults(no_spaces=config['youtube-api-key'])
    parser.set_defaults(log_level=config['log-level'])

    return parser.parse_args(raw_args)