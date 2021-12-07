#!/mnt/data/zhouziwen/bin/miniConda/miniconda3/bin/python
#coding=utf-8
#基于某列作为主键，比较两个文件的内容是否相同。


import argparse,os,sys,time

parser = argparse.ArgumentParser(prog="compare_two_files", description='compare contents in two files when some column is set as key')

# 添加参数步骤，如果不提供参数，那个参数就是 None
parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
parser.add_argument("--file1", required=True, 
    help='''the first file's name''')
parser.add_argument("--file2", required=True, 
    help='''the second file's name''')
parser.add_argument("--key-column", required=False, default = "1",
    help='''the column number to set as key, if you need to specify multiple columns, use ',' as separator , for example '1,2' .
    default is 1, means first column''')
parser.add_argument("--file-separator", required=False,
    help='''separator of two files, default is backspace or tab''')

args = parser.parse_args()

#打印软件版本
print(" ---------------------------------------------")
print("|             compare_two_files.py            |")
print("|                                             |")
print("|             2021 - Version 1.0              |")
print("|          (lase update: Sept 16, 2021)       |")
print("|             Compass, Beijing                |")
print(" ---------------------------------------------\n")

#打印开始时间
begin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("Start time: {}\n".format(begin_time)) 


#打印所有参数        
print("Arguments\n")
print("  --file1 {}\n".format(args.file1))
print("  --file2 {}\n".format(args.file2))
print("  --key-column {}\n".format(args.key_column))
print("  --file-separator {}\n".format(args.file_separator))

#检验参数
error_status = False # 错误逻辑值

def Judge_file(file_path):
    import os
    if os.path.exists(file_path):
        if os.path.getsize(file_path):
            return True
    return False

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
    	return False

# 检查文件是否存在且非空
if not Judge_file(args.file1):
    print(f"Error: {args.file1} not exists or is empty file\n\n")
    sys.exit(1)
    
if not Judge_file(args.file2):
    print(f"Error: {args.file2} not exists or is empty file\n\n")
    sys.exit(1)

# 检查两个文件第一行列数是否相同
file1 = open(args.file1,'r')
file2 = open(args.file2,'r')

file1_column = len(file1.readline().strip().split(args.file_separator))
file2_column = len(file2.readline().strip().split(args.file_separator))

if file1_column != file2_column:
    print("Error: file1 and file2 has different columns in first row")
    sys.exit(1)

key_column_str_list = args.key_column.split(',')  # 所有关键列组成的列表，元素为字符串 

for i in key_column_str_list:
    if (not is_int(i)) or (int(i) < 0) or (int(i) > file1_column):
        print("Error: key column {i} is not integer or out of columns range")
        sys.exit(1)

key_index_list = [int(i)-1 for i in key_column_str_list]  # 所有关键列索引组成的列表

# 检查文件
file1.seek(0)
file2.seek(0)

j = 0
temp_id_set = set()
temp_line_set = set()
dict1 = {}
for i in file1:
    j += 1
    f = i.strip().split(args.file_separator)
    if (len(f) == file1_column):
        if '\t'.join(f) not in temp_line_set:
            temp_line_set.add('\t'.join(f))
            key = f[key_index_list[0]] # 键：多列内容用 \t 结合到一起
            for i2 in key_index_list[1:]:
                key = key + "\t" + f[i2]
            if key not in temp_id_set:
                temp_id_set.add(key)
                dict1[key] = '\t'.join(f) # 键：行内容
            else:
                print(f"Error: duplicated id {key} in different rows in {args.file1}\n") 
                error_status = True
        else:
            print(f"Warning: duplicted row {j} in {args.file1}\n")
    else:
        print(f"Error: {j} row in {args.file1} has less or more than {file1_column} columns\n")
        error_status = True

j = 0
temp_id_set = set()
temp_line_set = set()
dict2 = {}
only_in_file2_list = [] # 只在 file2 中的键的内容
for i in file2:
    j += 1
    f = i.strip().split(args.file_separator)
    if (len(f) == file2_column):
        if '\t'.join(f) not in temp_line_set:
            temp_line_set.add('\t'.join(f))
            key = f[key_index_list[0]] # 键：多列内容用 \t 结合到一起
            for i2 in key_index_list[1:]:
                key = key + "\t" + f[i2]
            if key not in temp_id_set:
                temp_id_set.add(key)
                if key in dict1:
                    dict2[key] = '\t'.join(f) # 共同的键：第二个文件行内容
                else:
                    only_in_file2_list.append('\t'.join(f)+'\n')
            else:
                print(f"Error: duplicated id {key} in different rows in {args.file2}\n") 
                error_status = True
        else:
            print(f"Warning: duplicted row {j} in {args.file2}\n")
    else:
        print(f"Error: {j} row in {args.file2} has less or more than {file2_column} columns\n")
        error_status = True

file1.close()
file2.close()

if error_status:
    sys.exit(1)


only_in_file1_list = [] # 只在 file1 中的键的内容

for i in dict1:
    if i not in dict2:
        only_in_file1_list.append(dict1[i]+'\n')

# 比较共同key的行
same_common_key_num = 0
diff_common_key_num = 0
diff_rows_list = [] # 不一致行的内容

for i in dict2:
    if dict1[i] == dict2[i]:
        same_common_key_num += 1
    else:
        diff_common_key_num += 1
        diff_rows_list.append(dict1[i]+'\n')
        diff_rows_list.append(dict2[i]+'\n\n')

if (len(only_in_file1_list) == 0) and (len(only_in_file2_list) == 0) and (diff_common_key_num == 0):
    print("Congratulations: two files are same in contents")
    sys.exit(0)
else:
    print(f"rows only in file1 : {len(only_in_file1_list)}\n")
    print(f"rows only in file2 : {len(only_in_file2_list)}\n")
    print(f"same rows in two files: {same_common_key_num}\n")
    print(f"different rows in two files: {diff_common_key_num}\n")
    
    # 写入文件
    if only_in_file1_list:
        only_in_file1 = open("only_in_file1.txt",'w')
        only_in_file1.writelines(only_in_file1_list)
        only_in_file1.close()

    if only_in_file2_list:
        only_in_file2 = open("only_in_file2.txt",'w')
        only_in_file2.writelines(only_in_file2_list)
        only_in_file2.close()

    if diff_rows_list:
        diff_rows_file = open("diff_rows.txt",'w')
        diff_rows_file.writelines(diff_rows_list)
        diff_rows_file.close()
