#coding=utf-8
#提供的raw 文件必须剔除性染色体
import argparse,os,time
import numpy as np

begin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("Start time: {}\n".format(begin_time)) 

np.seterr(divide='ignore',invalid='ignore')

parser = argparse.ArgumentParser(description='check the parent-offspring relationship in the pedigree file')

# 添加参数步骤，如果不提供参数，那个参数就是 None
parser.add_argument("--raw", required=True, 
    help='''the raw file generated from plink software''')
parser.add_argument("--chipid", required=True, 
    help='''id file corresponding to the raw file. two columns are required, 
        the first column is the chip id, the second column is the real id in pedigree file''')
parser.add_argument("--pedigree", required=True, 
    help='''the pedigree file of genotyped individuals.the first three 
        columns are id,sire and dam''')
parser.add_argument("--list", required=False, 
    help='''a list file consisting of only a list of real id which is consistent with pedigree file. calculations will be restricted for individuals present in the list file.''')
parser.add_argument("--check-prob", required=False, default="0.005",
    help='''the exclusion probability thresholdas as percentage of mendelian inconsistent SNPs between parent-progeny pairs,default is 0.005''')
parser.add_argument("--miss-snp", required=False, default="0.2",
    help='''the missing rate thresholdas of SNPs,default is 0.2''')
parser.add_argument("--miss-sample", required=False, default="0.5",
    help='''the missing rate thresholdas of samples,default is 0.5''')
parser.add_argument("--maf", required=False, default="0.01",
    help='''the maf thresholdas of snp,default is 0.01''')

args = parser.parse_args()

#打印所有参数        
print("Arguments\n")
print("  --raw {}\n".format(args.raw))
print("  --chipid {}\n".format(args.chipid))
print("  --pedigree {}\n".format(args.pedigree))
print("  --list {}\n".format(args.list))
print("  --check-prob {}\n".format(args.check_prob))
print("  --miss-snp {}\n".format(args.miss_snp))
print("  --miss-sample {}\n".format(args.miss_sample))
print("  --maf {}\n\n".format(args.maf))

#打印raw文件行数
raw_lines = os.popen("wc -l {}".format(args.raw)).read().split()[0]
true_raw_lines = int(raw_lines) -1 
print("Number of records in raw file: {}\n".format(true_raw_lines))

#读取文件
raw_file = open(args.raw,'r')
chipid_file = open(args.chipid,'r')
pedigree_file = open(args.pedigree,'r')

#new_raw = open("newid.raw",'w+')

check_prob = open("chek_paternity_prob.txt",'w')
check_pedigree = open("check_pedigree.txt",'w')


########### raw 文件处理


# 标题处理
# a = raw_file.readline().split() #标题行
# title_list = []
# for i in range(len(a)):
    # if i >= 6:
        # new_title = a[i][:-2] #去除最后两个字符
        # title_list.append(new_title)

#写入新标题
#new_raw.write('\t'.join(title_list)+'\n')

# chipid 替换为 eartag
set1=set();dick={}
j=0
for i in chipid_file:
    f = i.split()
    j+=1
    if len(f) >= 2:
        if f[1] not in set1: #去除重复个体号
            set1.add(f[1])
            dick[f[0]] = f[1]
    else:
        print("Warning: {} row in chipid file has less than 2 coloum\n".format(j))

gene_list=[]
raw_list=[]
raw_file.readline() #剔除标题
for i in raw_file:
    f = i.split()
    if f[1] in dick:
        gene_list.append(dick[f[1]])
        raw_list.append('\t'.join(f[6:]))
        #new_raw.write('\t'.join(f[6:])+'\n')
    else:
        print("Warning: {} in raw file not in chpid file or is duplicated samples\n".format(f[1]))

gene_id_array = np.array(gene_list)

#new_raw.seek(0)

# snp 缺失值过滤，结果文件是 array2
#numpy 0/1 结果会显示为 nan
array1 = np.genfromtxt(raw_list, dtype=np.int8, missing_values="NA", filling_values=3)
#array2 = array1.copy()

sample_num = array1.shape[0]
snp_num = array1.shape[1]


print("Number of SNPs in raw file: {}\n".format(snp_num))
print("Number of records present in chipid file: {}\n".format(sample_num))


bool_array1 = array1==3

total_miss = bool_array1.sum()/(bool_array1.shape[0] * bool_array1.shape[1])
toatl_callrate = 1 - total_miss
print("Total genotyping rate is {:.3f}\n".format(toatl_callrate))

snp_missing_count = bool_array1.sum(axis=0)


