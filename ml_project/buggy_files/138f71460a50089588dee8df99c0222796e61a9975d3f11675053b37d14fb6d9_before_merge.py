  def _split_generators(self, dl_manager):
    downloaded_dirs = dl_manager.download({
        "img_align_celeba": IMG_ALIGNED_DATA,
        "list_eval_partition": EVAL_LIST,
        "list_attr_celeba": ATTR_DATA,
        "landmarks_celeba": LANDMARKS_DATA,
    })

    # Load all images in memory (~1 GiB)
    # Use split to convert: `img_align_celeba/000005.jpg` -> `000005.jpg`
    all_images = {
        k.split("/")[-1]: img for k, img in
        dl_manager.iter_archive(downloaded_dirs["img_align_celeba"])
    }

    return [
        tfds.core.SplitGenerator(
            name=tfds.Split.TRAIN,
            gen_kwargs={
                "file_id": 0,
                "downloaded_dirs": downloaded_dirs,
                "downloaded_images": all_images,
            }),
        tfds.core.SplitGenerator(
            name=tfds.Split.VALIDATION,
            gen_kwargs={
                "file_id": 1,
                "downloaded_dirs": downloaded_dirs,
                "downloaded_images": all_images,
            }),
        tfds.core.SplitGenerator(
            name=tfds.Split.TEST,
            gen_kwargs={
                "file_id": 2,
                "downloaded_dirs": downloaded_dirs,
                "downloaded_images": all_images,
            })
    ]