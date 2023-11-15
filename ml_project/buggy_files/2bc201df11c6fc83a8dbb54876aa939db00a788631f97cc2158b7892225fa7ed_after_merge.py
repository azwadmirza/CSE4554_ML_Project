    def linspace(start, stop, num):
        arr = np.empty(num, dtype)
        if num == 0:
            return arr
        div = num - 1
        delta = stop - start
        arr[0] = start
        for i in range(1, num):
            arr[i] = start + delta * (i / div)
        return arr