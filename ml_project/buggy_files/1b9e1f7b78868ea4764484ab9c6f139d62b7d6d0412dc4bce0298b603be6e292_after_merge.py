def GetResultBitrateLength(filesize, attributes):
    """ Used to get the audio bitrate and length of search results and
    user browse files """

    h_bitrate = ""
    h_length = ""

    bitrate = 0

    # If there are 3 entries in the attribute list
    if len(attributes) == 3:

        a = attributes

        # Sometimes the vbr indicator is in third position
        if a[2] == 0 or a[2] == 1:

            if a[2] == 1:
                h_bitrate = " (vbr)"

            bitrate = a[0]
            h_bitrate = str(bitrate) + h_bitrate

            h_length = '%i:%02i' % (a[1] / 60, a[1] % 60)

        # Sometimes the vbr indicator is in second position
        elif a[1] == 0 or a[1] == 1:

            if a[1] == 1:
                h_bitrate = " (vbr)"

            bitrate = a[0]
            h_bitrate = str(bitrate) + h_bitrate

            h_length = '%i:%02i' % (a[2] / 60, a[2] % 60)

        # Lossless audio, length is in first position
        elif a[2] > 1:

            # Bitrate = sample rate (Hz) * word length (bits) * channel count
            # Bitrate = 44100 * 16 * 2
            bitrate = (a[1] * a[2] * 2) / 1000
            h_bitrate = str(bitrate)

            h_length = '%i:%02i' % (a[0] / 60, a[0] % 60)

        else:

            bitrate = a[0]
            h_bitrate = str(bitrate) + h_bitrate

    # If there are 2 entries in the attribute list
    elif len(attributes) == 2:

        a = attributes

        # Sometimes the vbr indicator is in second position
        if a[1] == 0 or a[1] == 1:

            # If it's a vbr file we can't deduce the length
            if a[1] == 1:

                h_bitrate = " (vbr)"

                bitrate = a[0]
                h_bitrate = str(bitrate) + h_bitrate

            # If it's a constant bitrate we can deduce the length
            else:

                bitrate = a[0]
                h_bitrate = str(bitrate) + h_bitrate

                # Dividing the file size by the bitrate in Bytes should give us a good enough approximation
                length = filesize / (bitrate / 8 * 1000)

                h_length = '%i:%02i' % (length / 60, length % 60)

        # Sometimes the bitrate is in first position and the length in second position
        else:

            bitrate = a[0]
            h_bitrate = str(bitrate) + h_bitrate

            h_length = '%i:%02i' % (a[1] / 60, a[1] % 60)

    return h_bitrate, bitrate, h_length