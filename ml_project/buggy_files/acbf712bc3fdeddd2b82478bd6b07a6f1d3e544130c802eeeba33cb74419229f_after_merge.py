    def plotGamma(self, event=None):
        msg = _translate('%(monName)s %(calibName)s Gamma Functions')
        figTitle = msg % {'monName': self.currentMonName,
                          'calibName': self.currentCalibName}
        plotWindow = PlotFrame(self, 1003, figTitle)

        figure = Figure(figsize=(5, 5), dpi=80)
        figureCanvas = FigureCanvas(plotWindow, -1, figure)
        plt = figure.add_subplot(111)
        plt.cla()

        gammaGrid = self.currentMon.getGammaGrid()
        lumsPre = self.currentMon.getLumsPre()
        levelsPre = self.currentMon.getLevelsPre()
        lumsPost = self.currentMon.getLumsPost()

        # Handle the case where the button is pressed but no gamma data is
        # available.
        if lumsPre is None:
            return   # nop
        elif lumsPre.any() != None:
            colors = 'krgb'
            xxSmooth = numpy.arange(0, 255.5, 0.5)
            eq = self.currentMon.getLinearizeMethod()
            for gun in range(4):  # includes lum
                gamma = gammaGrid[gun, 2]
                minLum = gammaGrid[gun, 0]
                maxLum = gammaGrid[gun, 1]
                if eq <= 2:
                    # plot fitted curve
                    curve = monitors.gammaFun(xxSmooth, minLum, maxLum, gamma,
                                              eq=eq, a=None, b=None, k=None)
                    plt.plot(xxSmooth, curve, colors[gun] + '-',
                             linewidth=1.5)
                if self.currentMon.getLinearizeMethod() == 4:
                    a, b, k = gammaGrid[gun, 3:]
                    # plot fitted curve
                    curve = monitors.gammaFun(xxSmooth, minLum, maxLum, gamma,
                                              eq=eq, a=a, b=b, k=k)
                    plt.plot(xxSmooth, curve, colors[gun] + '-',
                             linewidth=1.5)
                else:
                    pass
                    # polyFit = self.currentMon._gammaInterpolator[gun]
                    # curve = xxSmooth*0.0
                    # for expon, coeff in enumerate(polyFit):
                    #    curve += coeff*xxSmooth**expon
                    # plt.plot(xxSmooth, curve, colors[gun]+'-', linewidth=1.5)
                # plot POINTS
                plt.plot(levelsPre, lumsPre[gun, :], colors[gun] + 'o',
                         linewidth=1.5)

            lumsPost = self.currentMon.getLumsPost()
            levelsPost = self.currentMon.getLevelsPost()
        if lumsPost != None:
            for gun in range(4):  # includes lum,r,g,b
                lums = lumsPost[gun, :]
                gamma = gammaGrid[gun, 2]
                minLum = min(lums)
                maxLum = max(lums)
                # plot CURVE
                plt.plot([levelsPost[0], levelsPost[-1]],
                         [minLum, maxLum], colors[gun] + '--', linewidth=1.5)
                # plot POINTS
                plt.plot(levelsPost, lums, 'o', markerfacecolor='w',
                         markeredgecolor=colors[gun], linewidth=1.5)
        figureCanvas.draw()  # update the canvas
        plotWindow.addCanvas(figureCanvas)