    def run(self, args, config):
        media_dir = config['local']['media_dir']
        scan_timeout = config['local']['scan_timeout']
        flush_threshold = config['local']['scan_flush_threshold']
        excluded_file_extensions = config['local']['excluded_file_extensions']
        excluded_file_extensions = tuple(
            bytes(file_ext.lower()) for file_ext in excluded_file_extensions)

        library = _get_library(args, config)

        file_mtimes, file_errors = path.find_mtimes(
            media_dir, follow=config['local']['scan_follow_symlinks'])

        logger.info('Found %d files in media_dir.', len(file_mtimes))

        if file_errors:
            logger.warning('Encountered %d errors while scanning media_dir.',
                           len(file_errors))
        for name in file_errors:
            logger.debug('Scan error %r for %r', file_errors[name], name)

        num_tracks = library.load()
        logger.info('Checking %d tracks from library.', num_tracks)

        uris_to_update = set()
        uris_to_remove = set()
        uris_in_library = set()

        for track in library.begin():
            abspath = translator.local_track_uri_to_path(track.uri, media_dir)
            mtime = file_mtimes.get(abspath)
            if mtime is None:
                logger.debug('Missing file %s', track.uri)
                uris_to_remove.add(track.uri)
            elif mtime > track.last_modified or args.force:
                uris_to_update.add(track.uri)
            uris_in_library.add(track.uri)

        logger.info('Removing %d missing tracks.', len(uris_to_remove))
        for uri in uris_to_remove:
            library.remove(uri)

        for abspath in file_mtimes:
            relpath = os.path.relpath(abspath, media_dir)
            uri = translator.path_to_local_track_uri(relpath)

            if b'/.' in relpath:
                logger.debug('Skipped %s: Hidden directory/file.', uri)
            elif relpath.lower().endswith(excluded_file_extensions):
                logger.debug('Skipped %s: File extension excluded.', uri)
            elif uri not in uris_in_library:
                uris_to_update.add(uri)

        logger.info(
            'Found %d tracks which need to be updated.', len(uris_to_update))
        logger.info('Scanning...')

        uris_to_update = sorted(uris_to_update, key=lambda v: v.lower())
        uris_to_update = uris_to_update[:args.limit]

        scanner = scan.Scanner(scan_timeout)
        progress = _Progress(flush_threshold, len(uris_to_update))

        for uri in uris_to_update:
            try:
                relpath = translator.local_track_uri_to_path(uri, media_dir)
                file_uri = path.path_to_uri(os.path.join(media_dir, relpath))
                result = scanner.scan(file_uri)
                tags, duration = result.tags, result.duration
                if not result.playable:
                    logger.warning('Failed %s: No audio found in file.', uri)
                elif duration < MIN_DURATION_MS:
                    logger.warning('Failed %s: Track shorter than %dms',
                                   uri, MIN_DURATION_MS)
                else:
                    mtime = file_mtimes.get(os.path.join(media_dir, relpath))
                    track = utils.convert_tags_to_track(tags).replace(
                        uri=uri, length=duration, last_modified=mtime)
                    if library.add_supports_tags_and_duration:
                        library.add(track, tags=tags, duration=duration)
                    else:
                        library.add(track)
                    logger.debug('Added %s', track.uri)
            except exceptions.ScannerError as error:
                logger.warning('Failed %s: %s', uri, error)

            if progress.increment():
                progress.log()
                if library.flush():
                    logger.debug('Progress flushed.')

        progress.log()
        library.close()
        logger.info('Done scanning.')
        return 0