snp_missing_prob = snp_missing_count/sample_num

snp_missing_min = snp_missing_prob.min()
snp_missing_mean = snp_missing_prob.mean()
snp_missing_max = snp_missing_prob.max()

#打印snp缺失值情况
print("SNP missing\n")
print("  Min missing rate: {:.3f}\n".format(snp_missing_min))
print("  AVG missing rate: {:.3f}\n".format(snp_missing_mean))
print("  Max missing rate: {:.3f}\n".format(snp_missing_max))
#np.savetxt("snp_missing.txt",snp_missing_prob, fmt='%.4f')

snp_missing_pick = snp_missing_prob < float(args.miss_snp)
array2 = array1[:,snp_missing_pick]
snp_miss_remove = array1.shape[1] - array2.shape[1]
print("{} snps removed due to missing genotype data\n".format(snp_miss_remove))
del array1
del bool_array1


# maf 过滤,结果文件是 array3

#计算array2每列的缺失值
bool_array2 = array2==3
snp_missing_count2 = bool_array2.sum(axis=0)

#将array2 中的3替换为0，提取备份为 array2_copy
array2_copy = array2.copy()
array2[array2==3] = 0

maf_sum = array2.sum(axis=0)
#print("maf_sum[1:5] are {}".format(maf_sum[1:5]))
maf_denominator = 2*(sample_num-snp_missing_count2)
#print("sample_num are {}".format(sample_num))
#print("maf_denominator[1:5] are {}".format(maf_denominator[1:5]))


maf_prob = maf_sum/maf_denominator
#print("maf_prob[1:5] are {}".format(maf_prob[1:5]))

#maf_out = np.column_stack((maf_sum,maf_denominator,maf_prob))
#np.savetxt("maf_all.txt",maf_out)
#np.savetxt("maf.txt",maf_prob, fmt='%.4f')

maf_min = maf_prob.min()
maf_mean = maf_prob.mean()
maf_max = maf_prob.max()

#打印MAF情况
print("Minor alleles frequencies\n")
print("  Min alleles frequencies: {:.3f}\n".format(maf_min))
print("  AVG alleles frequencies: {:.3f}\n".format(maf_mean))
print("  Max alleles frequencies: {:.3f}\n".format(maf_max))

snp_maf_pick = maf_prob > float(args.maf)
array3 = array2_copy[:,snp_maf_pick]

snp_maf_remove = array2_copy.shape[1] - array3.shape[1]
print("{} snps removed due to minor allele threshold\n".format(snp_maf_remove))
del array2
del array2_copy

# sample_miss 过滤，结果为 array4

sample_num3 = array3.shape[0]
snp_num3 = array3.shape[1]

bool_array3 = array3==3

sample_missing_count = bool_array3.sum(axis=1)
sample_missing_prob = sample_missing_count/snp_num3

sample_missing_min = sample_missing_prob.min()
sample_missing_mean = sample_missing_prob.mean()
sample_missing_max = sample_missing_prob.max()

#打印sample缺失值情况
print("Sample missing\n")
print("  Min missing rate: {:.3f}\n".format(sample_missing_min))
print("  AVG missing rate: {:.3f}\n".format(sample_missing_mean))
print("  Max missing rate: {:.3f}\n".format(sample_missing_max))

#np.savetxt("sample_missing.txt",sample_missing_prob, fmt='%.4f')

sample_missing_pick = sample_missing_prob < float(args.miss_sample)
array4 = array3[sample_missing_pick,:]

gene_id_array_new = gene_id_array[sample_missing_pick] #样本过滤后的基因个体号

sample_miss_remove = array3.shape[0] - array4.shape[0]

print("{} samples removed due to missing genotype data\n".format(sample_miss_remove))

print("{} samples and {} snps pass QC finally\n".format(array4.shape[0],array4.shape[1]))

print("Begin paternity check\n")

#如果删除了样本，将删除的样本id和缺失率写入一个新文件
if sample_miss_remove > 0 :
    filter_sample_file = open('sample_filted.txt','w')
    sample_missing_fail = sample_missing_prob >= float(args.miss_sample)
    gene_id_fail_array = gene_id_array[sample_missing_fail]
    sample_missing_prob_array = sample_missing_prob[sample_missing_fail]
    for i in range(gene_id_fail_array.shape[0]):
        filter_sample_file.write(str(gene_id_fail_array[i])+'\t'+str("{:.4f}".format(sample_missing_prob_array[i]))+'\n')
    filter_sample_file.close()
    
del array3
del bool_array3
    
