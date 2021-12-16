# coding=utf-8
# 提供的系谱文件必须保证父母子均有基因型，并且最好亲子对检验均为正确，计算每个 trios 的孟德尔错误率。
# 中间结果文件 all_pairs_id.txt all_pairs.raw

import os,sys,subprocess
import pandas as pd
import numpy as np
from collections import Counter

np.seterr(divide='ignore',invalid='ignore')

raw_file_name = sys.argv[1] # raw 文件（事先提取需要的SNP，芯片号替换为个体号），第二列为真实个体号
true_pedigree_file = open(sys.argv[2],'r') # 真实系谱结果
out_file = open(sys.argv[3],'w') # 最终的结果文件

error_status = False # 错误逻辑值

# 遍历raw文件，生成基因型数组
raw_file = subprocess.run(["sed", "s/\<NA\>/3/g", raw_file_name], stdout = subprocess.PIPE).stdout.decode('utf-8').splitlines()

j = 0 
temp_id_set = set()
raw_id_list = []
raw_list=[]
raw_id_index_dict = {}
for i in raw_file[1:]:
    f = i.split()
    if f[1] not in temp_id_set: 
        temp_id_set.add(f[1])
        raw_id_list.append(f[1]) # raw 文件中的个体号
        raw_id_index_dict[f[1]] = j # 个体号：序号
        raw_list.append(f[6:])
    else:
        print(f"Error: duplicated id {f[1]} in {raw_file_name}\n")
        error_status = True
    j += 1

raw_id_set = temp_id_set # raw 文件中的个体号组成的集合

del raw_file

# array1 没有剔除第一类重复样, 基因型改为 1 2 3 0(缺失)
array1 = np.array(raw_list, dtype=np.int8)

array1 += 1
array1[array1==4] = 0

# 统计样本数目和SNP数目
sample_num = array1.shape[0]
snp_num = array1.shape[1]


# 遍历系谱文件
j = 0
trios_id_list = [] # trios 个体号列表
for i in true_pedigree_file:
    j += 1
    f = i.split()
    if len(f) >= 3:
        if (f[0] in raw_id_set) and (f[1] in raw_id_set) and (f[2] in raw_id_set): # 如果真实系谱中的个体有基因型
            trios_id_list.append(f) # 系谱文件所有列
        else:
            print(f"Warnning: {j} row's id or parent in {sys.argv[2]} not in {sys.argv[1]}\n")
    else:
        print(f"Error: {j} row in {sys.argv[2]} is less than 3 columns\n")
        error_status = True

# 输入文件有问题，中止
if error_status:
    sys.exit(1)

# 计算 trios 的孟德尔错误率
check_trios_list = []
for f in trios_id_list:
    id_index = raw_id_index_dict[f[0]]
    id_array = array1[id_index].copy() # 个体基因型改为 5 7 8
    id_array[id_array == 1] = 5
    id_array[id_array == 2] = 7
    id_array[id_array == 3] = 8
    parent1_index = raw_id_index_dict[f[1]]
    parent2_index = raw_id_index_dict[f[2]]
    parent1_array = array1[parent1_index] # 父母基因型不改变
    parent2_array = array1[parent2_index]
    # 计算父母子三者的元素乘积
    product_array = id_array * parent1_array * parent2_array
    # 调用 Counter() 统计 19 个可能的值的出现次数
    product_count = Counter(product_array)
    total_snp_num = snp_num - product_count[0] # 位点总数中剔除缺失位点
    error_snp_num = product_count[7] + product_count[8] + product_count[15] + product_count[16] + product_count[24] + product_count[30] + product_count[45] + product_count[63]
    if total_snp_num == 0: # 避免 0/0
        error_snp_prob = 0
    else:
        error_snp_prob = error_snp_num/total_snp_num
    check_trios_list.append(f+[str(error_snp_num), str(total_snp_num), str("{:.4f}".format(error_snp_prob))]) 

check_trios_list_sorted = sorted(check_trios_list, key =lambda x:float(x[-1]), reverse=True)


for i in check_trios_list_sorted:
    out_file.write('\t'.join(i)+'\n')

true_pedigree_file.close()
out_file.close()
