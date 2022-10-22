with open('output/known_id.txt',"r",encoding='utf-8') as f:
        known_xhs_id= [line.strip("\n") for line in f.readlines()]

print(known_xhs_id)