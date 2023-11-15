def atleast_3d(*arys):
  if len(arys) == 1:
    arr = array(arys[0])
    if ndim(arr) <= 1:
      arr = reshape(arr, (1, -1, 1))
    elif ndim(arr) == 2:
      arr = reshape(arr, shape(arr) + (1,))
    return arr
  else:
    return [atleast_3d(arr) for arr in arys]