    def apply(self, url, elements, evaluation):
        'FetchURL[url_String, elements_]'

        import tempfile
        import os

        py_url = url.get_string_value()

        temp_handle, temp_path = tempfile.mkstemp(suffix='')
        try:
            f = urllib2.urlopen(py_url)
            try:
                if sys.version_info >= (3, 0):
                    content_type = f.info().get_content_type()
                else:
                    content_type = f.headers['content-type']

                os.write(temp_handle, f.read())
            finally:
                f.close()

            def determine_filetype():
                return mimetype_dict.get(content_type)

            result = Import._import(temp_path, determine_filetype, elements, evaluation)
        except HTTPError as e:
            evaluation.message(
                'FetchURL', 'httperr', url,
                'the server returned an HTTP status code of %s (%s)' % (e.code, str(e.reason)))
            return Symbol('$Failed')
        except URLError as e:  # see https://docs.python.org/3/howto/urllib2.html
            if hasattr(e, 'reason'):
                evaluation.message('FetchURL', 'httperr', url, str(e.reason))
            elif hasattr(e, 'code'):
                evaluation.message('FetchURL', 'httperr', url, 'server returned %s' % e.code)
            return Symbol('$Failed')
        except ValueError as e:
            evaluation.message('FetchURL', 'httperr', url, str(e))
            return Symbol('$Failed')
        finally:
            os.unlink(temp_path)

        return result