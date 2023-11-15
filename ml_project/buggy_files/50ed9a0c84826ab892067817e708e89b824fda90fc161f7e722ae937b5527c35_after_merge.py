def get_metadata(book):
    download_urls = []
    for book_data in book.data:
        if book_data.format not in KOBO_FORMATS:
            continue
        for kobo_format in KOBO_FORMATS[book_data.format]:
            # log.debug('Id: %s, Format: %s' % (book.id, kobo_format))
            download_urls.append(
                {
                    "Format": kobo_format,
                    "Size": book_data.uncompressed_size,
                    "Url": get_download_url_for_book(book, book_data.format),
                    # The Kobo forma accepts platforms: (Generic, Android)
                    "Platform": "Generic",
                    # "DrmType": "None", # Not required
                }
            )

    book_uuid = book.uuid
    metadata = {
        "Categories": ["00000000-0000-0000-0000-000000000001",],
        "Contributors": get_author(book),
        "CoverImageId": book_uuid,
        "CrossRevisionId": book_uuid,
        "CurrentDisplayPrice": {"CurrencyCode": "USD", "TotalAmount": 0},
        "CurrentLoveDisplayPrice": {"TotalAmount": 0},
        "Description": get_description(book),
        "DownloadUrls": download_urls,
        "EntitlementId": book_uuid,
        "ExternalIds": [],
        "Genre": "00000000-0000-0000-0000-000000000001",
        "IsEligibleForKoboLove": False,
        "IsInternetArchive": False,
        "IsPreOrder": False,
        "IsSocialEnabled": True,
        "Language": "en",
        "PhoneticPronunciations": {},
        # TODO: Fix book.pubdate to return a datetime object so that we can easily
        # convert it to the format Kobo devices expect.
        "PublicationDate": book.pubdate,
        "Publisher": {"Imprint": "", "Name": get_publisher(book),},
        "RevisionId": book_uuid,
        "Title": book.title,
        "WorkId": book_uuid,
    }

    if get_series(book):
        if sys.version_info < (3, 0):
            name = get_series(book).encode("utf-8")
        else:
            name = get_series(book)
        metadata["Series"] = {
            "Name": get_series(book),
            "Number": get_seriesindex(book),        # ToDo Check int() ?
            "NumberFloat": float(get_seriesindex(book)),
            # Get a deterministic id based on the series name.
            "Id": uuid.uuid3(uuid.NAMESPACE_DNS, name),
        }

    return metadata