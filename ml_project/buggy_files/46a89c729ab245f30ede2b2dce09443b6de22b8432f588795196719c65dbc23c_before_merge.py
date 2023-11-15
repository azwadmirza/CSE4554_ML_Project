  def _split_generators(self, dl_manager):
    iris_file = dl_manager.download(IRIS_URL)
    all_lines = tf.io.gfile.GFile(iris_file).read().split("\n")
    records = [l for l in all_lines if l]  # get rid of empty lines

    # Specify the splits
    return [
        tfds.core.SplitGenerator(
            name=tfds.Split.TRAIN,
            gen_kwargs={"records": records}),
    ]