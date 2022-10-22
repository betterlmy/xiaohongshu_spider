known_xhs_id = [5,6,'7']


with open("output/known_id.txt","w",encoding="utf-8") as f:
    for id in known_xhs_id:
        f.write(str(id)+"\n")