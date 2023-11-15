    def __init__(
        self,
        name,
        value,
        storage="STANDARD",
        etag=None,
        is_versioned=False,
        version_id=0,
        max_buffer_size=DEFAULT_KEY_BUFFER_SIZE,
        multipart=None,
    ):
        self.name = name
        self.last_modified = datetime.datetime.utcnow()
        self.acl = get_canned_acl("private")
        self.website_redirect_location = None
        self._storage_class = storage if storage else "STANDARD"
        self._metadata = {}
        self._expiry = None
        self._etag = etag
        self._version_id = version_id
        self._is_versioned = is_versioned
        self._tagging = FakeTagging()
        self.multipart = multipart

        self._value_buffer = tempfile.SpooledTemporaryFile(max_size=max_buffer_size)
        self._max_buffer_size = max_buffer_size
        self.value = value