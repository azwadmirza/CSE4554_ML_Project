        def append_url_to_file(target_url, tmp_filename, segment_name):
            target_filename = '%s-%s' % (tmp_filename, segment_name)
            count = 0
            while count <= fragment_retries:
                try:
                    success = ctx['dl'].download(target_filename, {'url': combine_url(base_url, target_url)})
                    if not success:
                        return False
                    down, target_sanitized = sanitize_open(target_filename, 'rb')
                    ctx['dest_stream'].write(down.read())
                    down.close()
                    segments_filenames.append(target_sanitized)
                    break
                except (compat_urllib_error.HTTPError, ) as err:
                    # YouTube may often return 404 HTTP error for a fragment causing the
                    # whole download to fail. However if the same fragment is immediately
                    # retried with the same request data this usually succeeds (1-2 attemps
                    # is usually enough) thus allowing to download the whole file successfully.
                    # So, we will retry all fragments that fail with 404 HTTP error for now.
                    if err.code != 404:
                        raise
                    # Retry fragment
                    count += 1
                    if count <= fragment_retries:
                        self.report_retry_fragment(segment_name, count, fragment_retries)
            if count > fragment_retries:
                self.report_error('giving up after %s fragment retries' % fragment_retries)
                return False