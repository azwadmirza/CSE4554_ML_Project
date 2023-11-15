                def map_f(values, f):
                    return lib.map_infer_mask(values, f,
                                              isnull(values).view(np.uint8))