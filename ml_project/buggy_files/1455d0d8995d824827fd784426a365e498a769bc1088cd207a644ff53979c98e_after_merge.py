    def _get_torrent_hash(result):
        """
        Gets the torrent hash from either the magnet or torrent file content
        params: :result: an instance of the searchResult class
        """
        if result.url.startswith('magnet'):
            result.hash = re.findall(r'urn:btih:([\w]{32,40})', result.url)[0]
            if len(result.hash) == 32:
                result.hash = b16encode(b32decode(result.hash)).lower()
        else:
            if not result.content:
                logger.exception('Torrent without content')
                raise Exception('Torrent without content')

            try:
                torrent_bdecode: Union[Iterable, Dict] = bencodepy.decode(result.content)
            except (bencodepy.BencodeDecodeError, Exception) as error:
                logger.exception('Unable to bdecode torrent')
                logger.info('Error is: {0}'.format(error))
                logger.info('Torrent bencoded data: {0!r}'.format(result.content))
                raise

            try:
                info = torrent_bdecode[b'info']
            except Exception:
                logger.exception('Unable to find info field in torrent')
                logger.info('Torrent bencoded data: {0!r}'.format(result.content))
                raise

            try:
                result.hash = sha1(bencodepy.encode(info)).hexdigest()
                logger.debug('Result Hash is {0}'.format(result.hash))
            except (bencodepy.Ben, Exception) as error:
                logger.exception('Unable to bencode torrent info')
                logger.info('Error is: {0}'.format(error))
                logger.info('Torrent bencoded data: {0!r}'.format(result.content))
                raise

        return result