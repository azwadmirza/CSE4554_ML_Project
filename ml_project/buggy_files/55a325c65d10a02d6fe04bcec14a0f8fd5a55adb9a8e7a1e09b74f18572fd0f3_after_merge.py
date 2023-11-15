def atleast_1d(*arys):
  if len(arys) == 1:
    arr = array(arys[0])
    return arr if ndim(arr) >= 1 else reshape(arr, -1)
  else:
    return [atleast_1d(arr) for arr in arys]