def perform_svtextin_node_object(node, node_ref):
    '''
    as it's a beta service, old IO json may not be compatible - in this interest
    of neat code we assume it finds everything.
    '''
    texts = bpy.data.texts
    params = node_ref.get('params')

    # original textin used 'current_text', textin+ uses 'text'
    current_text = params.get('current_text', params.get('text'))

    # it's not clear from the exporter code why textmode parameter isn't stored
    # in params.. for now this lets us look in both places. ugly but whatever.
    textmode = params.get('textmode')
    if not textmode:
        textmode = node_ref.get('textmode')
    node.textmode = textmode

    if not current_text:
        info("`%s' doesn't store a current_text in params", node.name)

    elif not current_text in texts:
        new_text = texts.new(current_text)
        text_line_entry = node_ref['text_lines']

        if node.textmode == 'JSON':
            if isinstance(text_line_entry, str):
                debug('loading old text json content / backward compatibility mode')

            elif isinstance(text_line_entry, dict):
                text_line_entry = json.dumps(text_line_entry['stored_as_json'])

        new_text.from_string(text_line_entry)

    else:
        # reaches here if  (current_text) and (current_text in texts)
        # can probably skip this..
        # texts[current_text].from_string(node_ref['text_lines'])
        debug('%s seems to reuse a text block loaded by another node - skipping', node.name)