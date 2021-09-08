# coding=utf-8
# 转换基因型数据格式

import os,sys
import pandas as pd

in_excel_name = sys.argv[1] # 第一个参数为Excel文件名
map_file_name = sys.argv[2] # 第二个参数为原始map文件名
out_prefix = sys.argv[3] # 第三个参数为输出的plink文件前缀

# 使用pandas读入 excel
in_file = pd.read_excel(in_excel_name, 'Sheet1')

# 缺失值替换为 "00"
in_file.fillna("00", inplace=True)

# 将第一列和其他列切分开
id_series = in_file.iloc[:,0]
snp_dataframe = in_file.iloc[:,1:]

# 如果基因型为一个字符，则为纯合子，改为两个字符，如 A 改为 AA
row_num = snp_dataframe.shape[0]
col_num = snp_dataframe.shape[1]

for i in range(row_num):
    for j in range(col_num):
        if len(snp_dataframe.iloc[i,j]) == 1: # 判断字符串长度
            snp_dataframe.iloc[i,j] = snp_dataframe.iloc[i,j] * 2

# 生成compound格式的ped格式
# 这里稍微麻烦一点，因为 pandas 合并数据框默认是按照行索引
# 首先值均为0的series，使用 pd.concat() 函数进行拼接

s1 = pd.Series(['0']*row_num)
compound_ped = pd.concat([s1,id_series,s1,s1,s1,s1,snp_dataframe], axis=1)

# 保存为文件，行索引和列标题均不要
compound_ped.to_csv("compound.ped", index=False, header=False, sep=" ")

# 提取map文件
# 首先提取snp名称
snp_list = list(snp_dataframe)

raw_map_file = open(map_file_name,'r')
out_map_file = open("compound.map",'w')

map_dick = {}
for i in raw_map_file:
    f = i.split()
    map_dick[f[1]] = i # snp名称：map文件的整行内容
    
for i in snp_list:
    if i in map_dick:
        out_map_file.write(map_dick[i])
    else:
        print(f"Error: snp {i} in {in_excel_name} but not in {map_file_name}\n")
        sys.exit(1)

raw_map_file.close()
out_map_file.close()

#最后用plink软件转化为正常的plink格式的文件
os.system(f"plink --allow-extra-chr --file compound --compound-genotypes --recode --out {out_prefix} > /dev/null")





