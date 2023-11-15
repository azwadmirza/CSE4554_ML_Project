def export(journal, format, output=None):
    """Exports the journal to various formats.
    format should be one of json, txt, text, md, markdown.
    If output is None, returns a unicode representation of the output.
    If output is a directory, exports entries into individual files.
    Otherwise, exports to the given output file.
    """
    maps = {
        "json": to_json,
        "txt": to_txt,
        "text": to_txt,
        "md": to_md,
        "markdown": to_md
    }
    if output and os.path.isdir(output): # multiple files
        return write_files(journal, output, format)
    else:
        content = maps[format](journal)
        if output:
            try:
                with codecs.open(output, "w", "utf-8") as f:
                    f.write(content)
                return "[Journal exported to {0}]".format(output)
            except IOError as e:
                return "[ERROR: {0} {1}]".format(e.filename, e.strerror)
        else:
            return content