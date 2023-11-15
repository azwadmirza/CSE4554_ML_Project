def fixSubTableOverFlows(ttf, overflowRecord):
	"""
	An offset has overflowed within a sub-table. We need to divide this subtable into smaller parts.
	"""
	ok = 0
	table = ttf[overflowRecord.tableType].table
	lookup = table.LookupList.Lookup[overflowRecord.LookupListIndex]
	subIndex = overflowRecord.SubTableIndex
	subtable = lookup.SubTable[subIndex]

	# First, try not sharing anything for this subtable...
	if not hasattr(subtable, "DontShare"):
		subtable.DontShare = True
		return True

	if hasattr(subtable, 'ExtSubTable'):
		# We split the subtable of the Extension table, and add a new Extension table
		# to contain the new subtable.

		subTableType = subtable.ExtSubTable.__class__.LookupType
		extSubTable = subtable
		subtable = extSubTable.ExtSubTable
		newExtSubTableClass = lookupTypes[overflowRecord.tableType][extSubTable.__class__.LookupType]
		newExtSubTable = newExtSubTableClass()
		newExtSubTable.Format = extSubTable.Format
		lookup.SubTable.insert(subIndex + 1, newExtSubTable)

		newSubTableClass = lookupTypes[overflowRecord.tableType][subTableType]
		newSubTable = newSubTableClass()
		newExtSubTable.ExtSubTable = newSubTable
	else:
		subTableType = subtable.__class__.LookupType
		newSubTableClass = lookupTypes[overflowRecord.tableType][subTableType]
		newSubTable = newSubTableClass()
		lookup.SubTable.insert(subIndex + 1, newSubTable)

	if hasattr(lookup, 'SubTableCount'): # may not be defined yet.
		lookup.SubTableCount = lookup.SubTableCount + 1

	try:
		splitFunc = splitTable[overflowRecord.tableType][subTableType]
	except KeyError:
		return ok

	ok = splitFunc(subtable, newSubTable, overflowRecord)
	return ok