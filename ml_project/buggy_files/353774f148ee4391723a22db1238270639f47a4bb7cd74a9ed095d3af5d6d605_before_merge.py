def get_lilliefors_table(dist='norm'):
    '''
    Generates tables for significance levels of Lilliefors test statistics

    Tables for available normal and exponential distribution testing,
    as specified in Lilliefors references above

    Parameters
    ----------
    dist : string.
        distribution being tested in set {'norm', 'exp'}.

    Returns
    -------
    lf : TableDist object.
        table of critical values
    '''
    # function just to keep things together
    # for this test alpha is sf probability, i.e. right tail probability

    if dist == 'norm':
        alpha = np.array([ 0.2  ,  0.15 ,  0.1  ,  0.05 ,  0.01 ,  0.001])[::-1]
        size = np.array([ 4,   5,   6,   7,   8,   9,  10,  11,  12,  13,  14,  15,
                     16,  17,  18,  19,  20,  25,  30,  40, 100, 400, 900], float)

        # critical values, rows are by sample size, columns are by alpha
        crit_lf = np.array(   [[303, 321, 346, 376, 413, 433],
                               [289, 303, 319, 343, 397, 439],
                               [269, 281, 297, 323, 371, 424],
                               [252, 264, 280, 304, 351, 402],
                               [239, 250, 265, 288, 333, 384],
                               [227, 238, 252, 274, 317, 365],
                               [217, 228, 241, 262, 304, 352],
                               [208, 218, 231, 251, 291, 338],
                               [200, 210, 222, 242, 281, 325],
                               [193, 202, 215, 234, 271, 314],
                               [187, 196, 208, 226, 262, 305],
                               [181, 190, 201, 219, 254, 296],
                               [176, 184, 195, 213, 247, 287],
                               [171, 179, 190, 207, 240, 279],
                               [167, 175, 185, 202, 234, 273],
                               [163, 170, 181, 197, 228, 266],
                               [159, 166, 176, 192, 223, 260],
                               [143, 150, 159, 173, 201, 236],
                               [131, 138, 146, 159, 185, 217],
                               [115, 120, 128, 139, 162, 189],
                               [ 74,  77,  82,  89, 104, 122],
                               [ 37,  39,  41,  45,  52,  61],
                               [ 25,  26,  28,  30,  35,  42]])[:,::-1] / 1000.

        # also build a table for larger sample sizes
        def f(n):
            return np.array([0.736, 0.768, 0.805, 0.886, 1.031]) / np.sqrt(n)

        higher_sizes = np.array([35, 40, 45, 50, 60, 70,
                                 80, 100, 200, 500, 1000,
                                 2000, 3000, 5000, 10000, 100000], float)
        higher_crit_lf = np.zeros([higher_sizes.shape[0], crit_lf.shape[1]-1])
        for i in range(len(higher_sizes)):
            higher_crit_lf[i, :] = f(higher_sizes[i])

        alpha_large = alpha[:-1]
        size_large = np.concatenate([size, higher_sizes])
        crit_lf_large = np.vstack([crit_lf[:-4,:-1], higher_crit_lf])
        lf = TableDist(alpha, size, crit_lf)

    elif dist == 'exp':
        alpha = np.array([0.2,  0.15,  0.1,  0.05, 0.01])[::-1]
        size = np.array([3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,25,30],
                        float)

        crit_lf = np.array([   [451, 479, 511, 551, 600],
                                [396, 422, 499, 487, 548],
                                [359, 382, 406, 442, 504],
                                [331, 351, 375, 408, 470],
                                [309, 327, 350, 382, 442],
                                [291, 308, 329, 360, 419],
                                [277, 291, 311, 341, 399],
                                [263, 277, 295, 325, 380],
                                [251, 264, 283, 311, 365],
                                [241, 254, 271, 298, 351],
                                [232, 245, 261, 287, 338],
                                [224, 237, 252, 277, 326],
                                [217, 229, 244, 269, 315],
                                [211, 222, 236, 261, 306],
                                [204, 215, 229, 253, 297],
                                [199, 210, 223, 246, 289],
                                [193, 204, 218, 239, 283],
                                [188, 199, 212, 234, 278],
                                [170, 180, 191, 210, 247],
                                [155, 164, 174, 192, 226]])[:,::-1] / 1000.

        def f(n):
            return np.array([.86, .91, .96, 1.06, 1.25]) / np.sqrt(n)

        higher_sizes = np.array([35, 40, 45, 50, 60, 70,
                                80, 100, 200, 500, 1000,
                                2000, 3000, 5000, 10000, 100000], float)
        higher_crit_lf = np.zeros([higher_sizes.shape[0], crit_lf.shape[1]])
        for i in range(len(higher_sizes)):
            higher_crit_lf[i,:] = f(higher_sizes[i])

        size = np.concatenate([size, higher_sizes])
        crit_lf = np.vstack([crit_lf, higher_crit_lf])
        lf = TableDist(alpha, size, crit_lf)
    else:
        raise ValueError("Invalid dist parameter. dist must be 'norm' or 'exp'")

    return lf