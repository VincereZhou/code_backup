# 使用 R 转换数据

Rscript mass_to_plink.R rawdata.xlsx raw.map

mv new.ped new1.ped
mv new.map new1.map

# 使用 python 进行转换

python mass_to_plink.py rawdata.xlsx raw.map new2

# 比对两次结果

python compair_samples.py --plink1 new1 --plink2 new2 --exclude-miss no > compair_samples.log

