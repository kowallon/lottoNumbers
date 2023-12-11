from bs4 import BeautifulSoup
import requests
from collections import Counter

response = requests.get("https://megalotto.pl/wyniki/lotto-plus/100-ostatnich-losowan")


soup = BeautifulSoup(response.text, "html.parser")

numbers = soup.find_all(class_="numbers_in_list")
all_scores = []
# Appending each scraped number into list
for number in numbers:
    all_scores.append(int(number.text))


# Each draw has 6 numbers, so I divide all_scores list into lists of 6 numbers. Each list is different draw from past
sublists = []

for i in range(0, len(all_scores), 6):
    sublist = all_scores[i:i + 6]
    sublists.append(sublist)

number_counts = Counter(all_scores)

# for number, count in number_counts.items():
#     print(f"Number {number} occurec {count} times")

first_occurrence_indices = {}

#print(number_counts)
for i, sublist in enumerate(sublists):
    # Iterate through the elements in the sublist
    for j, number in enumerate(sublist):
        # Check if the number is in the dictionary
        if number not in first_occurrence_indices:
            # Store the index of the first occurrence
            first_occurrence_indices[number] = (i, j)


# for number, indices in first_occurrence_indices.items():
#     print(f"Number {number}: First occurrence at index {indices[0]}")

#Adding data to google sheet
sheet = requests.get("https://api.sheety.co/de54cdbc4e5e602184d9bec61caedf66/lotto/arkusz1")
sheet_data = sheet.json()['arkusz1']
print(sheet_data)

# for row in sheet_data:
#     #print(row['id'])
#     print(row)

# Fill occurrances column
for number,count in number_counts.items():
    for row in sheet_data:
        if row['numer'] == number:
            body = {
                'arkusz1': {
                    'wystąpienia': count
                }
            }
            requests.put(f"https://api.sheety.co/de54cdbc4e5e602184d9bec61caedf66/lotto/arkusz1/{row['id']}", json=body)

# Fill frequency column - on average how often each number is drawn

for data_row in sheet_data:
    try:
        frequency = 100/int(data_row['wystąpienia'])
    except:
        frequency = 0
    finally:
        body = {
            'arkusz1': {
                'frequency': round(frequency,2)
            }
        }
        requests.put(f"https://api.sheety.co/de54cdbc4e5e602184d9bec61caedf66/lotto/arkusz1/{data_row['id']}",
                     json=body)

# Fill last time column - when was the last time number was drawn

for number, indeces in first_occurrence_indices.items():
    for row in sheet_data:
        if row['numer'] == number:
            body = {
                'arkusz1': {
                    'last': indeces[0]
                }
            }
            requests.put(f"https://api.sheety.co/de54cdbc4e5e602184d9bec61caedf66/lotto/arkusz1/{row['id']}", json=body)


# The idea is that if certain number is on average drawn every 9 draws and last time it was drawn 8 draws ago, then
# there's a decent chance, that it will be drawn in the upcoming draw, so I deduct last from frequency and take abs val

for data in sheet_data:
    chance = float(data['frequency']) - float(data['last'])
    print(f"numer {data['numer']} {round(abs(chance),2)}")
    body = {
        'arkusz1': {
            'chance': round(abs(chance),2)
        }
    }
    requests.put(f"https://api.sheety.co/de54cdbc4e5e602184d9bec61caedf66/lotto/arkusz1/{data['id']}", json=body)



