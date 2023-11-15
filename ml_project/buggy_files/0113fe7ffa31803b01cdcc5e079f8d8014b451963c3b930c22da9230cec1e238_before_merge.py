def transform(data, func):
    if compat.USE_PYGEOS:
        coords = pygeos.get_coordinates(data)
        new_coords = func(coords[:, 0], coords[:, 1])
        result = pygeos.set_coordinates(data.copy(), np.array(new_coords).T)
        return result
    else:
        from shapely.ops import transform

        n = len(data)
        result = np.empty(n, dtype=object)
        for i in range(n):
            geom = data[i]
            result[i] = transform(func, geom)

        return result