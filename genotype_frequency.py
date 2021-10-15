# coding=utf-8
# 统计三种基因型频率及MAF

import os,sys
import numpy as np

raw_file_name = sys.argv[1]

os.system(f"sed 's/\<NA\>/3/g' {raw_file_name} > temp.raw") # 改为精准匹配

raw_file = open("temp.raw",'r')
raw_file_title = raw_file.readline().split() #剔除标题
title_list = []
for i in raw_file_title[6:]:
    title_list.append(i[:-2]) # snp 名称列表
    
raw_list=[]
for i in raw_file:
    f = i.split()
    raw_list.append(f[6:])
    
raw_file.close()

array1 = np.array(raw_list, dtype=np.int8)

# 统计三种基因型数据

p_array = (array1==2).sum(axis=0) # 按列求和, 较小等位基因的纯合子
h_array = (array1==1).sum(axis=0) # 按列求和
r_array = (array1==0).sum(axis=0) # 按列求和

p_rate = p_array/(p_array+h_array+r_array)
h_rate = h_array/(p_array+h_array+r_array)
r_rate = r_array/(p_array+h_array+r_array)

maf_rate = (2*p_rate + h_rate)/2

# 写入结果文件
out_file = open(sys.argv[2],'w')

snp_num = len(title_list)
for i in range(snp_num):
    out_file.write(title_list[i]+"\t"+str(p_rate[i])+"\t"+str(h_rate[i])+"\t"+str(r_rate[i])+"\t"+str(maf_rate[i])+"\n")

out_file.close()

# 删除中间文件

os.system("rm temp.raw")
