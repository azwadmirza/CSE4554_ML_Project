def atleast_2d(*arys):
  if len(arys) == 1:
    arr = array(arys[0])
    return arr if ndim(arr) >= 2 else reshape(arr, (1, -1))
  else:
    return [atleast_2d(arr) for arr in arys]