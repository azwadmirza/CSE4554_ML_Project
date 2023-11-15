def show(dataset, **kwargs):
    """Display the dataset as an image.
    """
    if not dataset.is_loaded():
        raise ValueError("Dataset not loaded, cannot display.")

    img = get_enhanced_image(dataset, **kwargs)
    img.show()