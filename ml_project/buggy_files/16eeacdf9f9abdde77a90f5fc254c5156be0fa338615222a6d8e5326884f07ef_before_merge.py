def _sample_image(image, sampled_diag):
    unique, counts = np.unique(sampled_diag, axis=0, return_counts=True)
    unique = tuple(tuple(row) for row in unique.astype(np.int).T)
    image[unique] = counts