    def display_split(self, workspace, figure):
        import matplotlib.cm

        input_image = workspace.display_data.input_image
        disp_collection = workspace.display_data.disp_collection
        ndisp = len(disp_collection)
        ncols = int(np.ceil((ndisp+1)**0.5))
        subplots = (ncols, (ndisp/ncols)+1)
        figure.set_subplots(subplots)
        figure.subplot_imshow_color(0, 0, input_image, title="Original image")

        for eachplot in range(ndisp):
             placenum = eachplot +1
             figure.subplot_imshow(placenum%ncols, placenum/ncols, disp_collection[eachplot][0],
                                   title="%s" % (disp_collection[eachplot][1]),
                                   colormap=matplotlib.cm.Greys_r,
                                   sharexy=figure.subplot(0, 0))