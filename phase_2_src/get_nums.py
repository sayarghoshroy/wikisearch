import os
import sys
import _pickle as pickle
import lzma

path = '/scratch/sayar/new_comb/'
dirs = os.listdir(path)
cnt = 0
filecnt = 0
for filename in dirs:
	filecnt += 1
	if filecnt % 10000 == 0:
		print(filecnt)
	with lzma.open(path + filename, "rb") as f:
		dickie = pickle.load(f)
		cnt += len(dickie.keys())

print("Number of Tokens: " + str(cnt))
