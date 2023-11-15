    def unpack_rar_files(dirpath):
        """Unpack any existing rar files present in the specified dirpath.

        :param dirpath: the directory path to be used
        :type dirpath: str
        """
        from . import process_tv
        for root, _, files in os.walk(dirpath, topdown=False):
            rar_files = [rar_file for rar_file in files if is_rar_file(rar_file)]
            if rar_files and app.UNPACK:
                video_files = [video_file for video_file in files if is_media_file(video_file)]
                if u'_UNPACK' not in root.upper() and (not video_files or root == app.TV_DOWNLOAD_DIR):
                    logger.debug(u'Found rar files in post-process folder: %s', rar_files)
                    process_tv.ProcessResult(app.TV_DOWNLOAD_DIR).unrar(root, rar_files, False)
            elif rar_files and not app.UNPACK:
                logger.warning(u'Unpack is disabled. Skipping: %s', rar_files)