def check_read_formats(entry):
    EXTENSIONS_READER = {'TXT', 'PDF', 'EPUB', 'CBZ', 'CBT', 'CBR'}
    bookformats = list()
    if len(entry.data):
        for ele in iter(entry.data):
            if ele.format in EXTENSIONS_READER:
                bookformats.append(ele.format.lower())
    return bookformats