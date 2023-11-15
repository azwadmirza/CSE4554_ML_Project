def atleast_2d(*arys):
  if len(arys) == 1:
    arr = array(arys[0])
    return arr if arr.ndim >= 2 else arr.reshape((1, -1))
  else:
    return [atleast_2d(arr) for arr in arys]