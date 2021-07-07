# coding=utf-8
# 使用自助法计算maf的bias和 se
# 临时文件为 temp.ped/map

import os,sys
import numpy as np

plink_prefix = sys.argv[1] # plink文件前缀
yuan_frq_file = open(sys.argv[2],'r') # 原始的 freq 文件
run_times = int(sys.argv[3]) # 重复抽样次数，如 1000
out_file = open(sys.argv[4],'w') # 输出文件，在原始的freq文件上新增3列。


os.system(f"cp {plink_prefix}.map temp.map") #复制map文件

# 提取原ped，map信息
list1 = []
yuan_ped_file = open(f"{plink_prefix}.ped",'r')
yuan_map_file = open(f"{plink_prefix}.map",'r')
sample_num = 0
for i in yuan_ped_file:
    f = i.split()
    sample_num += 1
    list1.append('\t'.join(f[2:])) #第三列之后的数据

snp_num = 0
for i in yuan_map_file:
    snp_num += 1
    
print(f"Sample num：{sample_num}\n")
print(f"SNP num：{snp_num}\n")

yuan_ped_file.close()
yuan_map_file.close()

# 提取原始的freq文件信息

# 重复抽样，得到maf
total_maf_list = []
for j in range(1, run_times+1):
    random_array =  np.random.choice(sample_num,sample_num) # 有放回抽样
    # 生成新的ped文件
    new_ped_file = open("temp.ped",'w')
    for i in random_array:
        new_ped_file.write('0'+'\t'+str(j)+'\t'+list1[i]+'\n')
    new_ped_file.close()
    # 统计maf
    os.system("plink --allow-extra-chr --chr-set 95 --file temp --freq --out temp > /dev/null")
    frq_file = open("temp.frq",'r')
    title = frq_file.readline() # 去除标题
    maf_list = []
    for i in frq_file:
        f = i.split()
        if f[4] == 'NA': #如果maf为NA，替换为0，此时缺失率为1
            f[4] = '0'
        maf_list.append(f[4])
    frq_file.close()
    # 查看maf结果是否正常
    if len(maf_list) != snp_num:
        print(f"Error: snp num in temp.frq is not same with {plink_prefix}.map\n")
        break
        sys.exit(1)
    else:
        total_maf_list.append('\t'.join(maf_list))
        
# 统计所有maf结果的均值与标准误
# 每一行是一次抽样，每一列是一个SNP
array1 = np.genfromtxt(total_maf_list, dtype=np.float16, missing_values="NA", filling_values=0)

snp_mean_list = np.mean(array1, axis=0)
snp_se_list = np.std(array1, axis=0)

# 合并结果
title = yuan_frq_file.readline().split() # 去除标题
out_file.write('\t'.join(title)+'\t'+'bootstrap_mean'+'\t'+'bootstrap_bias'+'\t'+'bootstrap_se'+'\n')

j = 0
for i in yuan_frq_file:
    f = i.split()
    if f[4] == 'NA': #如果maf为NA，替换为0，此时缺失率为1
        f[4] = '0'
    yuan_maf = float(f[4])
    bias = snp_mean_list[j] - yuan_maf # bias = 自助法均值 - 真值
    out_file.write('\t'.join(f)+'\t'+str(snp_mean_list[j])+'\t'+str(bias)+'\t'+str(snp_se_list[j])+'\n')
    j += 1


yuan_frq_file.close()
out_file.close()
    