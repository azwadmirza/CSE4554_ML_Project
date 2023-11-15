    def hash_area(area):
        """Get (and set) the hash for the *area*.
        """
        try:
            return area.kdtree_hash
        except AttributeError:
            LOG.debug("Computing kd-tree hash for area %s",
                      getattr(area, 'name', 'swath'))
        try:
            area_hash = "".join((hashlib.sha1(json.dumps(area.proj_dict,
                                                         sort_keys=True).encode("utf-8")).hexdigest(),
                                 hashlib.sha1(json.dumps(area.area_extent).encode(
                                     "utf-8")).hexdigest(),
                                 hashlib.sha1(json.dumps((int(area.shape[0]),
                                                          int(area.shape[1]))).encode('utf-8')).hexdigest()))
        except AttributeError:
            if not hasattr(area, "lons") or area.lons is None:
                lons, lats = area.get_lonlats()
            else:
                lons, lats = area.lons, area.lats

            try:
                mask_hash = hashlib.sha1(lons.mask | lats.mask).hexdigest()
            except AttributeError:
                mask_hash = "False"
            area_hash = "".join((mask_hash,
                                 hashlib.sha1(lons).hexdigest(),
                                 hashlib.sha1(lats).hexdigest()))
        area.kdtree_hash = area_hash
        return area_hash