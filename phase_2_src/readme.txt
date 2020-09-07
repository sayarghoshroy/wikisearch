Index Creation Code is split into index.py and merge.py.
index.sh is used to build the index

Primary files from each dump is processed into temp_dicts. 34 partial indices from temp_dict are considered to build the complete index.

search.py contains necessary functions to run queries and populate queries_op.txt

To Search, Use:
bash search.sh queries.txt

Note: For now, K will be set within 1 and 100.
