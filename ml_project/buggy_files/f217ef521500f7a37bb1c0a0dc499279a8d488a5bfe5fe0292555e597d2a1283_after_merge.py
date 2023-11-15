    def _unpack_data(self,file,encoding='latin-1'):
        """This needs to be special because it reads until the end of
        file. This causes an error in the series of data"""

        #Size of datapoints in bytes. Always int16 (==2) or 32 (==4)
        Psize = int(self._get_work_dict_key_value('_15_Size_of_Points')/8)
        dtype = np.int16 if Psize == 2 else np.int32

        if self._get_work_dict_key_value('_01_Signature') != 'DSCOMPRESSED' :
            #If the points are not compressed we need to read the exact
            #size occupied by datapoints

            #Datapoints in X and Y dimensions
            Npts_tot = self._get_work_dict_key_value('_20_Total_Nb_of_Pts')
            #Datasize in WL
            Wsize = self._get_work_dict_key_value('_14_W_Size')

            #We need to take into account the fact that Wsize is often
            #set to 0 instead of 1 in non-spectral data to compute the
            #space occupied by data in the file
            readsize = Npts_tot*Psize
            if Wsize != 0:
                readsize*=Wsize
            #if Npts_channel is not 0:
            #    readsize*=Npts_channel

            #Read the exact size of the data
            _points = np.frombuffer(file.read(readsize),dtype=dtype)
            #_points = np.fromstring(file.read(readsize),dtype=dtype)

        else:
            #If the points are compressed do the uncompress magic. There
            #the space occupied by datapoints is self-taken care of.
            #Number of streams
            _directoryCount = self._get_uint32(file)

            #empty lists to store the read sizes
            rawLengthData = []
            zipLengthData = []
            for i in range(_directoryCount):
                #Size of raw and compressed data sizes in each stream
                rawLengthData.append(self._get_uint32(file))
                zipLengthData.append(self._get_uint32(file))

            #We now initialize an empty binary string to store the results
            rawData = b''
            for i in range(_directoryCount):
                #And for each stream we uncompress using zip lib
                #and add it to raw string
                rawData += zlib.decompress(file.read(zipLengthData[i]))

            #Finally numpy converts it to a numeric object
            _points = np.frombuffer(rawData, dtype=dtype)
            #_points = np.fromstring(rawData, dtype=dtype)

        # rescale data
        #We set non measured points to nan according to .sur ways
        nm = []
        if self._get_work_dict_key_value("_11_Special_Points") == 1 :
            # has unmeasured points
            nm = _points == self._get_work_dict_key_value("_16_Zmin")-2

        #We set the point in the numeric scale
        _points = _points.astype(np.float) \
            * self._get_work_dict_key_value("_23_Z_Spacing") \
            * self._get_work_dict_key_value("_35_Z_Unit_Ratio") \
            + self._get_work_dict_key_value("_55_Z_Offset")

        _points[nm] = np.nan
        #Return the points, rescaled
        return _points