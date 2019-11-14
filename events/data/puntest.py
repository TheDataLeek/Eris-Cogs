# test to see if I can call puns.csv the way I want
import csv

with open("puns.csv", newline="") as csvfile:
    # Puns.csv is arranged into two columns titled 'word' and 'response'
    punreader = csv.DictReader(csvfile, delimiter="|")
    # Make those columns two separate lists
    keywords = []
    response = []
    for row in punreader:
        keywords.append(row["word"])
        response.append(row["response"])
    cleanish_message = ["Everything", "is", "downhill", "for", "an", "addict"]
    # cleanish_message = ['Fuck', 'you']
    q = list(set(keywords) & set(cleanish_message))
    if q:
        print(q)
        print(response[keywords.index(q[0])])
    else:
        print("No keywords found")
