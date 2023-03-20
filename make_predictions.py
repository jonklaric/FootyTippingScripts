
import pandas as pd
import numpy as np
from datetime import datetime
import os
import shutil


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


folder = os.path.dirname(os.path.realpath(__file__))

NRLdata = pd.read_csv(folder + "\\nrl-2023-EAustraliaStandardTime.csv")
NRLdata["Round"] = NRLdata["Round Number"]
#NRLdata["Round"] = NRLdata["Round Number"].apply(lambda x: int(x) if "Final" not in x else -1)
NRLdata["Datetime"] = NRLdata["Date"].apply(lambda x: datetime.strptime(x, "%d/%m/%Y %H:%M"))

df_elos = pd.read_csv(folder + "\\nrl-2023-eloratings.csv", index_col="Team")
df_elos_modified = pd.read_csv(folder + "\\nrl-2023-eloratings_modified.csv", index_col="Team")
for col in df_elos.columns:
    if col=='0':
        continue
    df_elos[col] = df_elos[col].fillna(df_elos[str(int(col)-1)])
    df_elos_modified[col] = df_elos_modified[col].fillna(df_elos[str(int(col)-1)])
round_num = max([int(x) for x in df_elos.columns])+1
print(set(NRLdata["Round"]))
print(NRLdata)
NRLrounddata = NRLdata[NRLdata["Round"] == round_num]
round_string = str(round_num-1)

print(NRLrounddata)

print("Generating footy tips for round {0}".format(round_num))
probs = []
output_filename = "\\nrl-2023-round_{0}.txt".format(round_num)
with open(folder + output_filename, "w") as f:
    print("Generating footy tips for round {0}".format(round_num), file=f)
    for i,row in NRLrounddata.iterrows():
        print("\t",row["Home Team"], "vs", row["Away Team"], file=f)
        home_team_elo = df_elos[round_string][row["Home Team"]]
        home_team_mod_elo = df_elos_modified[round_string][row["Home Team"]]
        away_team_elo = df_elos[round_string][row["Away Team"]]
        away_team_mod_elo = df_elos_modified[round_string][row["Away Team"]]
        print("Regular Elo:\t", home_team_elo, "vs", away_team_elo, file=f)
        print("Modified Elo:\t", home_team_mod_elo, "vs", away_team_mod_elo, file=f)
        if home_team_elo > away_team_elo:
            stronger_team = row["Home Team"]
        else:
            stronger_team = row["Away Team"]
        if home_team_mod_elo > away_team_mod_elo:
            mod_stronger_team = row["Home Team"]
        else:
            mod_stronger_team = row["Away Team"]
        print("Based on the Elo scores, {0} are the \'stronger\' team.".format(stronger_team), file=f)
        print("Based on the Modified Elo scores, {0} are the \'stronger\' team.".format(mod_stronger_team), file=f)
        if row["Home Team"] != "Warriors":
            win_prob_home = getExpectedWinProb(home_team_elo,away_team_elo, "Home")
            win_prob_away = getExpectedWinProb(away_team_elo, home_team_elo, "Away")
            win_prob_home_mod = getExpectedWinProb(home_team_mod_elo, away_team_mod_elo, "Home")
            win_prob_away_mod = getExpectedWinProb(away_team_mod_elo, home_team_mod_elo, "Away")
        else:
            win_prob_home = getExpectedWinProb(home_team_elo, away_team_elo, "")
            win_prob_away = getExpectedWinProb(away_team_elo, home_team_elo, "")
            win_prob_home_mod = getExpectedWinProb(home_team_mod_elo, away_team_mod_elo, "")
            win_prob_away_mod = getExpectedWinProb(away_team_mod_elo, home_team_mod_elo, "")
        print("Win probabilities:",np.round(win_prob_home,3),"vs", np.round(win_prob_away,3), file=f)
        print("Win probs (modified):",np.round(win_prob_home_mod,3),"vs", np.round(win_prob_away_mod,3), file=f)
        if win_prob_home_mod > 0.5:
            tip = row["Home Team"]
            probs.append(min(win_prob_home,win_prob_home_mod))
        else:
            tip = row["Away Team"]        
            probs.append(min(win_prob_away,win_prob_away_mod))
        print("\t *** Team to Tip: {0}. *** \n".format(tip), file=f)

shutil.copy(folder + output_filename, "C:\\Users\\jonkl\\Desktop" + output_filename)


N = 100000
x = np.random.random((len(probs), N))
y = np.zeros((len(probs), N))
for i in range(len(probs)):
    win = [1 if k <= probs[i] else 0 for k in x[i]]
    y[i] = win

wins = np.zeros(N)
for k in range(N):
    wins[k] = sum(y[:,k])
print("Expected wins:",np.mean(wins))

import matplotlib.pyplot as plt


plt.hist(wins,bins=[-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5], density=True)
plt.plot([np.mean(wins)], [0.3], marker='x', color='red')
plt.title("Round {0} expected wins = {1}".format(round_num, np.mean(wins)))
plt.show()
