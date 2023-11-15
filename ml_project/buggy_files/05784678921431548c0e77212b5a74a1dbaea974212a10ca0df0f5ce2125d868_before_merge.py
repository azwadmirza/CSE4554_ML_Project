def array_repeat(a, repeats):
    def array_repeat_impl(a, repeat):
        return np.repeat(a, repeat)

    return array_repeat_impl