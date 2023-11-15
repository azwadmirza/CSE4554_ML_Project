def is_active(input_element):
    """Check if we can interact with the given element."""
    try:
        return is_displayed(input_element) and input_element.is_enabled()
    except WebDriverException:
        return False