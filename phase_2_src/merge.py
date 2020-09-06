import subprocess

import pickle
import sys
import re
import os
import shutil

from os import listdir
from os.path import isfile, join

sequence = []

mypath = "./temp_dicts"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

start_flag = 0
start_dict = {}

for idx in range(10):
	sequence.append(str(idx))
	file_final = open("./comb/" + str(idx) + ".pickle", "wb")
	pickle.dump({}, file_final)
	file_final.close()

for idx in range(26):
	sequence.append(str(chr(ord('a') + idx)))
	file_final = open("./comb/" + str(chr(ord('a') + idx)) + ".pickle", "wb")
	pickle.dump({}, file_final)
	file_final.close()

charsize = len(sequence)

print(sequence)

count = 1
set_A = []

for data_path in onlyfiles:
	file_path = mypath + "/" + data_path
	print(count)
	count += 1

	if start_flag == 0:
		start_flag = 1
		file = open(file_path, "rb")
		try:
			start_dict = pickle.load(file)
		except EOFError:
			start_dict = {}
		
		for key in start_dict.keys():
			set_A.append(key)

		set_A.sort()

		seq_ptr = 0
		now_file = open("./comb/0" + ".pickle", "rb")
		
		try:
			now_dict = pickle.load(file)
		except EOFError:
			now_dict = {}
		now_file = open("./comb/0" + ".pickle", "wb")

		for key in set_A:
			if key[0] != sequence[seq_ptr]:
				pickle.dump(now_dict, now_file)
				now_file.close()

				while seq_ptr < charsize and key[0] > sequence[seq_ptr]:
					seq_ptr += 1

				if seq_ptr < charsize:
					now_dict = {}
					now_file = open("./comb/" + sequence[seq_ptr] + ".pickle", "rb")

					try:
						now_dict = pickle.load(file)
					except EOFError:
						now_dict = {}
					now_file = open("./comb/" + sequence[seq_ptr] + ".pickle", "wb")

			now_dict[key] = start_dict[key]
		start_dict = {}
		continue

	# Loading in the next file to be merged
	newfile = open(file_path, "rb")
	try:
		new_dict = pickle.load(file)
	except EOFError:
		new_dict = {}

	set_B = []
	for key in new_dict.keys():
		set_B.append(key)
	set_B.sort()
	
	len_A = len(set_A)
	len_B = len(set_B)
	
	ptr_A = ptr_B = 0

	now_file = open("./comb/0" + ".pickle", "rb")
	try:
		now_dict = pickle.load(file)
	except EOFError:
		now_dict = {}
	now_file = open("./comb/0" + ".pickle", "wb")

	seq_ptr = 0
	update_set = []

	while(seq_ptr < charsize):
		if ptr_B >= len_B:
			break

		if ptr_A >= len_A:
			while(ptr_B < len_B):
				if set_B[ptr_B][0] != sequence[seq_ptr]:
					pickle.dump(now_dict, now_file)
					now_file.close()

					while seq_ptr < charsize and set_B[ptr_B][0] > sequence[seq_ptr]:
						seq_ptr += 1
					
					if seq_ptr < charsize:
						now_dict = {}
						now_file = open("./comb/" + sequence[seq_ptr] + ".pickle", "rb")
						try:
							now_dict = pickle.load(file)
						except EOFError:
							now_dict = {}
						now_file = open("./comb/" + sequence[seq_ptr] + ".pickle", "wb")

				now_dict[set_B[ptr_B]] = new_dict[set_B[ptr_B]]
				update_set.append(set_B[ptr_B])
				ptr_B += 1
			break

		if set_A[ptr_A] == set_B[ptr_B]:
			# combine

			if set_B[ptr_B][0] != sequence[seq_ptr]:
				pickle.dump(now_dict, now_file)

				while seq_ptr < charsize and set_B[ptr_B][0] > sequence[seq_ptr]:
					seq_ptr += 1
				
				if seq_ptr < charsize:
					now_dict = {}
					now_file = open("./comb/" + sequence[seq_ptr] + ".pickle", "rb")
					try:
						now_dict = pickle.load(file)
					except EOFError:
						now_dict = {}
					now_file = open("./comb/" + sequence[seq_ptr] + ".pickle", "wb")

			if set_A[ptr_A] not in now_dict.keys():
				print(str(set_A[ptr_A]) + " Not in A")

			if set_A[ptr_A] not in new_dict.keys():
				print(str(set_A[ptr_A]) + " Not in B")

			for idx in range(6):
				now_dict[set_A[ptr_A]][idx] += new_dict[set_B[ptr_B]][idx]
				now_dict[set_A[ptr_A]][6][idx] += new_dict[set_B[ptr_B]][6][idx]

			ptr_A += 1
			ptr_B += 1

		elif set_A[ptr_A] > set_B[ptr_B]:
			if set_B[ptr_B][0] != sequence[seq_ptr]:
				pickle.dump(now_dict, now_file)

				while seq_ptr < charsize and set_B[ptr_B][0] > sequence[seq_ptr]:
					seq_ptr += 1
				
				if seq_ptr < charsize:
					now_dict = {}
					now_file = open("./comb/" + sequence[seq_ptr] + ".pickle", "rb")
					try:
						now_dict = pickle.load(file)
					except EOFError:
						now_dict = {}
					now_file = open("./comb/" + sequence[seq_ptr] + ".pickle", "wb")

			now_dict[set_B[ptr_B]] = new_dict[set_B[ptr_B]]
			update_set.append(set_B[ptr_B])
			ptr_B += 1

		elif set_B[ptr_B] > set_A[ptr_A]:
			ptr_A += 1

	for elem in update_set:
		set_A.append(elem)