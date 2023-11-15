    def pil_rotater(pic, angle, resample, expand):
        return np.array(
            Image.fromarray(pic).rotate(angle, expand=expand, resample=resample)
        )