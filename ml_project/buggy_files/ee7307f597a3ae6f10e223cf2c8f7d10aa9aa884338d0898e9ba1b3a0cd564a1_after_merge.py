    def open_audio_file(self, item):
        """Open the file to read the PCM stream from the using
        ``item.path``.

        :return: the audiofile instance
        :rtype: :class:`audiotools.AudioFile`
        :raises :exc:`ReplayGainError`: if the file is not found or the
        file format is not supported
        """
        try:
            audiofile = self._mod_audiotools.open(py3_path(syspath(item.path)))
        except IOError:
            raise ReplayGainError(
                u"File {} was not found".format(item.path)
            )
        except self._mod_audiotools.UnsupportedFile:
            raise ReplayGainError(
                u"Unsupported file type {}".format(item.format)
            )

        return audiofile