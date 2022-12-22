
import pandas as pd

def preprocess():
    f_out = open("dataset/cwsac_battles_pp.csv", "w")
    
    nps_battles = pd.read_csv("dataset/nps_battles.csv", encoding='utf-8')

    f_out.write("battle,url,battle_name,other_names,state,locations,campaign,start_date,end_date,operation,assoc_battles,results_text,result,forces_text,strength,casualties_text,casualties,description,preservation,significance,")
    f_out.write("lat,long\n")

    with open("dataset/cwsac_battles.csv", "r") as f:
        for i, line in enumerate(f.readlines()):
            if (i == 0): continue

            battle_id = line.split(",")[0]
            print(battle_id)

            nps_battle = nps_battles.loc[nps_battles["cwsac_id"] == battle_id]
            
            lats = list(nps_battle["lat"])
            longs = list(nps_battle["long"])
            print(lats)
            if (len(lats) and len(longs)):
                lat = lats[0]
                long = longs[0]
            else:
                lat = 0
                long = 0
                
            line = line.replace("\n", "")

            f_out.write(f"{line},{lat},{long}\n")

    f_out.close()

if __name__ == "__main__":
    preprocess()