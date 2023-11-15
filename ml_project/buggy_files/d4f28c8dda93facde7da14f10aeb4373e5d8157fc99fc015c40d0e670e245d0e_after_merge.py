  def _generate_examples(self, images, annotations, subdir, image_ids):
    """Yields images and annotations.

    Args:
      images: object that iterates over the archive of images.
      annotations: object that iterates over the archive of annotations.
      subdir: subdirectory from which to extract images and annotations, e.g.
        training or testing.
      image_ids: file ids for images in this split.

    Yields:
      A tuple containing the example's key, and the example.
    """
    cv2 = tfds.core.lazy_imports.cv2

    all_annotations = dict()
    for fpath, fobj in annotations:
      prefix, ext = os.path.splitext(fpath)
      if ext != ".txt":
        continue
      if prefix.split(os.path.sep)[0] != subdir:
        continue

      # Key is the datapoint id. E.g. training/label_2/label_000016 -> 16.
      all_annotations[int(prefix[-6:])] = _parse_kitti_annotations(fobj)

    for fpath, fobj in images:
      prefix, ext = os.path.splitext(fpath)
      if ext != ".png":
        continue
      if prefix.split(os.path.sep)[0] != subdir:
        continue
      image_id = int(prefix[-6:])
      if image_id not in image_ids:
        continue
      annotations = all_annotations[image_id]
      img = cv2.imdecode(np.fromstring(fobj.read(), dtype=np.uint8),
                         cv2.IMREAD_COLOR)
      img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
      height, width, _ = img.shape
      for obj in annotations:
        obj["bbox"] = _build_bounding_box(obj["bbox_raw"], height, width)
        del obj["bbox_raw"]
      _, fname = os.path.split(fpath)
      record = {"image": img, "image/file_name": fname, "objects": annotations}
      yield fname, record