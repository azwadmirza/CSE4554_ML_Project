def persistence_image_amplitudes(diagrams, sampling, step_size,
                                 weight_function=lambda x: x, sigma=1., p=2.,
                                 **kwargs):
    persistence_image = persistence_images(diagrams, sampling, step_size,
                                           weight_function, sigma)
    return np.linalg.norm(persistence_image, axis=(1, 2), ord=p)