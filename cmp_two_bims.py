#!/mnt/data/zhouziwen/bin/miniConda/miniconda3/bin/python
#coding=utf-8
#对比两个bim文件是否相同，相同的SNP名称有相同的等位基因（0不算）

import sys
bim1 = open(sys.argv[1],'r')
bim2 = open(sys.argv[2],'r')
out_file = open(sys.argv[3],'w')

out_file.write("\t".join(["snp","bim1_A1","bim1_A2","bim2_A1","bim2_A2"])+'\n')

dick = {}
for i in bim1:
    f = i.split()
    dick[f[1]] = f[-2:] #snp名称：倒数第二列


error_base_num = 0
for i in bim2:
    f = i.split()
    if f[1] not in dick:
        print("Error: {} in bim2 not in bim1".format(f[1]))
        sys.exit()
    else:
        bim1_alleles_set = set(dick[f[1]])
        bim1_alleles_set.add("0")
        bim1_alleles_set.add(f[-2])
        bim1_alleles_set.add(f[-1])
        if len(bim1_alleles_set) > 3: #如果包括0，两个bim合并的等位基因数目大于3，就有问题
            error_base_num += 1
            bim1_alleles = '\t'.join(dick[f[1]])
            out_file.write(f"{f[1]}\t{bim1_alleles}\t{f[-2]}\t{f[-1]}\n")
            # print("Error: {} in bim2 file has more than 2 alleles".format(f[1]))
            # sys.exit()

if error_base_num == 0:
    print("Congradulation: two bim fils is consistent")
else:
    print(f"Error: {error_base_num} bases has more than 2 alleles")
           
            
bim1.close()
bim2.close()
out_file.close()

