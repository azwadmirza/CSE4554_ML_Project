def _build_splits(devkit):
  """Splits the train data into train/val/test by video.

  Ensures that images from the same video do not traverse the splits.

  Args:
    devkit: object that iterates over the devkit archive.

  Returns:
    train_images: File ids for the training set images.
    validation_images: File ids for the validation set images.
    test_images: File ids for the test set images.
  """
  mapping_line_ids = None
  mapping_lines = None
  for fpath, fobj in devkit:
    if fpath == os.path.join("mapping", "train_rand.txt"):
      # Converts 1-based line index to 0-based line index.
      mapping_line_ids = [
          int(x.strip()) - 1 for x in fobj.read().decode("utf-8").split(",")
      ]
    elif fpath == os.path.join("mapping", "train_mapping.txt"):
      mapping_lines = fobj.read().splitlines()
      mapping_lines = [x.decode("utf-8") for x in mapping_lines]

  assert mapping_line_ids
  assert mapping_lines

  video_to_image = collections.defaultdict(list)
  for image_id, mapping_lineid in enumerate(mapping_line_ids):
    line = mapping_lines[mapping_lineid]
    video_id = line.split(" ")[1]
    video_to_image[video_id].append(image_id)

  # Sets numpy random state.
  numpy_original_state = np.random.get_state()
  np.random.seed(seed=123)

  # Max 1 for testing.
  num_test_videos = max(1,
                        _TEST_SPLIT_PERCENT_VIDEOS * len(video_to_image) // 100)
  num_validation_videos = max(
      1,
      _VALIDATION_SPLIT_PERCENT_VIDEOS * len(video_to_image) // 100)
  test_videos = set(
      np.random.choice(
          sorted(list(video_to_image.keys())), num_test_videos, replace=False))
  validation_videos = set(
      np.random.choice(
          sorted(list(set(video_to_image.keys()) - set(test_videos))),
          num_validation_videos,
          replace=False))
  test_images = []
  validation_images = []
  train_images = []
  for k, v in video_to_image.items():
    if k in test_videos:
      test_images.extend(v)
    elif k in validation_videos:
      validation_images.extend(v)
    else:
      train_images.extend(v)

  # Resets numpy random state.
  np.random.set_state(numpy_original_state)
  return train_images, validation_images, test_images