    def parseImageBookmark(page):
        imageList = list()

        temp = page.find('ul', attrs={'class': PixivBookmark.__re_imageULItemsClass})
        temp = temp.findAll('a')
        if temp is None or len(temp) == 0:
            return imageList
        for item in temp:
            href = re.search(r'/artworks/(\d+)', str(item))
            if href is not None:
                href = href.group(1)
                if not int(href) in imageList:
                    imageList.append(int(href))

        return imageList