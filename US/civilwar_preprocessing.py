
import pandas as pd

us_states = {   # https://gist.github.com/tlancon/9794920a0c3a9990279de704f936050c
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}
us_states = {v: k for k, v in us_states.items()}

def preprocess():
    
    nps_battles = pd.read_csv("dataset/nps_battles.csv", encoding='utf-8')
    cwsac_campaigns = pd.read_csv("dataset/cwsac_campaigns.csv", encoding='utf-8')
    cwsac_commanders = pd.read_csv("dataset/cwsac_commanders.csv", encoding='utf-8')


    cwsac_battles = pd.read_csv("dataset/cwsac_battles.csv", encoding='utf-8')

    longs = []
    lats = []
    theater_names = []

    conf_commanders = []
    union_commanders = []

    cwsac_battles["state_name"] = cwsac_battles["state"].apply(lambda x: us_states[x])
    
    for idx, row in cwsac_battles.iterrows():

        battle_id = row["battle"]
        campaign_name = row["campaign"]

        nps_battle = nps_battles.loc[nps_battles["cwsac_id"] == battle_id]
        cwsac_campaign = cwsac_campaigns.loc[cwsac_campaigns["campaign"] == campaign_name]
        theater_names.append(list(cwsac_campaign["theater"])[0])

        # Commanders
        conf_commanders.append([None, None, None, None])
        union_commanders.append([None, None, None, None])

        conf_idx = 0
        union_idx = 0
        cwsac_commanders2 = cwsac_commanders.loc[cwsac_commanders["battle"] == battle_id]
        for idx, c in cwsac_commanders2.iterrows():
            if (c[1] == "Confederate"):
                conf_commanders[-1][conf_idx] = c[2]
                conf_idx += 1
            elif (c[1] == "US"):
                union_commanders[-1][union_idx] = c[2]
                union_idx += 1
                
        lats_ = list(nps_battle["lat"])
        longs_ = list(nps_battle["long"])
        if (len(lats_) and len(longs_)): 
            lats.append(lats_[0])
            longs.append(longs_[0])
        else:
            lats.append(0)
            longs.append(0)

    cwsac_battles["conf_commander1"] = [c[0] for c in conf_commanders]
    cwsac_battles["conf_commander2"] = [c[1] for c in conf_commanders]
    cwsac_battles["conf_commander3"] = [c[2] for c in conf_commanders]
    cwsac_battles["conf_commander4"] = [c[3] for c in conf_commanders]

    cwsac_battles["union_commander1"] = [c[0] for c in union_commanders]
    cwsac_battles["union_commander2"] = [c[1] for c in union_commanders]
    cwsac_battles["union_commander3"] = [c[2] for c in union_commanders]
    cwsac_battles["union_commander4"] = [c[3] for c in union_commanders]
        

    cwsac_battles["long"] = longs
    cwsac_battles["lat"] = lats
    cwsac_battles["theater"] = theater_names
    cwsac_battles.to_csv("dataset/cwsac_battles_pp.csv")

if __name__ == "__main__":
    preprocess()