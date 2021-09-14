#!/mnt/data/zhouziwen/bin/miniConda/miniconda3/bin/python
#coding=utf-8
#基于两个plink数据进行共同样本共同SNP之间的基因型比对
#比对两个plink时，需要先统一map中的SNP名称，以及 plink 文件中的样本名称。


import argparse,os,sys,time,math
import numpy as np

np.seterr(divide='ignore',invalid='ignore')
parser = argparse.ArgumentParser(prog="compare_two_plinks", description='compare common samples and common SNPs in two plink files')

# 添加参数步骤，如果不提供参数，那个参数就是 None
parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
parser.add_argument("--plink1", required=True, 
    help='''the first plink file's prefix, plink software must have been installed and added to the environment variables''')
parser.add_argument("--plink2", required=True, 
    help='''the second plink file's prefix, plink software must have been installed and added to the environment variables''')
parser.add_argument("--exclude-miss", required=False, default="yes",
    help='''when compare pairs, exclude missing bases or not ,must be yes or no, default is yes. 
            ''')
parser.add_argument("--save-temp", required=False, default="no",
    help='''save temporary files or not ,must be yes or no, default is no. 
            ''')
parser.add_argument("--out-prefix", required=False, default="cmp_two_plinks",
    help='''out file's prefix, default is "cmp_two_plinks",  two output files'suffix are  "_sample.txt" and "_snp.txt". 
            ''')

args = parser.parse_args()


#打印软件版本
print(" ---------------------------------------------")
print("|             compare_two_plinks.py           |")
print("|                                             |")
print("|             2021 - Version 1.0              |")
print("|          (lase update: Sept 03, 2021)       |")
print("|             Compass, Beijing                |")
print(" ---------------------------------------------\n")

#打印开始时间
begin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("Start time: {}\n".format(begin_time)) 


#打印所有参数        
print("Arguments\n")
print("  --plink1 {}\n".format(args.plink1))
print("  --plink2 {}\n".format(args.plink2))
print("  --exclude-miss {}\n".format(args.exclude_miss))
print("  --save-temp {}\n".format(args.save_temp))
print("  --out-prefix {}\n".format(args.out_prefix))

#检验参数
legal_argument_set = set(["yes", "no"])

# 判断输入文件是否存在且非空
def Judge_file(file_path):
    import os
    if os.path.exists(file_path):
        if os.path.getsize(file_path):
            return True
    return False


if not Judge_file(f"{args.plink1}.ped"):
    print(f"Error: {args.plink1}.ped not exists or is empty file\n\n")
    sys.exit(1)

if not Judge_file(f"{args.plink1}.map"):
    print(f"Error: {args.plink1}.map not exists or is empty file\n\n")
    sys.exit(1)

if not Judge_file(f"{args.plink2}.ped"):
    print(f"Error: {args.plink2}.ped not exists or is empty file\n\n")
    sys.exit(1)

if not Judge_file(f"{args.plink2}.map"):
    print(f"Error: {args.plink2}.map not exists or is empty file\n\n")
    sys.exit(1)

if args.exclude_miss not in legal_argument_set:
    print("Error: illegal input, --exclude-miss must be yes or no\n\n")
    sys.exit(1)
    
if args.save_temp not in legal_argument_set:
    print("Error: illegal input, --save-temp must be yes or no\n\n")
    sys.exit(1)

plink_prefix1 = args.plink1
plink_prefix2 = args.plink2

# 复制 map
os.system(f"cp {plink_prefix1}.map {plink_prefix1}_temp.map")
os.system(f"cp {plink_prefix2}.map {plink_prefix2}_temp.map")

# 重新生成plink 文件
ped1 = open(f"{plink_prefix1}.ped",'r')
map1 = open(f"{plink_prefix1}.map",'r')

ped2 = open(f"{plink_prefix2}.ped",'r')
map2 = open(f"{plink_prefix2}.map",'r')

re_ped1 = open(f"{plink_prefix1}_temp.ped",'w')
re_ped2 = open(f"{plink_prefix2}_temp.ped",'w')
common_snp_file = open(f'{plink_prefix1}_{plink_prefix2}_common_snp_temp.txt','w')

error_status = False 

#提取共同位点，只看SNP名称
j = 0
snp1_set = set()  # 第一个map的SNP名称
temp_line_set = set()
for i in map1:
    j += 1
    f = i.split()
    if (len(f) == 4):
        if '\t'.join(f) not in temp_line_set:
            temp_line_set.add('\t'.join(f))
            if f[1] not in snp1_set:
                snp1_set.add(f[1])
            else:
                print(f"Error: duplicated id {f[1]} in different rows in {plink_prefix1}.map\n") 
                error_status = True
        else:
            print(f"Error: duplicted row {j} in {plink_prefix1}.map\n")
            error_status = True

    else:
        print(f"Error: {j} row in {plink_prefix1}.map has less or more than 4 coloums\n")
        error_status = True

