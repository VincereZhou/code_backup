#!/mnt/data/zhouziwen/bin/miniConda/miniconda3/bin/python
#coding=utf-8
#基于plink数据进行样本间基因型比对
#需要先统一map中的SNP名称和样本名称

import argparse,os,sys,time,math
import numpy as np

np.seterr(divide='ignore',invalid='ignore')
parser = argparse.ArgumentParser(prog="compare_samples", description='compare samples in the genotype files based on SNP markers')

# 添加参数步骤，如果不提供参数，那个参数就是 None
parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.3')
parser.add_argument("--plink1", required=True, 
    help='''the first plink file's prefix, plink software must have been installed and added to the environment variables''')
parser.add_argument("--plink2", required=True, 
    help='''the second plink file's prefix, plink software must have been installed and added to the environment variables''')
parser.add_argument("--chipid1", required=False, 
    help='''first id file corresponding to the plink file. Two columns are required.
        the first column is the chip id, the second column is the sample id''')
parser.add_argument("--chipid2", required=False, 
    help='''second id file corresponding to the plink file. Two columns are required, 
        the first column is the chip id, the second column is the sample id''')
parser.add_argument("--cmp-all", required=False, default="no",
    help='''compare all pairs or not ,must be yes or no, default is no. 
            if setted to yes, then argument --dup-prob is ignored.''')
parser.add_argument("--exclude-miss", required=False, default="yes",
    help='''when compare pairs, exclude missing bases or not ,must be yes or no, default is yes. 
            ''')
parser.add_argument("--save-temp", required=False, default="no",
    help='''save temporary files or not ,must be yes or no, default is no. 
            ''')
parser.add_argument("--out", required=False, default="cmp_two_plinks.txt",
    help='''out file name, default is "cmp_two_plinks.txt". 
            ''')


args = parser.parse_args()

#打印软件版本
print(" ---------------------------------------------")
print("|             compare_samples.py              |")
print("|                                             |")
print("|             2021 - Version 1.3              |")
print("|          (lase update: Aug 08, 2021)        |")
print("|             Compass, Beijing                |")
print(" ---------------------------------------------\n")

#打印开始时间
begin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("Start time: {}\n".format(begin_time)) 


#打印所有参数        
print("Arguments\n")
print("  --plink1 {}\n".format(args.plink1))
print("  --plink2 {}\n".format(args.plink2))
print("  --chipid1 {}\n".format(args.chipid1))
print("  --chipid2 {}\n".format(args.chipid2))
print("  --cmp-all {}\n".format(args.cmp_all))
print("  --exclude-miss {}\n".format(args.exclude_miss))
print("  --save-temp {}\n".format(args.save_temp))
print("  --out {}\n".format(args.out))

#检验参数
legal_argument_set = set(["yes", "no"])

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False

if not os.path.exists(f"{args.plink1}.ped"):
    print(f"Error: not exist {args.plink1}.ped\n\n")
    sys.exit(1)

if not os.path.exists(f"{args.plink1}.map"):
    print(f"Error: not exist {args.plink1}.map\n\n")
    sys.exit(1)

if args.chipid1 is not None:
    if not os.path.exists(f"{args.chipid1}"):
        print(f"Error: not exist {args.chipid1}\n\n")
        sys.exit(1)

if not os.path.exists(f"{args.plink2}.ped"):
    print(f"Error: not exist {args.plink2}.ped\n\n")
    sys.exit(1)

if not os.path.exists(f"{args.plink2}.map"):
    print(f"Error: not exist {args.plink2}.map\n\n")
    sys.exit(1)

if args.chipid2 is not None:
    if not os.path.exists(f"{args.chipid2}"):
        print(f"Error: not exist {args.chipid2}\n\n")
        sys.exit(1)

if args.cmp_all not in legal_argument_set:
    print("Error: illegal input, --cmp-all must be yes or no\n\n")
    sys.exit(1)

if args.exclude_miss not in legal_argument_set:
    print("Error: illegal input, --exclude-miss must be yes or no\n\n")
    sys.exit(1)

if args.save_temp not in legal_argument_set:
    print("Error: illegal input, --save-temp must be yes or no\n\n")
    sys.exit(1)

#开始流程

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
rename_chipid_file = open('rename_chipid_temp.txt','w')
common_snp_file = open(f'{plink_prefix1}_{plink_prefix2}_common_snp_temp.txt','w')

error_status = False 

#提取共同位点
j = 0
temp_id_set = set()
temp_line_set = set()
map1_dick = {}  # SNP名称：染色体_物理位置
for i in map1:
    j += 1
    f = i.split()
    if (len(f) == 4):
        if '\t'.join(f) not in temp_line_set:
            temp_line_set.add('\t'.join(f))
            if f[1] not in temp_id_set:
                temp_id_set.add(f[1])
                map1_dick[f[1]] = f[0]+"_"+f[3] # SNP名称：“染色体_物理位置”
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
                if f[1] in map1_dick:
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

