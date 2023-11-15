def load_elements_generator(elements, factory, modeling_language, gaphor_version):
    """Load a file and create a model if possible.

    Exceptions: IOError, ValueError.
    """
    log.debug(f"Loading {len(elements)} elements")

    # The elements are iterated three times:
    size = len(elements) * 3

    def update_status_queue(_n=[0]):
        n = _n[0] = _n[0] + 1
        if n % 30 == 0:
            yield (n * 100) / size

    # First create elements and canvas items in the factory
    # The elements are stored as attribute 'element' on the parser objects:
    yield from _load_elements_and_canvasitems(
        elements, factory, modeling_language, gaphor_version, update_status_queue
    )
    yield from _load_attributes_and_references(elements, update_status_queue)

    for id, elem in list(elements.items()):
        yield from update_status_queue()
        elem.element.postload()