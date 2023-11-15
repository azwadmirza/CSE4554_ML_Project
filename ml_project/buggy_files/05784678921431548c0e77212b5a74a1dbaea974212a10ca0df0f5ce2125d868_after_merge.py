def array_repeat(a, repeats):
    def array_repeat_impl(a, repeats):
        return np.repeat(a, repeats)

    return array_repeat_impl