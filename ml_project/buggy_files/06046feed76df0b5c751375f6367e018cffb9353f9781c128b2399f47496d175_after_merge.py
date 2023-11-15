def _sample_image(image, diagram_pixel_coords):
    # WARNING: Modifies `image` in-place
    unique, counts = \
        np.unique(diagram_pixel_coords, axis=0, return_counts=True)
    unique = tuple(tuple(row) for row in unique.astype(np.int).T)
    image[unique] = counts