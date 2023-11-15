def parse_get_bucket_location(parsed, http_response, **kwargs):
    # s3.GetBucketLocation cannot be modeled properly.  To
    # account for this we just manually parse the XML document.
    # The "parsed" passed in only has the ResponseMetadata
    # filled out.  This handler will fill in the LocationConstraint
    # value.
    if 'LocationConstraint' in parsed:
        # Response already set - a stub?
        return
    response_body = http_response.content
    parser = xml.etree.cElementTree.XMLParser(
        target=xml.etree.cElementTree.TreeBuilder(),
        encoding='utf-8')
    parser.feed(response_body)
    root = parser.close()
    region = root.text
    parsed['LocationConstraint'] = region