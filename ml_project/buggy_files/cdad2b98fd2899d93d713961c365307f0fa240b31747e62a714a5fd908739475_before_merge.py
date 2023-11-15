def do_zip_mods():
    """Build the zipmods.zip file."""
    zf = zipfile.ZipFile("tests/zipmods.zip", "w")

    # Take one file from disk.
    zf.write("tests/covmodzip1.py", "covmodzip1.py")

    # The others will be various encodings.
    source = textwrap.dedent(u"""\
        # coding: {encoding}
        text = u"{text}"
        ords = {ords}
        assert [ord(c) for c in text] == ords
        print(u"All OK with {encoding}")
        """)
    # These encodings should match the list in tests/test_python.py
    details = [
        (u'utf8', u'ⓗⓔⓛⓛⓞ, ⓦⓞⓡⓛⓓ'),
        (u'gb2312', u'你好，世界'),
        (u'hebrew', u'שלום, עולם'),
        (u'shift_jis', u'こんにちは世界'),
        (u'cp1252', u'“hi”'),
    ]
    for encoding, text in details:
        filename = 'encoded_{}.py'.format(encoding)
        ords = [ord(c) for c in text]
        source_text = source.format(encoding=encoding, text=text, ords=ords)
        zf.writestr(filename, source_text.encode(encoding))

    zf.close()