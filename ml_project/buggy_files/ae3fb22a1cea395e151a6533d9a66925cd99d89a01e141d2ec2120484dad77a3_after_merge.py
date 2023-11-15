def _parse_parallel_sentences(f1, f2):
  """Returns examples from parallel SGML or text files, which may be gzipped."""
  def _parse_text(path):
    """Returns the sentences from a single text file, which may be gzipped."""
    split_path = path.split(".")

    if split_path[-1] == "gz":
      lang = split_path[-2]
      with tf.io.gfile.GFile(path, "rb") as f, gzip.GzipFile(fileobj=f) as g:
        return g.read().decode("utf-8").splitlines(), lang

    if split_path[-1] == "txt":
      # CWMT
      lang = split_path[-2].split("_")[-1]
      lang = "zh" if lang in ("ch", "cn") else lang
    else:
      lang = split_path[-1]
    with tf.io.gfile.GFile(path) as f:
      return f.read().splitlines(), lang

  def _parse_sgm(path):
    """Returns sentences from a single SGML file."""
    lang = path.split(".")[-2]
    sentences = []
    # Note: We can't use the XML parser since some of the files are badly
    # formatted.
    seg_re = re.compile(r"<seg id=\"\d+\">(.*)</seg>")
    with tf.io.gfile.GFile(path) as f:
      for line in f:
        seg_match = re.match(seg_re, line)
        if seg_match:
          assert len(seg_match.groups()) == 1
          sentences.append(seg_match.groups()[0])
    return sentences, lang

  parse_file = _parse_sgm if f1.endswith(".sgm") else _parse_text

  # Some datasets (e.g., CWMT) contain multiple parallel files specified with
  # a wildcard. We sort both sets to align them and parse them one by one.
  f1_files = tf.io.gfile.glob(f1)
  f2_files = tf.io.gfile.glob(f2)

  assert f1_files and f2_files, "No matching files found: %s, %s." % (f1, f2)
  assert len(f1_files) == len(f2_files), (
      "Number of files do not match: %d vs %d for %s vs %s." % (
          len(f1_files), len(f2_files), f1, f2))

  for f_id, (f1_i, f2_i) in enumerate(zip(sorted(f1_files), sorted(f2_files))):
    l1_sentences, l1 = parse_file(f1_i)
    l2_sentences, l2 = parse_file(f2_i)

    assert len(l1_sentences) == len(l2_sentences), (
        "Sizes do not match: %d vs %d for %s vs %s." % (
            len(l1_sentences), len(l2_sentences), f1_i, f2_i))

    for line_id, (s1, s2) in enumerate(zip(l1_sentences, l2_sentences)):
      key = "{}/{}".format(f_id, line_id)
      yield key, {
          l1: s1,
          l2: s2
      }