#开始进行亲子鉴定
#array4 改为 1 2 3 0(缺失)
#这样两个array 的乘积的array为3的是错误位点，是0的是缺失位点。

array4 += 1
array4[array4==4] = 0

snp_num4 = array4.shape[1]

#清洗系谱，剔除第一列个体没有基因型的行

offspring_sire_list = []
offspring_dam_list = []
pedigree_list = []

#判断 args.list 是否存在
id_set = set()
if args.list is None:
    for i in pedigree_file:
        f = i.split()
        id_set.add(f[0])
else:
    list_file = open(args.list,'r')
    for i in list_file:
        f = i.split()
        id_set.add(f[0])

test_records=0
sire_pairs=0
dam_pairs=0
pedigree_file.seek(0)
for i in pedigree_file:
    f = i.split()
    if (f[0] in gene_id_array_new) and (f[0] in id_set):
        pedigree_list.append(f[0:3])
        test_records+=1
        if f[1] in gene_id_array_new:
            sire_pairs+=1
            offspring_sire_list.append([f[0],f[1]])
        if f[2] in gene_id_array_new:
            dam_pairs+=1
            offspring_dam_list.append([f[0],f[2]])

check_dick = {}

#np.savetxt("gene_id_array_new.txt",gene_id_array_new, fmt="%s")

#np.where 结果是一个元组，元组里是一个索引构成的数组，如(array([1, 2]),)
conflict_sire_pairs=0
conflict_dam_pairs=0
for i in offspring_sire_list:
    first_index = np.where(gene_id_array_new == i[0])
    second_index = np.where(gene_id_array_new == i[1])
    first_array = array4[first_index]
    second_array = array4[second_index]
    product_array = first_array * second_array
    error_snp_nums = (product_array==3).sum()
    miss_snp_nums =  (product_array==0).sum()
    total_snp_nums = snp_num4 - miss_snp_nums
    error_snp_prob = error_snp_nums/total_snp_nums
    if error_snp_prob < float(args.check_prob):
        match_status = "Match"
    else:
        match_status = "No-Match"
        conflict_sire_pairs+=1
    check_dick[tuple(i)] = match_status
    check_prob.write('Offspring-Sire'+'\t'+i[0]+'\t'+i[1]+'\t'+str(error_snp_nums)+'\t'+str(total_snp_nums)+'\t'+str(error_snp_prob)+'\t'+match_status+'\n')

for i in offspring_dam_list:
    first_index = np.where(gene_id_array_new == i[0])
    second_index = np.where(gene_id_array_new == i[1])
    first_array = array4[first_index]
    second_array = array4[second_index]
    product_array = first_array * second_array
    error_snp_nums = (product_array==3).sum()
    miss_snp_nums =  (product_array==0).sum()
    total_snp_nums = snp_num4 - miss_snp_nums
    error_snp_prob = error_snp_nums/total_snp_nums
    if error_snp_prob < float(args.check_prob):
        match_status = "Match"
    else:
        match_status = "No-Match"
        conflict_dam_pairs+=1
    check_dick[tuple(i)] = match_status
    check_prob.write('Offspring-Dam'+'\t'+i[0]+'\t'+i[1]+'\t'+str(error_snp_nums)+'\t'+str(total_snp_nums)+'\t'+str("{:.4f}".format(error_snp_prob))+'\t'+match_status+'\n')

for i in pedigree_list:
    offspring_sire = (i[0],i[1])
    offspring_dam = (i[0],i[2])
    if offspring_sire in check_dick:
        sire_info = check_dick[offspring_sire]
    else:
        sire_info = "par_nogeno"
    if offspring_dam in check_dick:
        dam_info = check_dick[offspring_dam]
    else:
        dam_info = "par_nogeno"
    check_pedigree.write('\t'.join(i)+'\t'+sire_info+'\t'+dam_info+'\n')
    

raw_file.close()
chipid_file.close()
pedigree_file.close()
#new_raw.close()
check_prob.close()
check_pedigree.close()

print("Records tested: {}\n".format(test_records))
print("  Pair parent/progeny tested: {}\n".format(sire_pairs+dam_pairs))
print("  Pair with conflicts: {}\n\n".format(conflict_sire_pairs+conflict_dam_pairs))

print("Sire-progeny tested: {}\n".format(sire_pairs))
print("Sire-progeny with conflicts: {}\n\n".format(conflict_sire_pairs))

print("Dam-progeny tested: {}\n".format(dam_pairs))
print("Dam-progeny with conflicts: {}\n\n".format(conflict_dam_pairs))

print("End paternity check\n")

end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("\nFinish time: {}\n".format(end_time)) 



