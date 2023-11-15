def line_splitter(buffer, separator=u'\n'):
    index = buffer.find(six.text_type(separator))
    if index == -1:
        return None, None
    return buffer[:index + 1], buffer[index + 1:]