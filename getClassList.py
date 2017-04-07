import csv

variable = "registered"

def load_csv(fname):
    with open(fname, "rb") as f:
        reader = csv.DictReader(f)

        # initialize dictionary
        dict = {}

        # find all *variable* class combinations
        for row in reader:
            if row[variable] == "True":
                k = row['user_id']
                if k not in dict:
                    dict[k] = []

                dict[k].append(row['course_id'])

        # initialize classes dict
        classes = {}
        for key in dict:
            new_key = str(dict[key])
            if k not in classes:
                classes[new_key] = 0

            classes[new_key] += 1

        with open("class_list_" + variable + "_counts.csv", 'wb') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in classes.items():
                writer.writerow([key, value])

load_csv("full2017-02-08.csv")