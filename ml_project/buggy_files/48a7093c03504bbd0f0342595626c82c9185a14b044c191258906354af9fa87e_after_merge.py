def dec10216(inbuf):

    """
    /*
     * pack 4 10-bit words in 5 bytes into 4 16-bit words
     *
     * 0       1       2       3       4       5
     * 01234567890123456789012345678901234567890
     * 0         1         2         3         4
     */
    ip = &in_buffer[i];
    op = &out_buffer[j];
    op[0] = ip[0]*4 + ip[1]/64;
    op[1] = (ip[1] & 0x3F)*16 + ip[2]/16;
    op[2] = (ip[2] & 0x0F)*64 + ip[3]/4;
    op[3] = (ip[3] & 0x03)*256 +ip[4];
    """

    arr10 = inbuf.astype(np.uint16)
    arr16_len = int(len(arr10) * 4 / 5)
    arr10_len = int((arr16_len * 5) / 4)
    arr10 = arr10[:arr10_len]  # adjust size

    # dask is slow with indexing
    arr10_0 = arr10[::5]
    arr10_1 = arr10[1::5]
    arr10_2 = arr10[2::5]
    arr10_3 = arr10[3::5]
    arr10_4 = arr10[4::5]

    arr16_0 = (arr10_0 << 2) + (arr10_1 >> 6)
    arr16_1 = ((arr10_1 & 63) << 4) + (arr10_2 >> 4)
    arr16_2 = ((arr10_2 & 15) << 6) + (arr10_3 >> 2)
    arr16_3 = ((arr10_3 & 3) << 8) + arr10_4
    arr16 = da.stack([arr16_0, arr16_1, arr16_2, arr16_3], axis=-1).ravel()

    return arr16