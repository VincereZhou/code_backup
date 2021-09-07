#!/mnt/data/zhouziwen/bin/miniConda/miniconda3/bin/python
# coding=utf-8
# 按照一个芯片号文件拆分plink文件
# 如果芯片号文件只有一列，默认输出文件为 split_plink.ped split_plink.map

import os,sys
from collections import defaultdict

plink_prefix = sys.argv[1] # plink文件前缀
split_file = open(sys.argv[2],'r') # 拆分信息文件，无标题，一列（芯片号）或两列（芯片号-分类名）
plink_file = open(f"{plink_prefix}.ped",'r')
map_file_name = f"{plink_prefix}.map"

column_num = len(split_file.readline().split())
split_file.seek(0)

set1 = set()
dick = defaultdict(list)

j=0
if column_num == 1: # 只有一列
    for i in split_file:
        j += 1
        f = i.split()
        if len(f) == 1:
            if f[0] not in set1:
                set1.add(f[0])
                dick["split_plink"].append(f[0]) # 品种：芯片号的列表
            else:
                print(f"Error: duplicated chipid {f[0]} in {sys.argv[1]}\n")
                sys.exit(1)
        else:
            print(f"Error:{j} row in {sys.argv[1]} is not 1 columns\n")
            sys.exit(1)
elif column_num == 2:
    for i in split_file:
        j += 1
        f = i.split()
        if len(f) == 2:
            if f[0] not in set1:
                set1.add(f[0])
                dick[f[1]].append(f[0]) # 品种：芯片号的列表
            else:
                print(f"Error: duplicated chipid {f[0]} in {sys.argv[1]}\n")
                sys.exit(1)
        else:
            print(f"Error:{j} row in {sys.argv[1]} is not 2 columns\n")
            sys.exit(1)
else:
    print(f"Error: first row in {sys.argv[1]} is not 1 or 2 columns\n")
    sys.exit(1)
        
        
set2=set()
dick2 = {}

for i in plink_file:
    f = i.split()
    if f[1] not in set2:
        set2.add(f[1])
        dick2[f[1]] = i # 芯片号：芯片信息的行
    else:
        print(f"Error: duplicated chipid {f[1]} in {sys.argv[2]}.ped\n")
        sys.exit(1)
        
for i in dick: # 所有品种
    # 复制map文件
    os.system(f"cp {map_file_name} {i}.map") 
    out_plink_list = []
    for i2 in dick[i]:
        # 如果芯片号不在plink文件中报错
        if i2 not in dick2:
            print(f"Error: {i2} in {sys.argv[1]} not in {sys.argv[2]}\n")
            sys.exit(1)
        out_plink_list.append(dick2[i2])
    # 生成plink 文件
    out_plink_file = open(f"{i}.ped",'w')
    out_plink_file.writelines(out_plink_list)
    out_plink_file.close()

split_file.close()
plink_file.close()
