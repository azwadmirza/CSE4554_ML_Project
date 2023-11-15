	def _getFormatFieldAndOffsets(self,offset,formatConfig,calculateOffsets=True):
		formatField=textInfos.FormatField()
		if (self.obj.excelCellObject.Application.Version > "12.0"):
			cellObj=self.obj.excelCellObject.DisplayFormat
		else:
			cellObj=self.obj.excelCellObject
		fontObj=cellObj.font
		if formatConfig['reportAlignment']:
			value=alignmentLabels.get(self.obj.excelCellObject.horizontalAlignment)
			if value:
				formatField['text-align']=value
			value=alignmentLabels.get(self.obj.excelCellObject.verticalAlignment)
			if value:
				formatField['vertical-align']=value
		if formatConfig['reportFontName']:
			formatField['font-name']=fontObj.name
		if formatConfig['reportFontSize']:
			formatField['font-size']=str(fontObj.size)
		if formatConfig['reportFontAttributes']:
			formatField['bold']=fontObj.bold
			formatField['italic']=fontObj.italic
			underline=fontObj.underline
			formatField['underline']=False if underline is None or underline==xlUnderlineStyleNone else True
		if formatConfig['reportStyle']:
			try:
				styleName=self.obj.excelCellObject.style.nameLocal
			except COMError:
				styleName=None
			if styleName:
				formatField['style']=styleName
		if formatConfig['reportColor']:
			try:
				formatField['color']=colors.RGB.fromCOLORREF(int(fontObj.color))
			except COMError:
				pass
			try:
				pattern = cellObj.Interior.Pattern
				formatField['background-pattern'] = backgroundPatternLabels.get(pattern)
				if pattern in (xlPatternLinearGradient, xlPatternRectangularGradient):
					formatField['background-color']=(colors.RGB.fromCOLORREF(int(cellObj.Interior.Gradient.ColorStops(1).Color)))
					formatField['background-color2']=(colors.RGB.fromCOLORREF(int(cellObj.Interior.Gradient.ColorStops(2).Color)))
				else:
					formatField['background-color']=colors.RGB.fromCOLORREF(int(cellObj.interior.color))
			except COMError:
				pass
		if formatConfig["reportBorderStyle"]:
			borders = None
			hasMergedCells = self.obj.excelCellObject.mergeCells
			if hasMergedCells:
				mergeArea = self.obj.excelCellObject.mergeArea
				try:
					borders = mergeArea.DisplayFormat.borders # for later versions of office
				except COMError:
					borders = mergeArea.borders # for office 2007
			else:
				borders = cellObj.borders
			try:
				formatField['border-style']=getCellBorderStyleDescription(borders,reportBorderColor=formatConfig['reportBorderColor'])
			except COMError:
				pass
		return formatField,(self._startOffset,self._endOffset)