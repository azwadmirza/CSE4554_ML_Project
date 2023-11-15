def as_dataframe(
    ds: tf.data.Dataset,
    ds_info: Optional[dataset_info.DatasetInfo] = None,
) -> StyledDataFrame:
  """Convert the dataset into a pandas dataframe.

  Warning: The dataframe will be loaded entirely in memory, you may
  want to call `tfds.as_dataframe` on a subset of the data instead:

  ```
  df = tfds.as_dataframe(ds.take(10), ds_info)
  ```

  Args:
    ds: `tf.data.Dataset`. The tf.data.Dataset object to convert to panda
      dataframe. Examples should not be batched. The full dataset will be
      loaded.
    ds_info: Dataset info object. If given, helps improving the formatting.
      Available either through `tfds.load('mnist', with_info=True)` or
      `tfds.builder('mnist').info`

  Returns:
    dataframe: The `pandas.DataFrame` object
  """
  # Raise a clean error message if panda isn't installed.
  lazy_imports_lib.lazy_imports.pandas  # pylint: disable=pointless-statement

  # Pack `as_supervised=True` datasets
  if ds_info:
    ds = dataset_info.pack_as_supervised_ds(ds, ds_info)

  # Flatten the keys names, specs,... while keeping the feature key definition
  # order
  columns = _make_columns(ds.element_spec, ds_info=ds_info)
  rows = [_make_row_dict(ex, columns) for ex in dataset_utils.as_numpy(ds)]
  df = StyledDataFrame(rows)
  df.current_style.format({c.name: c.format_fn for c in columns if c.format_fn})
  return df