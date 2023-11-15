def show(dataset, **kwargs):
    """Display the dataset as an image.
    """
    img = get_enhanced_image(dataset.squeeze(), **kwargs)
    img.show()
    return img