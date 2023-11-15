    def run(self, info):
        metadata = {}
        if info.get('title') is not None:
            metadata['title'] = info['title']
        if info.get('upload_date') is not None:
            metadata['date'] = info['upload_date']
        if info.get('artist') is not None:
            metadata['artist'] = info['artist']
        elif info.get('uploader') is not None:
            metadata['artist'] = info['uploader']
        elif info.get('uploader_id') is not None:
            metadata['artist'] = info['uploader_id']
        if info.get('description') is not None:
            metadata['description'] = info['description']
            metadata['comment'] = info['description']
        if info.get('webpage_url') is not None:
            metadata['purl'] = info['webpage_url']
        if info.get('album') is not None:
            metadata['album'] = info['album']

        if not metadata:
            self._downloader.to_screen('[ffmpeg] There isn\'t any metadata to add')
            return [], info

        filename = info['filepath']
        temp_filename = prepend_extension(filename, 'temp')

        if info['ext'] == 'm4a':
            options = ['-vn', '-acodec', 'copy']
        else:
            options = ['-c', 'copy']

        for (name, value) in metadata.items():
            options.extend(['-metadata', '%s=%s' % (name, value)])

        # https://github.com/rg3/youtube-dl/issues/8350
        if info['protocol'] == 'm3u8_native':
            options.extend(['-bsf:a', 'aac_adtstoasc'])

        self._downloader.to_screen('[ffmpeg] Adding metadata to \'%s\'' % filename)
        self.run_ffmpeg(filename, temp_filename, options)
        os.remove(encodeFilename(filename))
        os.rename(encodeFilename(temp_filename), encodeFilename(filename))
        return [], info