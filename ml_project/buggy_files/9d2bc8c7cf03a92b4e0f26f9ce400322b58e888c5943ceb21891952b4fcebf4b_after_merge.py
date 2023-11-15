    def parseImageBookmark(page):
        imageList = list()

        image_bookmark = json.loads(page)
        for work in image_bookmark["body"]["works"]:
            if "isAdContainer" in work and work["isAdContainer"]:
                continue
            # Issue #822
            if "illustId" in work:
                imageList.append(int(work["illustId"]))
            elif "id" in work:
                imageList.append(int(work["id"]))

        # temp = page.find('ul', attrs={'class': PixivBookmark.__re_imageULItemsClass})
        # temp = temp.findAll('a')
        # if temp is None or len(temp) == 0:
        #     return imageList
        # for item in temp:
        #     href = re.search(r'/artworks/(\d+)', str(item))
        #     if href is not None:
        #         href = href.group(1)
        #         if not int(href) in imageList:
        #             imageList.append(int(href))

        return imageList