print("\nNumber of common SNPs in two plink files: {}\n".format(common_snp_num))

#创建一个函数，得到芯片号-个体号的字典(chipid_sampleid_dick 提前创建)
def Chipid_Sampleid(chipid_file_name):
    chipid_file = open(chipid_file_name,'r')
    global error_status
    j = 0
    temp_id_set = set()
    temp_id_set2 = set()
    temp_line_set = set()
    for i in chipid_file:
        j += 1
        f = i.split()
        if (len(f) >= 2):
            if '\t'.join(f) not in temp_line_set:
                temp_line_set.add('\t'.join(f))
                if f[0] not in temp_id_set:
                    temp_id_set.add(f[0])
                    if f[1] not in temp_id_set2:
                        temp_id_set2.add(f[1])
                        chipid_sampleid_dick[f[0]] = f[1] #芯片号：个体号
                    else:
                        print(f"Error: duplicated sample id {f[1]} in different rows in {chipid_file_name}\n") 
                        error_status = True
                else:
                    print(f"Error: duplicated chip id {f[0]} in different rows in {chipid_file_name}\n") 
                    error_status = True
            else:
                print(f"Warinning: duplicted row {j} in {chipid_file_name}\n")
        else:
            print(f"Error: {j} row in {chipid_file_name} has less than 2 coloums\n")
            error_status = True
    chipid_file.close()


 
#重命名
newid_dick = {} #chipid/sampleid:newid
sampleid_dick = {} #newid:chipid/sampleid

j = 0

#ped重编码为数字(1-indexed)，家系号设定为0。

#查看是否存在chipid1
if args.chipid1 is not None:
    chipid_sampleid_dick = {}
    Chipid_Sampleid(args.chipid1) #运行函数
    for i in ped1:
        f = i.split()
        if f[1] in chipid_sampleid_dick:
            j += 1
            newid_dick[chipid_sampleid_dick[f[1]]] = j
            sampleid_dick[j] = chipid_sampleid_dick[f[1]]
            rename_chipid_file.write(f"{chipid_sampleid_dick[f[1]]}\t{j}\n")
            f[1] = str(j)
            re_ped1.write('0'+'\t'+'\t'.join(f[1:])+'\n')
        else:
            print(f"Warning: {f[1]} in {args.plink1}.ped not in chpid file")
else:
    for i in ped1:
        f = i.split()
        j += 1
        newid_dick[f[1]] = j
        sampleid_dick[j] = f[1]
        rename_chipid_file.write(f"{f[1]}\t{j}\n")            
        f[1] = str(j)
        re_ped1.write('0'+'\t'+'\t'.join(f[1:])+'\n')
        
sample1_num = j
print("Number of records present in plink1 ped file: {}\n".format(sample1_num))

common_sample_list = []
common_sample_num = 0
#查看是否存在chipid2
if args.chipid2 is not None:
    chipid_sampleid_dick = {}
    Chipid_Sampleid(args.chipid2) #运行函数
    for i in ped2:
        f = i.split()
        if f[1] in chipid_sampleid_dick:
            j += 1 #接着上面递增
            sampleid_dick[j] = chipid_sampleid_dick[f[1]]
            if chipid_sampleid_dick[f[1]] in newid_dick: #提取相同样本
                common_sample_num += 1
                common_sample_list.append([newid_dick[chipid_sampleid_dick[f[1]]],j]) #两个重编号  
            rename_chipid_file.write(f"{chipid_sampleid_dick[f[1]]}\t{j}\n")
            f[1] = str(j)
            re_ped2.write('0'+'\t'+'\t'.join(f[1:])+'\n')
        else:
            print(f"Warning: {f[1]} in {args.plink2}.ped not in chpid file")
else:
    for i in ped2:
        f = i.split()
        j += 1
        sampleid_dick[j] = f[1]
        if f[1] in newid_dick:
                common_sample_num += 1
                common_sample_list.append([newid_dick[f[1]],j]) #两个重编号  
        rename_chipid_file.write(f"{f[1]}\t{j}\n")            
        f[1] = str(j)
        re_ped2.write('0'+'\t'+'\t'.join(f[1:])+'\n')
        
sample2_num = j - sample1_num
print("Number of records present in plink2 ped file: {}\n".format(sample2_num))
print("Number of common samples in two plink file: {}\n".format(common_sample_num))
    
ped1.close()
map1.close()
ped2.close()
map2.close()
re_ped1.close()
re_ped2.close()
rename_chipid_file.close()
common_snp_file.close()

#extract merge recodeA

