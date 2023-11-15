def is_amino_acid_functionally_conserved(amino_acid_residue_1, amino_acid_residue_2):
    """Checks if two amino acid residues are part of the same biochemical property group"""
    group = constants.amino_acid_property_group[amino_acid_residue_1]
    conserved_group = constants.conserved_amino_acid_groups[group]

    if amino_acid_residue_2 in conserved_group:
        return True
    if group == 'Polar and Nonpolar': #they fall in more than one group, multiple tests needed
        if amino_acid_residue_1 == 'H' and (amino_acid_residue_2 in constants.conserved_amino_acid_groups['Nonpolar'] \
                                            or amino_acid_residue_2 in constants.conserved_amino_acid_groups['Bases']):
            return True
        if amino_acid_residue_1 == 'Y' and (amino_acid_residue_2 in constants.conserved_amino_acid_groups['Aromatic']):
            return True
    return False