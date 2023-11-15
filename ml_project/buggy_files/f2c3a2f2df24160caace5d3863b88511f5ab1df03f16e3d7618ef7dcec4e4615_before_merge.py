  def abstractify(x):
    return ShapedArray(np.shape(x), dtypes.result_type(x))