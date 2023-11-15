    def parseBookmark(page, root_directory, db_path, locale='en', is_json=False):
        '''Parse favorite artist page'''
        from PixivDBManager import PixivDBManager
        bookmarks = list()
        result2 = list()
        db = PixivDBManager(root_directory=root_directory, target=db_path)

        if is_json:
            parsed = json.loads(page)
            for member in parsed["body"]["users"]:
                result2.append(member["userId"])
        else:
            # old method
            parse_page = BeautifulSoup(page, features="html5lib")
            __re_member = re.compile(locale + r'/users/(\d*)')

            member_list = parse_page.find(attrs={'class': 'members'})
            result = member_list.findAll('a')

            # filter duplicated member_id
            d = collections.OrderedDict()
            for r in result:
                member_id = __re_member.findall(r['href'])
                if len(member_id) > 0:
                    d[member_id[0]] = member_id[0]
            result2 = list(d.keys())

            parse_page.decompose()
            del parse_page

        for r in result2:
            item = db.selectMemberByMemberId2(r)
            bookmarks.append(item)

        return bookmarks