# url that i use to get my footy results and fixtures https://fixturedownload.com/download/nrl-2023-UTC.csv
import requests
import os

def get_nrl_data():
    folder = os.path.dirname(os.path.realpath(__file__))
    print(folder)
    url = "https://fixturedownload.com/download/nrl-2023-EAustraliaStandardTime.csv"
    print("Fetching data...")
    r = requests.get(url, verify=True)
    text = r.iter_lines()
    with open(folder + "\\nrl-2023-EAustraliaStandardTime.csv", "w") as f:
        for line in text:
            line = str(line).strip("\'").strip("b\'")
            print(line)
            f.write(line + "\n")
    print("All done!")
    return

if __name__ == "__main__":
    get_nrl_data()