from os import listdir
from os.path import isfile, join
import _pickle as pickle
import bz2
import lzma
# directory_load = './comb/'
directory_load = '/scratch/sayar/comb/'

# directory_store = './new_comb/'
directory_store = '/scratch/sayar/new_comb/'
files = [f for f in listdir(directory_load) if isfile(join(directory_load, f))]
count = 0

for file in files:
	print(file)
	f = open(directory_load + file, "rb")
	dic = pickle.load(f)
	name = ''

	key_set = []
	for key in dic.keys():
		name = key[0]
		key_set.append(key)

	key_set.sort()

	temp_dict = {}

	if ord(name[0]) >= ord('0') and ord(name[0]) <= ord('9'):
		print("Numeral")
	else:
		print("Alphabetical")

	for key in key_set:
		if len(key) >= 5:
			name_two = key[0: 5]
		elif len(key) == 4:
			name_two = key[0: 4]
		elif len(key) == 3:
			name_two = key[0: 3]
		elif len(key) == 2:
			name_two = key[0: 2]
		elif len(key) == 1:
			name_two = key[0]
		
		temp = dic[key]
		temp.pop()
		new_temp = []
		all_sizes = []
		
		for listie in temp:
			listie.sort(key = lambda x: x[1], reverse = True)
			sizie = len(listie)
			new_temp.append(listie[0:])
			all_sizes.append(sizie)

		new_temp.append(all_sizes)
		if count < 5:
			print(new_temp)
		count += 1
		if name_two not in temp_dict:
			temp_dict[name_two] = {}
		temp_dict[name_two][key] = new_temp

	for key in temp_dict.keys():
		with lzma.open(directory_store + str(key) + ".xz", 'wb') as f:
			pickle.dump(temp_dict[key], f)
print(count)
