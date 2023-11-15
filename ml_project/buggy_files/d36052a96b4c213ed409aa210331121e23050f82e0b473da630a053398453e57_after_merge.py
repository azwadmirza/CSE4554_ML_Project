    def get_mapping(self):
        is_scanning = "DigiScan" in self.imdict.ImageTags.keys()
        mapping = {
            "ImageList.TagGroup0.ImageTags.DataBar.Acquisition Date": (
                "General.date",
                self._get_date),
            "ImageList.TagGroup0.ImageTags.DataBar.Acquisition Time": (
                "General.time",
                self._get_time),
            "ImageList.TagGroup0.ImageTags.Microscope Info.Voltage": (
                "Acquisition_instrument.TEM.beam_energy",
                lambda x: x / 1e3),
            "ImageList.TagGroup0.ImageTags.Microscope Info.Stage Position.Stage Alpha": (
                "Acquisition_instrument.TEM.tilt_stage",
                None),
            "ImageList.TagGroup0.ImageTags.Microscope Info.Illumination Mode": (
                "Acquisition_instrument.TEM.acquisition_mode",
                self._get_mode),
            "ImageList.TagGroup0.ImageTags.Microscope Info.Probe Current (nA)": (
                "Acquisition_instrument.TEM.beam_current",
                None),
            "ImageList.TagGroup0.ImageTags.Session Info.Operator": (
                "General.authors",
                self._parse_string),
            "ImageList.TagGroup0.ImageTags.Session Info.Specimen": (
                "Sample.description",
                self._parse_string),
        }

        if "Microscope_Info" in self.imdict.ImageTags.keys():
            is_TEM = is_diffraction = None
            if "Illumination_Mode" in self.imdict.ImageTags['Microscope_Info'].keys():
                is_TEM = (
                    'TEM' == self.imdict.ImageTags.Microscope_Info.Illumination_Mode)
            if "Imaging_Mode" in self.imdict.ImageTags['Microscope_Info'].keys():
                is_diffraction = (
                    'DIFFRACTION' == self.imdict.ImageTags.Microscope_Info.Imaging_Mode)

            if is_TEM:
                if is_diffraction:
                    mapping.update({
                        "ImageList.TagGroup0.ImageTags.Microscope Info.Indicated Magnification": (
                            "Acquisition_instrument.TEM.camera_length",
                            None),
                    })
                else:
                    mapping.update({
                        "ImageList.TagGroup0.ImageTags.Microscope Info.Indicated Magnification": (
                            "Acquisition_instrument.TEM.magnification",
                            None),
                    })
            else:
                mapping.update({
                    "ImageList.TagGroup0.ImageTags.Microscope Info.STEM Camera Length": (
                        "Acquisition_instrument.TEM.camera_length",
                        None),
                    "ImageList.TagGroup0.ImageTags.Microscope Info.Indicated Magnification": (
                        "Acquisition_instrument.TEM.magnification",
                        None),
                })

            mapping.update({
                "ImageList.TagGroup0.ImageTags": (
                    "Acquisition_instrument.TEM.microscope",
                    self._get_microscope_name),
                "ImageList.TagGroup0.ImageData.Calibrations.Brightness.Units": (
                    "Signal.quantity",
                    self._get_quantity),
                "ImageList.TagGroup0.ImageData.Calibrations.Brightness.Scale": (
                    "Signal.Noise_properties.Variance_linear_model.gain_factor",
                    None),
                "ImageList.TagGroup0.ImageData.Calibrations.Brightness.Origin": (
                    "Signal.Noise_properties.Variance_linear_model.gain_offset",
                    None),
            })

        if self.signal_type == "EELS":
            if is_scanning:
                mapped_attribute = 'dwell_time'
            else:
                mapped_attribute = 'exposure'
            mapping.update({
                "ImageList.TagGroup0.ImageTags.EELS.Acquisition.Date": (
                    "General.date",
                    self._get_date),
                "ImageList.TagGroup0.ImageTags.EELS.Acquisition.Start time": (
                    "General.time",
                    self._get_time),
                "ImageList.TagGroup0.ImageTags.EELS.Experimental Conditions." +
                "Collection semi-angle (mrad)": (
                    "Acquisition_instrument.TEM.Detector.EELS.collection_angle",
                    None),
                "ImageList.TagGroup0.ImageTags.EELS.Experimental Conditions." +
                "Convergence semi-angle (mrad)": (
                    "Acquisition_instrument.TEM.convergence_angle",
                    None),
                "ImageList.TagGroup0.ImageTags.EELS.Acquisition.Integration time (s)": (
                    "Acquisition_instrument.TEM.Detector.EELS.%s" % mapped_attribute,
                    None),
                "ImageList.TagGroup0.ImageTags.EELS.Acquisition.Number_of_frames": (
                    "Acquisition_instrument.TEM.Detector.EELS.frame_number",
                    None),
                "ImageList.TagGroup0.ImageTags.EELS_Spectrometer.Aperture_label": (
                    "Acquisition_instrument.TEM.Detector.EELS.aperture_size",
                    lambda string: float(string.replace(' mm', ''))),
                "ImageList.TagGroup0.ImageTags.EELS Spectrometer.Instrument name": (
                    "Acquisition_instrument.TEM.Detector.EELS.spectrometer",
                    None),
            })
        elif self.signal_type == "EDS_TEM":
            mapping.update({
                "ImageList.TagGroup0.ImageTags.EDS.Acquisition.Date": (
                    "General.date",
                    self._get_date),
                "ImageList.TagGroup0.ImageTags.EDS.Acquisition.Start time": (
                    "General.time",
                    self._get_time),
                "ImageList.TagGroup0.ImageTags.EDS.Detector_Info.Azimuthal_angle": (
                    "Acquisition_instrument.TEM.Detector.EDS.azimuth_angle",
                    None),
                "ImageList.TagGroup0.ImageTags.EDS.Detector_Info.Elevation_angle": (
                    "Acquisition_instrument.TEM.Detector.EDS.elevation_angle",
                    None),
                "ImageList.TagGroup0.ImageTags.EDS.Solid_angle": (
                    "Acquisition_instrument.TEM.Detector.EDS.solid_angle",
                    None),
                "ImageList.TagGroup0.ImageTags.EDS.Live_time": (
                    "Acquisition_instrument.TEM.Detector.EDS.live_time",
                    None),
                "ImageList.TagGroup0.ImageTags.EDS.Real_time": (
                    "Acquisition_instrument.TEM.Detector.EDS.real_time",
                    None),
            })
        elif "DigiScan" in self.imdict.ImageTags.keys():
            mapping.update({
                "ImageList.TagGroup0.ImageTags.DigiScan.Sample Time": (
                    "Acquisition_instrument.TEM.dwell_time",
                    lambda x: x / 1e6),
            })
        else:
            mapping.update({
                "ImageList.TagGroup0.ImageTags.Acquisition.Parameters.Detector." +
                "exposure_s": (
                    "Acquisition_instrument.TEM.exposure_time",
                    None),
            })
        return mapping