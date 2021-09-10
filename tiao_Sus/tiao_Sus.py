#coding=utf-8
#挑不规则行数据

import sys
in_file = open(sys.argv[1],'r')
field = sys.argv[2]
out_file = open(sys.argv[3],'w')

dick = {}

j=0
for i in in_file:
    dick[j] = i #行：内容 从0开始
    j+=1

j=0 
while j < len(dick): #不是<=
    if ('>' in dick[j]) and (field in dick[j]):
        out_file.write(dick[j])
        j+=1
        while ('>' not in dick[j]):
            out_file.write(dick[j])
            j+=1
    else:
        j+=1
    
in_file.close()
out_file.close()

           
        