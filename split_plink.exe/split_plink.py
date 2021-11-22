#!/mnt/data/zhouziwen/bin/miniConda/miniconda3/bin/python
# coding=utf-8
# 按照一个芯片号文件拆分plink文件
# 如果芯片号文件只有一列，默认输出文件为 split_plink.ped split_plink.map
# windows 下 cp 改为 copy ; 新增一个输入文件，剔除芯片号文件。

import os,sys
from collections import defaultdict

plink_prefix = "all" # plink文件前缀
split_file = open("split_plink.txt",'r') # 拆分信息文件，无标题，一列（芯片号）或两列（芯片号-分类名）
exclude_file = open("exclude_chipid.txt",'r') # 剔除芯片号文件。
plink_file = open(f"{plink_prefix}.ped",'r')
map_file_name = f"{plink_prefix}.map"

error_status = False # 错误逻辑值

# 需要剔除的芯片号
exclude_set = set()

j = 0
for i in exclude_file:
    j += 1
    f = i.split()
    if (len(f) >= 1):
        exclude_set.add(f[0])
    else:
        print(f"Error: {j} row in exclude_chipid.txt has 0 columns\n")
        error_status = True

# 遍历芯片文件
set2=set()
dick2 = {}

for i in plink_file:
    f = i.split()
    if f[1] not in set2:
        set2.add(f[1])
        dick2[f[1]] = i # 芯片号：芯片信息的行
    else:
        print(f"Error: duplicated chipid {f[1]} in all.ped\n")
        error_status = True

# 遍历 split_plink.txt 文件
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
                if f[0] not in exclude_set: # 不在需要剔除的个体中
                    if f[0] in dick2:
                        dick["split_plink"].append(f[0]) # 品种：芯片号的列表
                    else:
                        print(f"Error: {f[0]} in split_plink.txt not in all.ped\n")
                        error_status = True
            else:
                print(f"Error: duplicated chipid {f[0]} in split_plink.txt\n")
                error_status = True
        else:
            print(f"Error:{j} row in split_plink.txt is not 1 columns\n")
            error_status = True
elif column_num == 2:
    for i in split_file:
        j += 1
        f = i.split()
        if len(f) == 2:
            if f[0] not in set1:
                set1.add(f[0])
                if f[0] not in exclude_set: # 不在需要剔除的个体中
                    if f[0] in dick2:
                        dick[f[1]].append(f[0]) # 品种：芯片号的列表
                    else:
                        print(f"Error: {f[0]} in split_plink.txt not in all.ped\n")
                        error_status = True
            else:
                print(f"Error: duplicated chipid {f[0]} in split_plink.txt\n")
                error_status = True
        else:
            print(f"Error:{j} row in split_plink.txt is not 2 columns\n")
            error_status = True
else:
    print(f"Error: first row in split_plink.txt is not 1 or 2 columns\n")
    error_status = True
        

if error_status:
    print("Please check your data again")
    input("Press any key to exit.")
    sys.exit(1)


for i in dick: # 所有品种
    # 复制map文件
    os.system(f"copy {map_file_name} {i}.map") 
    out_plink_list = []
    for i2 in dick[i]:
        out_plink_list.append(dick2[i2])
    # 生成plink 文件
    out_plink_file = open(f"{i}.ped",'w')
    out_plink_file.writelines(out_plink_list)
    out_plink_file.close()

split_file.close()
plink_file.close()
exclude_file.close()


print("Congratulation: split plink file success")
input("Press any key to exit.")
