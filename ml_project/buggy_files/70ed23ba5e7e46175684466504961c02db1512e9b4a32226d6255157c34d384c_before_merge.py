def get_image_bookmark(hide, start_page=1, end_page=0, tag='', sorting=None):
    """Get user's image bookmark"""
    total_list = list()
    i = start_page
    while True:
        if end_page != 0 and i > end_page:
            print("Page Limit reached: " + str(end_page))
            break

        url = 'https://www.pixiv.net/bookmark.php?p=' + str(i)
        if hide:
            url = url + "&rest=hide"
        # Implement #468 default is desc, only for your own bookmark.
        if sorting in ('asc', 'date_d', 'date'):
            url = url + "&order=" + sorting
        if tag is not None and len(tag) > 0:
            url = url + '&tag=' + PixivHelper.encode_tags(tag)
        PixivHelper.print_and_log('info', "Importing user's bookmarked image from page " + str(i))
        PixivHelper.print_and_log('info', "Source URL: " + url)

        page = __br__.open(url)
        parse_page = BeautifulSoup(page.read().decode("utf-8"), features="html5lib")
        bookmarks = PixivBookmark.parseImageBookmark(parse_page)
        total_list.extend(bookmarks)
        if len(bookmarks) == 0:
            print("No more images.")
            break
        else:
            print(" found " + str(len(bookmarks)) + " images.")

        i = i + 1

        page.close()
        parse_page.decompose()
        del parse_page
        # Issue#569
        wait()

    return total_list