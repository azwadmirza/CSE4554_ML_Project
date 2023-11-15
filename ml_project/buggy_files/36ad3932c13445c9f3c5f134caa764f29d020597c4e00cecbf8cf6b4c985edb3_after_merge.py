def show_examples(
    ds: tf.data.Dataset,
    ds_info: dataset_info.DatasetInfo,
    **options_kwargs: Any
):
  """Visualize images (and labels) from an image classification dataset.

  This function is for interactive use (Colab, Jupyter). It displays and return
  a plot of (rows*columns) images from a tf.data.Dataset.

  Usage:
  ```python
  ds, ds_info = tfds.load('cifar10', split='train', with_info=True)
  fig = tfds.show_examples(ds, ds_info)
  ```

  Args:
    ds: `tf.data.Dataset`. The tf.data.Dataset object to visualize. Examples
      should not be batched. Examples will be consumed in order until
      (rows * cols) are read or the dataset is consumed.
    ds_info: The dataset info object to which extract the label and features
      info. Available either through `tfds.load('mnist', with_info=True)` or
      `tfds.builder('mnist').info`
    **options_kwargs: Additional display options, specific to the dataset type
      to visualize. Are forwarded to `tfds.visualization.Visualizer.show`.
      See the `tfds.visualization` for a list of available visualizers.

  Returns:
    fig: The `matplotlib.Figure` object
  """
  if not isinstance(ds_info, dataset_info.DatasetInfo):  # Arguments inverted
    # `absl.logging` does not appear on Colab by default, so uses print instead.
    print('WARNING: For consistency with `tfds.load`, the `tfds.show_examples` '
          'signature has been modified from (info, ds) to (ds, info).\n'
          'The old signature is deprecated and will be removed. '
          'Please change your call to `tfds.show_examples(ds, info)`')
    ds, ds_info = ds_info, ds

  # Pack `as_supervised=True` datasets
  ds = dataset_info.pack_as_supervised_ds(ds, ds_info)

  for visualizer in _ALL_VISUALIZERS:
    if visualizer.match(ds_info):
      return visualizer.show(ds, ds_info, **options_kwargs)
    raise ValueError(
        'Visualisation not supported for dataset `{}`'.format(ds_info.name)
    )