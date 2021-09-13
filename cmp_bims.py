#!/mnt/data/zhouziwen/bin/miniConda/miniconda3/bin/python
#coding=utf-8
#查找目标文件夹下哪个plink文件有问题
#先将每队plink转化为bim, 再查看bim文件的问题

import sys,os
from collections import defaultdict

work_path = sys.argv[1]

total_error_status = False

# 切换目录
os.chdir(work_path) 

# 每对plink文件生成 bim 文件
for i in os.listdir("."):
    if os.path.isfile(i): #判断是文件
        if i[-4:] == ".ped": #判断后缀是.ped
            prefix = i[:-4]   #去除.ped
            if not os.path.exists(f"{prefix}.map"):
                print(f"Error: have {prefix}.ped but not have {prefix}.map\n")
                total_error_status = True
            else:
                exit_code = os.system(f"plink --allow-extra-chr --chr-set 95 --file {prefix} --out {prefix} &> /dev/null")
                if exit_code != 0:
                    print(f"Error: plink file {prefix} has problems and can't go through plink software, please see {prefix}.log\n")
                    total_error_status = True

if total_error_status:
    sys.exit(1) 


dict1 = defaultdict(set) #snp:碱基（不包括0）

#遍历所有的bim文件
j = 0
for i in os.listdir("."):
    if (os.path.isfile(i)) and (i[-4:] == ".bim"): #判断是文件，后缀为bim
        # prefix = i[:-4]   #去除.bim
        j += 1
        if j == 1:
            print(f"{i} is first bim") # 打印第一个文件
            bim_file = open(i,'r')
            for i2 in bim_file:
                f2 = i2.split()
                temp_alleles_set = dict1[f2[1]] # 该SNP的碱基集合
                temp_alleles_set.add("0") # 先添加0
                temp_alleles_set.add(f2[-2])
                temp_alleles_set.add(f2[-1])
            bim_file.close()
        else:
            # 以第一个bim为模板，比对其他bim文件。
            bim_file = open(i,'r')
            for i2 in bim_file:
                f2 = i2.split()
                if f2[1] in dict1:
                    temp_alleles_set = dict1[f2[1]].copy() # 第一个文件该SNP碱基集合的拷贝
                    temp_alleles_set.add(f2[-2])
                    temp_alleles_set.add(f2[-1])
                    if len(temp_alleles_set) > 3: # 如果超过了两个碱基
                        print(f"Error: SNP {f2[1]} in {i} is not consistent with first bim\n") #打印错误文件的错误碱基
                        break
                else:
                    print(f"Error: SNP {f2[1]} in {i} not in first bim\n")
                    break
            else:
                print(f"{i} is well") #没有问题则打印没问题
            bim_file.close()

            
            
            
