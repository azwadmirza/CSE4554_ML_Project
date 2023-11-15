def convert(
        ctx, files, output, driver, dtype, scale_ratio, scale_offset,
        photometric, overwrite, creation_options):
    """Copy and convert raster datasets to other data types and formats.

    Data values may be linearly scaled when copying by using the
    --scale-ratio and --scale-offset options. Destination raster values
    are calculated as

      dst = scale_ratio * src + scale_offset

    For example, to scale uint16 data with an actual range of 0-4095 to
    0-255 as uint8:

      $ rio convert in16.tif out8.tif --dtype uint8 --scale-ratio 0.0625

    Format specific creation options may also be passed using --co. To
    tile a new GeoTIFF output file, do the following.

      --co tiled=true --co blockxsize=256 --co blockysize=256

    To compress it using the LZW method, add

      --co compress=LZW

    """
    with ctx.obj['env']:

        outputfile, files = resolve_inout(
            files=files, output=output, overwrite=overwrite, num_inputs=1
        )
        inputfile = files[0]

        with rasterio.open(inputfile) as src:

            # Use the input file's profile, updated by CLI
            # options, as the profile for the output file.
            profile = src.profile

            if driver:
                profile['driver'] = driver

            if dtype:
                profile['dtype'] = dtype
            dst_dtype = profile['dtype']

            if photometric:
                creation_options['photometric'] = photometric

            profile.update(**creation_options)

            with rasterio.open(outputfile, 'w', **profile) as dst:

                data = src.read()

                if scale_ratio:
                    # Cast to float64 before multiplying.
                    data = data.astype('float64', casting='unsafe', copy=False)
                    np.multiply(
                        data, scale_ratio, out=data, casting='unsafe')

                if scale_offset:
                    # My understanding of copy=False is that this is a
                    # no-op if the array was cast for multiplication.
                    data = data.astype('float64', casting='unsafe', copy=False)
                    np.add(
                        data, scale_offset, out=data, casting='unsafe')

                # Cast to the output dtype and write.
                result = data.astype(dst_dtype, casting='unsafe', copy=False)
                dst.write(result)