# required modules
import numpy as np
import pandas as pd
from datetime import datetime
import os



def getNewElo(elo_rating, W, W_prob):
    return np.round(elo_rating + 12.0*(W-W_prob),2)

def getExpectedWinProb(elo_rating, elo_rating_opposition, home_or_away):
    if home_or_away == "Home":
        dr = elo_rating-elo_rating_opposition+48.2
    elif home_or_away == "Away":
        dr = elo_rating-elo_rating_opposition-48.2
    else:
        dr = elo_rating-elo_rating_opposition
    return 1.0/(1.0+10.0**(-(dr/400.0)))

def main():
    folder = os.path.dirname(os.path.realpath(__file__))
    NRLdata = pd.read_csv(folder + "\\nrl-2022-EAustraliaStandardTime.csv")
    NRLdata["Round"] = NRLdata["Round Number"]
    NRLdata["Round"] = NRLdata["Round"].apply(lambda x: int(x) if type(x)==str and "Final" not in x else -1)
    NRLdata["Datetime"] = NRLdata["Date"].apply(lambda x: datetime.strptime(x, "%d/%m/%Y %H:%M"))
    NRLdata = NRLdata[NRLdata["Round"] > 0]
    df_elos = pd.read_csv(folder + "\\nrl-2022-eloratings.csv", index_col="Team")
    df_elos_modified = pd.read_csv(folder + "\\nrl-2022-eloratings_modified.csv", index_col="Team")
    rounds = sorted(set(NRLdata.dropna(subset=["Result"])['Round Number']))
    rounds = sorted([int(x) for x in rounds])
    rounds = [str(x) for x in rounds]
    print(rounds)
    #sorted_rounds = [str(x) for x in [int(x) for x in rounds]]
    for round_string in rounds:
        if round_string in df_elos.columns:
            print("Round {0} is already up to date...".format(round_string))
            continue
        else:
            print("Updating Elo ratings for round {0}. \n".format(round_string))
        prev_round = str(int(round_string)-1)
        round_df = NRLdata[NRLdata["Round Number"]==round_string]
        new_elos = {}
        new_elos_mod = {}
        for i,row in round_df.iterrows():
            results = [int(x) for x in row["Result"].replace(" ","").split("-")]
            print("Match:",row["Home Team"],"vs",row["Away Team"])
            print(results[0],"-",results[1])
            print("{0} won!".format(row["Home Team"])) if results[0] > results[1] else print("{0} won!".format(row["Away Team"]))
            # getNewElo(elo_rating, K, W, W_prob)
            teams = [row["Home Team"], row["Away Team"]]
            for j in range(2):
                team = teams[j]
                opponent = teams[j-1]
                prev_elo = df_elos.loc[team][prev_round]
                prev_elo_mod = df_elos_modified.loc[team][prev_round]
                prev_elo_opponent = df_elos.loc[opponent][prev_round]
                prev_elo_opponent_mod = df_elos_modified.loc[opponent][prev_round]
                if j==0:
                    home_away = "Home"
                else:
                    home_away = "Away"
                win_prob = getExpectedWinProb(prev_elo, prev_elo_opponent, home_away)
                win_prob_mod = getExpectedWinProb(prev_elo_mod, prev_elo_opponent_mod, home_away)
                print(team,"old rating:",prev_elo)
                print("Win prob:",win_prob)
                if results[j] > results[j-1]:
                    print("They won!")
                    won_match = 1
                else:
                    print("They lost!")
                    won_match = 0
                if (results[j] > results[j-1]) and (abs(results[j] - results[j-1]) >= 4):
                    print("They REALLY won!")
                    won_match_mod = 1
                elif (results[j] > results[j-1]) and (abs(results[j] - results[j-1]) < 4):
                    print("They effectively drew!")
                    won_match_mod = 0.5                
                elif (results[j] < results[j-1]) and (abs(results[j] - results[j-1]) < 4):
                    print("They effectively drew!")
                    won_match_mod = 0.5
                else:
                    print("They REALLY lost!")
                    won_match_mod = 0
                new_elos[team] = getNewElo(prev_elo, won_match, win_prob)
                new_elos_mod[team] = getNewElo(prev_elo_mod, won_match_mod, win_prob_mod)
        new_elos_df = pd.DataFrame.from_dict(new_elos, orient='index', columns=[round_string])
        new_elos_mod_df = pd.DataFrame.from_dict(new_elos_mod, orient='index', columns=[round_string])
        df_elos = df_elos.merge(new_elos_df, how='left', left_index=True, right_index=True).sort_values(by=round_string, ascending=False)
        df_elos_modified = df_elos_modified.merge(new_elos_mod_df, how='left', left_index=True, right_index=True).sort_values(by=round_string, ascending=False)
        print("Elo scores updated for round {}. \n".format(round_string))
    for col in df_elos.columns:
        if col=='0':
            continue
        df_elos[col] = df_elos[col].fillna(df_elos[str(int(col)-1)])
        df_elos_modified[col] = df_elos_modified[col].fillna(df_elos_modified[str(int(col)-1)])
    df_elos.to_csv(folder + "\\nrl-2022-eloratings.csv", index_label="Team")
    df_elos_modified.to_csv(folder + "\\nrl-2022-eloratings_modified.csv", index_label="Team")

if __name__ == "__main__":
    main()