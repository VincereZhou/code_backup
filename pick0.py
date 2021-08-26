#!/mnt/data/zhouziwen/bin/miniConda/miniconda3/bin/python
#coding=utf-8
import sys 
id = open(sys.argv[1],'r')
bigfile = open(sys.argv[2],'r')
outfile = open(sys.argv[3],'w')


set1 = set();dick={}

for i in bigfile:
    f = i.split()
    if f[0] not in dick:
        dick[f[0]] = i
    else:
        print(f"Error: duplicated id {f[0]} in {sys.argv[2]}\n")
        sys.exit(1)
        
not_in_num = 0
duplicate_id_num = 0
not_in_list = []

for i in id:
    f = i.split()
    if f[0] not in set1: #id文件去重
        set1.add(f[0])
        if f[0] in dick:
            outfile.write(dick[f[0]])
        else:
            not_in_num += 1
            not_in_list.append(f[0])
    else:
        duplicate_id_num += 1
        
if duplicate_id_num > 0:
    print(f"Warning: {duplicate_id_num} duplicated id in {sys.argv[1]}\n")

if not_in_num > 0:
    print(f"Warning: {not_in_num} id not in {sys.argv[2]}\n")
    not_in_file = open('pick0_not_in_id.txt','w')
    for i in not_in_list:
        not_in_file.write(f"{i}\n")
    not_in_file.close()
      
id.close()
bigfile.close()
outfile.close()
