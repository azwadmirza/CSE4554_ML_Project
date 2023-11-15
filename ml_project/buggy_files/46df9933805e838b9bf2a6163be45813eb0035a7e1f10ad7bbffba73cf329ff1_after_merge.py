def main():
    pip_version = StrictVersion(check_output(['pip', '--version'])
                                .decode('utf-8').split()[1])
    has_pip_cache = pip_version >= StrictVersion('6.0')
    index_base = get_index_base()
    temp = mkdtemp(prefix='pipstrap-')
    try:
        downloads = [hashed_download(index_base + '/packages/' + path,
                                     temp,
                                     digest)
                     for path, digest in PACKAGES]
        check_output('pip install --no-index --no-deps -U ' +
                     # Disable cache since we're not using it and it otherwise
                     # sometimes throws permission warnings:
                     ('--no-cache-dir ' if has_pip_cache else '') +
                     ' '.join(quote(d) for d in downloads),
                     shell=True)
    except HashError as exc:
        print(exc)
    except Exception:
        rmtree(temp)
        raise
    else:
        rmtree(temp)
        return 0
    return 1