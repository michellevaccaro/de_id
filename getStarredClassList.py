import csv

variable = "viewed"

def load_csv(fname):
    with open(fname, "rb") as f:
        reader = csv.DictReader(f)

        # initialize dictionary
        dict = {}

        # find all class combinations
        for row in reader:
            if row[variable] == "True":
                k = row['user_id']
                if k not in dict:
                    dict[k] = []

                dict[k].append(row['course_id'])

        # initialize classes dict
        classes = {}
        for key in dict:
            k = str(dict[key])
            if k not in classes:
                classes[k] = 0

            classes[k] += 1

        # scan list and flag entries
        # flagged = []
        # for k in classes:
        #     if classes[k] < 5:
        #         flagged.append(k)


        with open("class_list_" + variable + "_starred.csv", 'wb') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in classes.items():
                if classes[key] < 5:
                    writer.writerow([key, value])

load_csv("full2017-02-08.csv")