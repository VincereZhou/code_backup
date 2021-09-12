# coding=utf-8
# 一个生成指定snp顺序的plink文件的程序
# 三个参数，第一个为参考map文件，第二个为输入plink文件前缀，第三个为输出plink文件前缀。

import os,sys

ref_map_name = sys.argv[1]
in_plink_prefix = sys.argv[2]
out_plink_prefix = sys.argv[3]

error_status = False

# 判断输入文件是否存在且非空
def Judge_file(file_path):
    import os
    if os.path.exists(file_path):
        if os.path.getsize(file_path):
            return True
    return False

if not Judge_file(ref_map_name):
    print(f"Error: {ref_map_name} not exist or is empty file\n")
    error_status = True
    
if not Judge_file(f"{in_plink_prefix}.ped"):
    print(f"Error: {in_plink_prefix}.ped not exist or is empty file\n")
    error_status = True
elif not Judge_file(f"{in_plink_prefix}.map"):
    print(f"Error: {in_plink_prefix}.map not exist or is empty file\n")
    error_status = True

if in_plink_prefix == out_plink_prefix:
    print("Error: second argument is same with third argument\n")
    error_status = True

if error_status:
    sys.exit(1)

# 判断两个map的SNP名称是否完全一致
ref_map_file = open(ref_map_name,'r')
in_map_file = open(f"{in_plink_prefix}.map",'r')

ref_snp_list = []
ref_snp_dick = {}
j = 0
temp_id_set = set()
for i in ref_map_file:
    j += 1
    f = i.split()
    if len(f) == 4:
        if f[1] not in temp_id_set:
            temp_id_set.add(f[1])
            ref_snp_list.append(f[1])
            ref_snp_dick[f[1]] = str(j) # snp: 序号
        else:
            print(f"Error: duplicated id {f[1]} in {ref_map_name}\n")
            error_status = True
    else:
        print(f"Error: {j} row in {ref_map_name} has less or more than 4 columns\n")
        error_status = True

in_snp_list = []
not_in_snp_list = [] # 不在参考map中的snp
j = 0
temp_id_set = set()
for i in in_map_file:
    j += 1
    f = i.split()
    if len(f) == 4:
        if f[1] not in temp_id_set:
            temp_id_set.add(f[1])
            in_snp_list.append(f[1])
            if f[1] not in ref_snp_dick:
                not_in_snp_list.append(f[1])
                error_status = True
        else:
            print(f"Error: duplicated id {f[1]} in {in_plink_prefix}.map\n")
            error_status = True
    else:
        print(f"Error: {j} row in {in_plink_prefix}.map has less or more than 4 columns\n")
        error_status = True


ref_map_file.close()
in_map_file.close()

if not_in_snp_list:
    temp_str = ", ".join(not_in_snp_list)
    print(f"Error: snp in {in_plink_prefix}.map but not in {ref_map_name}: {temp_str}\n")

if (not error_status) and (len(ref_snp_list) != len(in_snp_list)):
    print(f"Error: snp numbers of {in_plink_prefix}.map and {ref_map_name} are not same\n")
    error_status = True

if error_status:
    sys.exit(1)

# 生成临时map文件，染色体均设为1，物理位置设置为参考map的序号
temp_map_file = open(f"{in_plink_prefix}_temp.map",'w')
for i in in_snp_list:
    temp_map_file.write('1'+'\t'+i+'\t'+'0'+'\t'+ref_snp_dick[i]+'\n')

temp_map_file.close()

# 重排
os.system(f"plink --allow-extra-chr --chr-set 95 --ped {in_plink_prefix}.ped --map {in_plink_prefix}_temp.map --recode --out {out_plink_prefix} > /dev/null")

# 使用参考map替换结果map
os.system(f"cp {ref_map_name} {out_plink_prefix}.map")

# 删除中间文件
os.system("rm *temp*")
