def get_bookmarks(hide, start_page=1, end_page=0, member_id=None):
    """Get User's bookmarked artists """
    total_list = list()
    i = start_page
    limit = 24
    offset = 0
    is_json = False

    while True:
        if end_page != 0 and i > end_page:
            print('Limit reached')
            break
        PixivHelper.print_and_log('info', f'Exporting page {i}')
        if member_id:
            is_json = True
            offset = 24 * (i - 1)
            url = f'https://www.pixiv.net/ajax/user/{member_id}/following?offset={offset}&limit={limit}'
        else:
            url = f'https://www.pixiv.net/bookmark.php?type=user&p={i}'
        if hide:
            url = url + "&rest=hide"
        else:
            url = url + "&rest=show"

        PixivHelper.print_and_log('info', f"Source URL: {url}")

        page = __br__.open_with_retry(url)
        page_str = page.read().decode('utf8')
        page.close()

        bookmarks = PixivBookmark.parseBookmark(page_str,
                                                root_directory=__config__.rootDirectory,
                                                db_path=__config__.dbPath,
                                                is_json=is_json)

        if len(bookmarks) == 0:
            print('No more data')
            break
        total_list.extend(bookmarks)
        i = i + 1
        print(str(len(bookmarks)), 'items')
        wait()
    return total_list