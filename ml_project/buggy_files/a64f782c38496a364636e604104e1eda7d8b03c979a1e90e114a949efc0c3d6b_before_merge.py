    def roiChanged(self):
        if self.image is None:
            return
            
        image = self.getProcessedImage()

        # Extract image data from ROI
        axes = (self.axes['x'], self.axes['y'])

        data, coords = self.roi.getArrayRegion(image.view(np.ndarray), self.imageItem, returnMappedCoords=True)
        if data is None:
            return

        # Convert extracted data into 1D plot data
        if self.axes['t'] is None:
            # Average across y-axis of ROI
            data = data.mean(axis=axes[1])
            if axes == (1,0): ## we're in row-major order mode -- there's probably a better way to do this slicing dynamically, but I've not figured it out yet.
                coords = coords[:,0,:] - coords[:,0,0:1]
            else: #default to old way
                coords = coords[:,:,0] - coords[:,0:1,0] 
            xvals = (coords**2).sum(axis=0) ** 0.5
        else:
            # Average data within entire ROI for each frame
            data = data.mean(axis=max(axes)).mean(axis=min(axes))
            xvals = self.tVals

        # Handle multi-channel data
        if data.ndim == 1:
            plots = [(xvals, data, 'w')]
        if data.ndim == 2:
            if data.shape[1] == 1:
                colors = 'w'
            else:
                colors = 'rgbw'
            plots = []
            for i in range(data.shape[1]):
                d = data[:,i]
                plots.append((xvals, d, colors[i]))

        # Update plot line(s)
        while len(plots) < len(self.roiCurves):
            c = self.roiCurves.pop()
            c.scene().removeItem(c)
        while len(plots) > len(self.roiCurves):
            self.roiCurves.append(self.ui.roiPlot.plot())
        for i in range(len(plots)):
            x, y, p = plots[i]
            self.roiCurves[i].setData(x, y, pen=p)