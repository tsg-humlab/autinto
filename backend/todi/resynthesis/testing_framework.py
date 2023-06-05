import textgrid

def compare(file1, file2):
	tg1 = textgrid.TextGrid.fromFile(file1 + ".TextGrid")
	tg2 = textgrid.TextGrid.fromFile(file2 + ".TextGrid")

	for i in range(len(tg1)):
		if len(tg1[i]) != len(tg2[i]):
			return False
		for j in range(len(tg1[i])):
			if tg1[i][j] != tg2[i][j]:
				return False

	return len(tg1) == len(tg2)


file1 = "/home/pim/Documents/todi/147"
file2 = "/home/pim/Documents/todi/148"

print(compare(file1, file2))

