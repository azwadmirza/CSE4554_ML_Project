    def _verify_download(self, file_name):
        try:
            bencodepy.bread(file_name)
        except bencodepy.BencodeDecodeError as e:
            logger.debug('Failed to validate torrent file: {0}'.format(str(e)))
            logger.debug('Result is not a valid torrent file')
            return False
        return True