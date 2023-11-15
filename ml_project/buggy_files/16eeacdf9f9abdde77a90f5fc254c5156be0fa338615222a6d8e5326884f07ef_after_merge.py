def _sample_image(image, sampled_diag):
    # NOTE: Modifies `image` in-place
    unique, counts = np.unique(sampled_diag, axis=0, return_counts=True)
    unique = tuple(tuple(row) for row in unique.astype(np.int).T)
    image[unique] = counts