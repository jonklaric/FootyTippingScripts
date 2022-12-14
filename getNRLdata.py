# url that i use to get my footy results and fixtures from
import requests
import os

def getNRLdata():
    folder = os.path.dirname(os.path.realpath(__file__))
    print(folder)
    url = "https://fixturedownload.com/download/nrl-2022-UTC.csv"
    print("Fetching data...")
    r = requests.get(url)
    text = r.iter_lines()
    with open(folder + "\\nrl-2022-EAustraliaStandardTime.csv", "w") as f:
        for line in text:
            line = str(line).strip("\'").strip("b\'")
            print(line)
            f.write(line + "\n")
    print("All done!")

if __name__ == "__main__":
    getNRLdata()