j = 0
temp_id_set = set()
temp_line_set = set()
common_snp_num = 0
for i in map2:
    j += 1
    f = i.split()
    if (len(f) == 4):
        if '\t'.join(f) not in temp_line_set:
            temp_line_set.add('\t'.join(f))
            if f[1] not in temp_id_set:
                temp_id_set.add(f[1])
                if f[1] in snp1_set:
                    common_snp_num += 1
                    common_snp_file.write(f[1]+'\n')
            else:
                print(f"Error: duplicated id {f[1]} in different rows in {plink_prefix2}.map\n") 
                error_status = True
        else:
            print(f"Error: duplicted row {j} in {plink_prefix2}.map\n")
            error_status = True

    else:
        print(f"Error: {j} row in {plink_prefix2}.map has less or more than 4 coloums\n")
        error_status = True

if common_snp_num == 0:
    print("Error: no common SNP in two plink files")
    error_status = True
else:
    print("\nNumber of common SNPs in two plink files: {}\n".format(common_snp_num))
   
#重命名
# newid_dick = {} #chipid/sampleid:newid
# sampleid_dick = {} #newid:chipid/sampleid


#ped重编码为数字(1-indexed)
# 第一次结果不对
# 我懂了，plink 的 merge 命令会重新排列样本顺序，所以不是按照ped1,ped2的顺序

# 修改程序，严格按照想要的总文件的顺序，重编码芯片号。然后合并时先合并ped2,再合并ped1
# 重编码 ped 文件，第一列家系号替换为0，个体号重编码为数字。因为 merge 命令会按照 家系号 + 个体号进行排序。

ped1_dick = {}
for i in ped1:
    f = i.split()
    if f[1] not in ped1_dick:
        ped1_dick[f[1]] = '\t'.join(f[2:])+'\n'
    else:
        error_status = True
        print(f"Error: duplicated chip id {f[1]} in {plink_prefix1}.ped\n")

        
sample1_num = len(ped1_dick)

print("Number of records present in plink1 file: {}\n".format(sample1_num))

common_sample_list = []
common_sample_num = 0

j=0
temp_id_set = set()
for i in ped2:
    j += 1
    f = i.split()
    if f[1] not in temp_id_set:
        temp_id_set.add(f[1])
        if f[1] in ped1_dick:
            common_sample_num += 1
            common_sample_list.append(f[1]) #两个样本重复样的芯片号
            re_ped2.write('0'+'\t'+str(j)+'\t'+'\t'.join(f[2:])+'\n')
    else:
        error_status = True
        print(f"Error: duplicated chip id {f[1]} in {plink_prefix2}.ped\n")

sample2_num = j
print("Number of records present in plink2 file: {}\n".format(sample2_num))

if common_sample_num == 0:
    print("Error: no common sample in two plink files")
    error_status = True
else:
    print("Number of common samples in two plink files: {}\n".format(common_sample_num))

## re_ped1 重排个体顺序，使得与 re_ped2 一致
## 这里的 j 沿着上面递增，没有初始化 j = 0

for i in common_sample_list:
    j += 1
    re_ped1.write('0'+'\t'+str(j)+'\t'+ped1_dick[i])

ped1.close()
map1.close()
ped2.close()
map2.close()
re_ped1.close()
re_ped2.close()
common_snp_file.close()


# 如果读取文件过程中出现错误退出
if error_status:
    print("Please check your file again!")
    sys.exit(1)


# extract merge recodeA
# 合并文件是第二个plink文件的共同样本在上方，第一个plink的共同样本在下方，二者样本的顺序一致。

merge_status = os.system(f"plink --allow-extra-chr --chr-set 95 --file {plink_prefix2}_temp --merge {plink_prefix1}_temp --extract {plink_prefix1}_{plink_prefix2}_common_snp_temp.txt --recodeA --out {plink_prefix1}_{plink_prefix2}_merge_temp > /dev/null")

if merge_status != 0:
    print("Error in merge two plink data\n")
    print("Maybe some common SNP from Complementary strands, check your data again")
    sys.exit(1)

#raw文件处理
os.system(f"sed 's/NA/3/g' {plink_prefix1}_{plink_prefix2}_merge_temp.raw > {plink_prefix1}_{plink_prefix2}_merge_temp_sed.raw")
raw_file = open(f"{plink_prefix1}_{plink_prefix2}_merge_temp_sed.raw",'r')
out_sample_file = open(f"{args.out_prefix}_sample.txt",'w')
out_snp_file = open(f"{args.out_prefix}_snp.txt",'w')

