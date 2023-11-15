def _parse_frde_bitext(fr_path, de_path):
  with tf.io.gfile.GFile(fr_path) as f:
    fr_sentences = f.read().splitlines()
  with tf.io.gfile.GFile(de_path) as f:
    de_sentences = f.read().splitlines()
  assert len(fr_sentences) == len(de_sentences), (
      "Sizes do not match: %d vs %d for %s vs %s." % (
          len(fr_sentences), len(de_sentences), fr_path, de_path))
  for line_id, (s1, s2) in enumerate(zip(fr_sentences, de_sentences)):
    yield line_id, {
        "fr": s1,
        "de": s2
    }