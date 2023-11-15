    def _verify_download(self, file_name):
        try:
            bencodepy.decode_from_file(file_name)
        except bencodepy.DecodingError as e:
            logger.debug('Failed to validate torrent file: {0}'.format(str(e)))
            logger.debug('Result is not a valid torrent file')
            return False
        return True