# 处理标题，得到 SNP 名称
snp_list = []
title = raw_file.readline().split() #剔除标题
for i in title[6:]:
    snp_name = i[:-2]
    snp_list.append(snp_name) # SNP名称的列表

raw_list=[]
for i in raw_file:
    f = i.split()
    raw_list.append(f[6:])

array1 = np.array(raw_list, dtype=np.int8)

total_sample_num = array1.shape[0]
snp_num = array1.shape[1]

print("Number of records present in merged ped file: {}\n".format(total_sample_num))
print("Number of SNPs in merged plink files: {}\n".format(snp_num))

if (total_sample_num != (2*common_sample_num)):
    print("Error: total samples number of merged plink file is not 2 fold of common samples in two plink files\n")
    sys.exit(1)

#计算不一致率
out_sample_list = []
out_snp_list = []
  
if args.exclude_miss == 'yes':
    for i in range(snp_num):
        first_index = range(0,common_sample_num)
        second_index = range(common_sample_num,total_sample_num)
        v1 = array1[first_index,i]
        v2 = array1[second_index,i]
        non_miss_index = np.where((v1!=3) & (v2!=3))
        total_num = non_miss_index[0].shape[0]
        v1_new = v1[non_miss_index]
        v2_new = v2[non_miss_index]
        no_match_num = np.count_nonzero(v1_new!=v2_new)
        if total_num > 0:
            no_match_rate = no_match_num/total_num
        else:
            no_match_rate = 0
        out_snp_list.append([snp_list[i],f"{no_match_num}",f"{total_num}",f"{no_match_rate:.4f}"])
    for i in range(len(common_sample_list)):
        first_index = i
        second_index = i+common_sample_num
        v1 = array1[first_index,:]
        v2 = array1[second_index,:]
        non_miss_index = np.where((v1!=3) & (v2!=3))
        total_num = non_miss_index[0].shape[0]
        v1_new = v1[non_miss_index]
        v2_new = v2[non_miss_index]
        no_match_num = np.count_nonzero(v1_new!=v2_new)
        if total_num > 0:
            no_match_rate = no_match_num/total_num
        else:
            no_match_rate = 0
        out_sample_list.append([common_sample_list[i],f"{no_match_num}",f"{total_num}",f"{no_match_rate:.4f}"])
        
elif args.exclude_miss == 'no':
    for i in range(snp_num):
        first_index = range(0,common_sample_num)
        second_index = range(common_sample_num,total_sample_num)
        v1 = array1[first_index,i]
        v2 = array1[second_index,i]
        total_num = common_sample_num
        no_match_num = np.count_nonzero(v1!=v2)
        no_match_rate = no_match_num/total_num
        out_snp_list.append([snp_list[i],f"{no_match_num}",f"{total_num}",f"{no_match_rate:.4f}"])
    for i in range(len(common_sample_list)):
        first_index = i
        second_index = i+common_sample_num
        v1 = array1[first_index,:]
        v2 = array1[second_index,:]
        total_num = snp_num
        no_match_num = np.count_nonzero(v1!=v2)
        no_match_rate = no_match_num/total_num
        out_sample_list.append([common_sample_list[i],f"{no_match_num}",f"{total_num}",f"{no_match_rate:.4f}"])



sorted_out_snp_list = sorted(out_snp_list, key = lambda s:float(s[3]), reverse = True) #不一致率从大到小
sorted_out_sample_list = sorted(out_sample_list, key = lambda s:float(s[3]), reverse = True) #不一致率从大到小

unconsistent_snp_num = 0 # 不一致的SNP数目
unconsistent_sample_num = 0 # 不一致的样本数目

for i in sorted_out_snp_list:
    out_snp_file.write('\t'.join(i)+'\n')
    if int(i[1]) > 0:
        unconsistent_snp_num += 1

for i in sorted_out_sample_list:
    out_sample_file.write('\t'.join(i)+'\n')
    if int(i[1]) > 0:
        unconsistent_sample_num += 1

print(f"unconsistent sample number: {unconsistent_sample_num}\n")
print(f"unconsistent  snp   number: {unconsistent_snp_num}\n")


raw_file.close()
out_sample_file.close()
out_snp_file.close()
    
#删除中间文件
if args.save_temp == "yes":
    pass
elif args.save_temp == "no":
    os.system(f"rm *temp*")


end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("Finish time: {}\n".format(end_time)) 

