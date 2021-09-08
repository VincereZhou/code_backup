# 需要设置参数
args<-commandArgs(T)

# 加载 readxl 包，用于读取Excel数据
library(readxl)

# 第一个参数为原始基因型数据的Excel文件名，内容放在 sheet1 中
in_file = read_excel(args[1],sheet = 1)

# 第二个参数为参考map文件，包含了原始基因型数据的所有位点。
map_file = read.table(args[2],header = F)

# 提取原始基因型数据的所有SNP名称
snp_name = names(in_file)[2:length(names(in_file))]

# 向量转为数据框
snp_dataframe = data.frame(snp_name) #生成数据框

# 基因型第一列为芯片号
id_vector = in_file[,1]

# 剔除第一列，即为所有基因型信息的列
data = in_file[,-1] #不要第一列

# 创建一个空的数据框，用于保存处理后的基因型信息
out_data=data.frame()

# 对原始基因型数据进行处理
# Excel 中的空格为缺失，改为00
# 如果只有一个字符，则为纯合子，改为两个字符，如 A 改为 AA
for(i in 1:nrow(data)){
  for (j in 1:ncol(data)){
    if (is.na(data[i,j])){
      out_data[i,j] = "00" #缺失改为00
    } else {
      if (nchar(data[i,j]) == 1){
        out_data[i,j] = paste0(data[i,j],data[i,j])
      } else {
        out_data[i,j] = data[i,j]
      }
    }
  }
}

# out_data 的列名设为空
names(out_data) = NULL

# 生成plink格式的ped文件，使用 cbind 函数合并列，利用了R的广播机制
out_ped = cbind(0,id_vector,0,0,0,0,out_data)

# 生成compound格式的ped文件
write.table(out_ped,file = "compound.ped", col.names = F,quote = F,row.names = F)

# 生成map文件
# 首先对 map_file 和 snp_dataframe 添加列名
names(map_file) = c("chr","snp","3","pos")
names(snp_dataframe) = c("snp") #必须用数据框才能merge

# 使用 merge 函数进行“左连接”, 提取 snp_dataframe 在原始map 文件中的行
# 注意：必须事先保证原始基因型数据的所有SNP均在提供的map文件中。
out_map = merge(snp_dataframe, map_file, by="snp", all.x=TRUE) #顺序错了

# 使用 merge 生成的 out_map 顺序乱了，需要重排列的顺序
new_map = out_map[,names(map_file)] #重排

# 写入文件
write.table(new_map,file = "compound.map", col.names = F,quote = F,row.names = F)

#最后用plink软件转化为正常的plink格式的文件
system("plink --allow-extra-chr --file compound --compound-genotypes --recode --out new > /dev/null")
