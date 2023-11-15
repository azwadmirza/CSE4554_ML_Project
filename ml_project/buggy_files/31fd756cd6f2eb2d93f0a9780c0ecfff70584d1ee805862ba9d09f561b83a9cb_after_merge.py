def convert_text_snippet(snippet_info):
    text = snippet_info['text']
    text_builder = []
    prev_pos = 0
    next_pos = None
    total_placeholders = len(snippet_info['placeholders']) + 1
    for i, placeholder in enumerate(snippet_info['placeholders']):
        placeholder_begin = placeholder['begin']
        placeholder_end = placeholder['end']
        next_pos = placeholder_begin
        standard_text = text[prev_pos:next_pos]
        snippet_text = text[next_pos:placeholder_end][1:-1]
        prev_pos = placeholder['end']
        text_builder.append(standard_text)
        placeholder_number = (i + 1) % total_placeholders
        snippet = '${%d:%s}' % (placeholder_number, snippet_text)
        text_builder.append(snippet)
    text_builder.append(text[prev_pos:])
    text_builder.append('$0')
    return ''.join(text_builder)