    def pil_rotater(pic, angle, resample, expand):
        # Ensures that pic is of the correct type
        return np.array(
            Image.fromarray(np.array(pic).astype(np.uint8)).rotate(
                angle, expand=expand, resample=resample
            )
        )