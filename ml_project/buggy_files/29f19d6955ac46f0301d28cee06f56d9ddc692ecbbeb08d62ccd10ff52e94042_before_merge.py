def scrape_lyrics_from_html(html):
    """Scrape lyrics from a URL. If no lyrics can be found, return None
    instead.
    """
    from bs4 import SoupStrainer, BeautifulSoup

    if not html:
        return None

    def is_text_notcode(text):
        length = len(text)
        return (length > 20 and
                text.count(' ') > length / 25 and
                (text.find('{') == -1 or text.find(';') == -1))
    html = _scrape_strip_cruft(html)
    html = _scrape_merge_paragraphs(html)

    # extract all long text blocks that are not code
    try:
        soup = BeautifulSoup(html, "html.parser",
                             parse_only=SoupStrainer(text=is_text_notcode))
    except HTMLParseError:
        return None

    soup = sorted(soup.stripped_strings, key=len)[-1]

    return soup