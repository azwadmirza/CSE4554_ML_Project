def _b_orthonormalize(B, blockVectorV, blockVectorBV=None, retInvR=False):
    if blockVectorBV is None:
        if B is not None:
            blockVectorBV = B(blockVectorV)
        else:
            blockVectorBV = blockVectorV  # Shared data!!!
    gramVBV = np.dot(blockVectorV.T.conj(), blockVectorBV)
    gramVBV = cholesky(gramVBV)
    gramVBV = inv(gramVBV, overwrite_a=True)
    # gramVBV is now R^{-1}.
    blockVectorV = np.dot(blockVectorV, gramVBV)
    if B is not None:
        blockVectorBV = np.dot(blockVectorBV, gramVBV)
    else:
        blockVectorBV = None

    if retInvR:
        return blockVectorV, blockVectorBV, gramVBV
    else:
        return blockVectorV, blockVectorBV