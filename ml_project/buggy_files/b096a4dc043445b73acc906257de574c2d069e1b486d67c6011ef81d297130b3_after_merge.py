    def update_figure(self):
        if self.image_dict is None:
            return
        with self.image_dict_lock:
            image_dict = dict([(x, y.copy()) for x, y in self.image_dict.iteritems()])
        channel_dict = {}
        totals = np.zeros(4)
        for i in range(self.channel_grid.GetNumberRows()):
            channel_name = self.channel_grid.GetRowLabelValue(i)
            channel_dict[channel_name] = np.array([
                int(self.channel_grid.GetCellValue(i, j))
                for j in range(4)], float)
            totals += channel_dict[channel_name]
            
        site_dict = {}
        tile_dims = [0, 0]
        if self.use_site_grid:
            for i in range(self.site_grid.GetNumberRows()):
                site_name = self.site_grid.GetRowLabelValue(i)
                site_dict[site_name] = np.array([
                    float(self.site_grid.GetCellValue(i, j)) - 1
                    for j in range(2)])[::-1]
                tile_dims = [max(i0, i1) for i0, i1 in zip(
                    site_dict[site_name], tile_dims)]
        else:
            site_dict[None] = np.zeros(2)
        img_size = [0, 0]
        for sd in image_dict.values():
            for channel in sd:
                img_size = [max(i0, i1) for i0, i1 in zip(
                    sd[channel].shape, img_size)]
        if all([iii == 0 for iii in img_size]):
            return
        img_size = np.array(img_size)
        tile_dims = np.array(tile_dims)+1
        for k in site_dict:
            site_dict[k] *= img_size
        img_size = np.hstack([np.ceil(tile_dims * img_size).astype(int), [3]])
        megapicture = np.zeros(img_size, np.uint8)
        for site, sd in image_dict.iteritems():
            offs = site_dict[site].astype(int)
            # TO_DO - handle images that aren't scaled from 0 to 255
            for channel, image in sd.iteritems():
                imgmax = np.max(image)
                scale = 1 if imgmax <= 1 else 255 if imgmax < 256 \
                    else 4095 if imgmax < 4096 else 65535
                a = channel_dict[channel][3]
                rgb = channel_dict[channel][:3] / 255.
                image = image * a / scale
                if image.ndim < 3:
                    image = image[:, :, np.newaxis] * rgb[np.newaxis, np.newaxis, :]
                
                if image.shape[0] + offs[0] > megapicture.shape[0]:
                    image = image[:(megapicture.shape[0] - offs[0]), :, :]
                if image.shape[1] + offs[1] > megapicture.shape[1]:
                    image = image[:, :(megapicture.shape[1] - offs[1]), :]
                megapicture[offs[0]:(offs[0]+image.shape[0]),
                            offs[1]:(offs[1]+image.shape[1]), :] += image.astype(megapicture.dtype)
        self.axes.cla()
        self.axes.imshow(megapicture)
        self.canvas.draw()
        self.navtoolbar.update()