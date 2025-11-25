import csv
import json


purchase_dict = {}

with open('purchase_log.txt', 'r', encoding='utf-8') as file:
    for line in file:
        data = json.loads(line.strip())
        user = data.get("user_id")
        category = data.get("category")
        purchase_dict[user] = category


with (open('visit_log__1_.csv', 'r', encoding='utf-8') as file_visits,
      open('funnel.csv', "w", encoding='utf-8', newline='') as file_res):

    reader = csv.reader(file_visits)
    writer = csv.writer(file_res)

    writer.writerow(["user_id", "source", "category"])
    next(reader)

    for user_id, source in reader:
        if user_id in purchase_dict:
            writer.writerow([user_id, source, purchase_dict[user_id]])