merge_status = os.system(f"plink --allow-extra-chr --chr-set 95 --file {plink_prefix1}_temp --merge {plink_prefix2}_temp --extract {plink_prefix1}_{plink_prefix2}_common_snp_temp.txt --recodeA --out {plink_prefix1}_{plink_prefix2}_merge_temp > /dev/null")

if merge_status != 0:
    print("Error in merge two plink data\n")
    print("Maybe some common SNP from Complementary strands,check your data again")
    sys.exit(1)

#raw文件处理
os.system(f"sed 's/NA/3/g' {plink_prefix1}_{plink_prefix2}_merge_temp.raw > {plink_prefix1}_{plink_prefix2}_merge_temp_sed.raw")
raw_file = open(f"{plink_prefix1}_{plink_prefix2}_merge_temp_sed.raw",'r')
out_file = open(args.out,'w')

gene_list=[]
raw_list=[]
title = raw_file.readline() #剔除标题
for i in raw_file:
    f = i.split()
    gene_list.append(int(f[1]))
    raw_list.append(f[6:])

gene_id_array1 = np.array(gene_list)

array1 = np.array(raw_list, dtype=np.int8)

total_sample_num = array1.shape[0]
snp_num = array1.shape[1]
print("Number of records present in merged ped file: {}\n".format(total_sample_num))
print("Number of SNPs in merged plink files: {}\n".format(snp_num))

#创建比对函数（是否剔除缺失值）
#这个函数定死了使用 array1 first_index second index
#创建两个函数，这样只要判断一次，而不要每个pair都要判断是否剔除缺失值

def Exclude_Miss_Yes():
    #输出变量设置为全局变量
    global total_num,no_match_num,no_match_rate
    v1 = array1[first_index,:]
    v2 = array1[second_index,:]
    non_miss_index = np.where((v1!=3) & (v2!=3))
    total_num = non_miss_index[0].shape[0]
    v1_new = v1[non_miss_index]
    v2_new = v2[non_miss_index]
    no_match_num = np.count_nonzero(v1_new!=v2_new)
    no_match_rate = no_match_num/total_num

    
def Exclude_Miss_No():
    #输出变量设置为全局变量
    global total_num,no_match_num,no_match_rate
    v1 = array1[first_index,:]
    v2 = array1[second_index,:]
    total_num = v1.shape[0]
    no_match_num = np.count_nonzero(v1!=v2)
    no_match_rate = no_match_num/total_num

#计算不一致率
out_list = []
if args.cmp_all == 'yes': #计算所有pairs
    if args.exclude_miss == 'yes':
        for i in range(sample1_num):
            for j in range(sample1_num, total_sample_num):
                first_index = i
                second_index = j
                #计算去除缺失后的不一致位点数
                Exclude_Miss_Yes()
                #newid = index + 1
                out_list.append([sampleid_dick[first_index+1],sampleid_dick[second_index+1],f"{no_match_num}",f"{total_num}",f"{no_match_rate:.4f}"])
    elif args.exclude_miss == 'no':
        for i in range(sample1_num):
            for j in range(sample1_num, total_sample_num):
                first_index = i
                second_index = j
                #计算去除缺失后的不一致位点数
                Exclude_Miss_No()
                #newid = index + 1
                out_list.append([sampleid_dick[first_index+1],sampleid_dick[second_index+1],f"{no_match_num}",f"{total_num}",f"{no_match_rate:.4f}"])                             
elif args.cmp_all == 'no': #只计算个体号相同的pairs
    if len(common_sample_list) == 0: #如果没有共同个体，报错
        print("Error: two ped file has no same samples, check your data again!")
        sys.exit(1)
    else:
        if args.exclude_miss == 'yes':
            for i in common_sample_list:
                #index = newid - 1
                first_index = i[0] - 1
                second_index = i[1] -1 
                #计算去除缺失后的不一致位点数
                Exclude_Miss_Yes()
                out_list.append([sampleid_dick[i[0]],sampleid_dick[i[1]],f"{no_match_num}",f"{total_num}",f"{no_match_rate:.4f}"])
        elif args.exclude_miss == 'no':
            for i in common_sample_list:
                #index = newid - 1
                first_index = i[0] - 1
                second_index = i[1] -1 
                #计算去除缺失后的不一致位点数
                Exclude_Miss_No()
                out_list.append([sampleid_dick[i[0]],sampleid_dick[i[1]],f"{no_match_num}",f"{total_num}",f"{no_match_rate:.4f}"])


sorted_out_list = sorted(out_list, key = lambda s:(float(s[4]),s[0])) #不一致率从小到大
for i in sorted_out_list:
    out_file.write('\t'.join(i)+'\n')

raw_file.close()
out_file.close()
    
#删除中间文件
if args.save_temp == "yes":
    pass
elif args.save_temp == "no":
    os.system(f"rm *temp*")

    
    
end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("Finish time: {}\n".format(end_time)) 
