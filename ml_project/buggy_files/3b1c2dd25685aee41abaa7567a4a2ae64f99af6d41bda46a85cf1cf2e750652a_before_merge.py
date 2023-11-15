def smart_open(uri, mode="rb", **kw):
    """
    Open the given S3 / HDFS / filesystem file pointed to by `uri` for reading or writing.

    The only supported modes for now are 'rb' (read, default) and 'wb' (replace & write).

    The reads/writes are memory efficient (streamed) and therefore suitable for
    arbitrarily large files.

    The `uri` can be either:

    1. a URI for the local filesystem (compressed ``.gz`` or ``.bz2`` files handled automatically):
       `./lines.txt`, `/home/joe/lines.txt.gz`, `file:///home/joe/lines.txt.bz2`
    2. a URI for HDFS: `hdfs:///some/path/lines.txt`
    3. a URI for Amazon's S3 (can also supply credentials inside the URI):
       `s3://my_bucket/lines.txt`, `s3://my_aws_key_id:key_secret@my_bucket/lines.txt`
    4. an instance of the boto.s3.key.Key class.

    Examples::

      >>> # stream lines from http; you can use context managers too:
      >>> with smart_open.smart_open('http://www.google.com') as fin:
      ...     for line in fin:
      ...         print line

      >>> # stream lines from S3; you can use context managers too:
      >>> with smart_open.smart_open('s3://mybucket/mykey.txt') as fin:
      ...     for line in fin:
      ...         print line

      >>> # you can also use a boto.s3.key.Key instance directly:
      >>> key = boto.connect_s3().get_bucket("my_bucket").get_key("my_key")
      >>> with smart_open.smart_open(key) as fin:
      ...     for line in fin:
      ...         print line

      >>> # stream line-by-line from an HDFS file
      >>> for line in smart_open.smart_open('hdfs:///user/hadoop/my_file.txt'):
      ...    print line

      >>> # stream content *into* S3:
      >>> with smart_open.smart_open('s3://mybucket/mykey.txt', 'wb') as fout:
      ...     for line in ['first line', 'second line', 'third line']:
      ...          fout.write(line + '\n')

      >>> # stream from/to (compressed) local files:
      >>> for line in smart_open.smart_open('/home/radim/my_file.txt'):
      ...    print line
      >>> for line in smart_open.smart_open('/home/radim/my_file.txt.gz'):
      ...    print line
      >>> with smart_open.smart_open('/home/radim/my_file.txt.gz', 'wb') as fout:
      ...    fout.write("hello world!\n")
      >>> with smart_open.smart_open('/home/radim/another.txt.bz2', 'wb') as fout:
      ...    fout.write("good bye!\n")
      >>> # stream from/to (compressed) local files with Expand ~ and ~user constructions:
      >>> for line in smart_open.smart_open('~/my_file.txt'):
      ...    print line
      >>> for line in smart_open.smart_open('my_file.txt'):
      ...    print line

    """
    logger.debug('%r', locals())

    #
    # This is a work-around for the problem described in Issue #144.
    # If the user has explicitly specified an encoding, then assume they want
    # us to open the destination in text mode, instead of the default binary.
    #
    # If we change the default mode to be text, and match the normal behavior
    # of Py2 and 3, then the above assumption will be unnecessary.
    #
    if kw.get('encoding') is not None and 'b' in mode:
        mode = mode.replace('b', '')

    # validate mode parameter
    if not isinstance(mode, six.string_types):
        raise TypeError('mode should be a string')

    if isinstance(uri, six.string_types):
        # this method just routes the request to classes handling the specific storage
        # schemes, depending on the URI protocol in `uri`
        parsed_uri = ParseUri(uri)

        if parsed_uri.scheme in ("file", ):
            # local files -- both read & write supported
            # compression, if any, is determined by the filename extension (.gz, .bz2)
            return file_smart_open(parsed_uri.uri_path, mode, encoding=kw.pop('encoding', None))
        elif parsed_uri.scheme in ("s3", "s3n", 's3u'):
            return s3_open_uri(parsed_uri, mode, **kw)
        elif parsed_uri.scheme in ("hdfs", ):
            encoding = kw.pop('encoding', None)
            if encoding is not None:
                warnings.warn(_ISSUE_146_FSTR % {'encoding': encoding, 'scheme': parsed_uri.scheme})
            if mode in ('r', 'rb'):
                return HdfsOpenRead(parsed_uri, **kw)
            if mode in ('w', 'wb'):
                return HdfsOpenWrite(parsed_uri, **kw)
            else:
                raise NotImplementedError("file mode %s not supported for %r scheme", mode, parsed_uri.scheme)
        elif parsed_uri.scheme in ("webhdfs", ):
            encoding = kw.pop('encoding', None)
            if encoding is not None:
                warnings.warn(_ISSUE_146_FSTR % {'encoding': encoding, 'scheme': parsed_uri.scheme})
            if mode in ('r', 'rb'):
                return WebHdfsOpenRead(parsed_uri, **kw)
            elif mode in ('w', 'wb'):
                return WebHdfsOpenWrite(parsed_uri, **kw)
            else:
                raise NotImplementedError("file mode %s not supported for %r scheme", mode, parsed_uri.scheme)
        elif parsed_uri.scheme.startswith('http'):
            encoding = kw.pop('encoding', None)
            if encoding is not None:
                warnings.warn(_ISSUE_146_FSTR % {'encoding': encoding, 'scheme': parsed_uri.scheme})
            if mode in ('r', 'rb'):
                return HttpOpenRead(parsed_uri, **kw)
            else:
                raise NotImplementedError("file mode %s not supported for %r scheme", mode, parsed_uri.scheme)
        else:
            raise NotImplementedError("scheme %r is not supported", parsed_uri.scheme)
    elif isinstance(uri, boto.s3.key.Key):
        return s3_open_key(uri, mode, **kw)
    elif hasattr(uri, 'read'):
        # simply pass-through if already a file-like
        return uri
    else:
        raise TypeError('don\'t know how to handle uri %s' % repr(uri))