  def _parse_text(path):
    """Returns the sentences from a single text file, which may be gzipped."""
    split_path = path.split(".")

    if split_path[-1] == "gz":
      lang = split_path[-2]
      with tf.io.gfile.GFile(path, "rb") as f, gzip.GzipFile(fileobj=f) as g:
        return g.read().decode("utf-8").split("\n"), lang

    if split_path[-1] == "txt":
      # CWMT
      lang = split_path[-2].split("_")[-1]
      lang = "zh" if lang in ("ch", "cn") else lang
    else:
      lang = split_path[-1]
    with tf.io.gfile.GFile(path) as f:
      return f.read().split("\n"), lang