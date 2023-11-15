  def encode_example(self, audio_or_path_or_fobj):
    if isinstance(audio_or_path_or_fobj, (np.ndarray, list)):
      return audio_or_path_or_fobj
    elif isinstance(audio_or_path_or_fobj, six.string_types):
      filename = audio_or_path_or_fobj
      file_format = self._file_format or filename.split('.')[-1]
      with tf.io.gfile.GFile(filename, 'rb') as audio_f:
        try:
          return self._encode_file(audio_f, file_format)
        except Exception as e:  # pylint: disable=broad-except
          utils.reraise(e, prefix=f'Error for {filename}: ')
    else:
      return self._encode_file(audio_or_path_or_fobj, self._file_format)