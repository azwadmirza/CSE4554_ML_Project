def get_image_bookmark(hide, start_page=1, end_page=0, tag='', sorting=None):
    """Get user's image bookmark"""
    total_list = list()
    i = start_page
    offset = 0
    limit = 48
    member_id = __br__._myId

    while True:
        if end_page != 0 and i > end_page:
            print("Page Limit reached: " + str(end_page))
            break

        # https://www.pixiv.net/ajax/user/189816/illusts/bookmarks?tag=&offset=0&limit=48&rest=show
        show = "show"
        if hide:
            show = "hide"

        # # Implement #468 default is desc, only for your own bookmark.
        # not available in current api
        # if sorting in ('asc', 'date_d', 'date'):
        #     url = url + "&order=" + sorting

        if tag is not None and len(tag) > 0:
            tag = PixivHelper.encode_tags(tag)
        offset = limit * (i - 1)
        url = f"https://www.pixiv.net/ajax/user/{member_id}/illusts/bookmarks?tag={tag}&offset={offset}&limit={limit}&rest={show}"

        PixivHelper.print_and_log('info', f"Importing user's bookmarked image from page {i}")
        PixivHelper.print_and_log('info', f"Source URL: {url}")

        page = __br__.open(url)
        page_str = page.read().decode('utf8')
        page.close()

        bookmarks = PixivBookmark.parseImageBookmark(page_str)
        total_list.extend(bookmarks)
        if len(bookmarks) == 0:
            print("No more images.")
            break
        else:
            print(" found " + str(len(bookmarks)) + " images.")

        i = i + 1

        # Issue#569
        wait()

    return total_list