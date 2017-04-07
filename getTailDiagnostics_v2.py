import csv

variable = "registered"

def delete_entries(fname):
    master_dict = make_dict(fname)
    classes = get_classes(fname)
    count = 0
    while not is_k_anon(master_dict):
        # print master_dict
        delete_class(classes, master_dict)
        count += 1
    print count


def delete_class(classes, master_dict):
    # print classes
    x = get_min_class(classes)
    classes.pop(x)
    # print classes

    for k in master_dict.keys():
        temp = string_to_list(k)
        # print temp
        if x in k and x in temp:
            temp.remove(x)
            new_str = str(temp)
            master_dict.pop(k)
            if not new_str == '[]':
                if new_str in master_dict:
                    master_dict[new_str] += 1
                else:
                    master_dict[new_str] = 1


def get_min_class(classes):
    min = 9999999
    c = ''
    for k in classes:
        if classes[k] < min:
            min = classes[k]
            c = k
    print c, min
    return c


# tested
def is_k_anon(dict):
    for key in dict:
        if dict[key] < 5:
            return False
    return True


# tested
def make_dict(fname):
    with open(fname, "rb") as f:
        reader = csv.reader(f)

        my_dict = {}
        for row in reader:
            key = row[0]
            val = int(row[1])
            my_dict[key] = val
        return my_dict


# tested
def get_classes(fname):
    with open(fname, "rb") as f:
        reader = csv.reader(f)

        count = 0
        class_dict = {}
        for row in reader:
            classes = string_to_list(row[0])
            for c in classes:
                if c not in class_dict:
                    class_dict[c] = int(row[1])
                else:
                    class_dict[c] += 1
        return class_dict


def get_max_length(master_dict):
    max = 0
    for k in master_dict.keys():
        temp = len(string_to_list(k))
        if temp > max:
            max = temp
    return max


def get_min_length(master_dict):
    min = 100
    for k in master_dict.keys():
        temp = len(string_to_list(k))
        if temp < min:
            min = temp
    return min


def get_avg_length(master_dict):
    sum = 0
    count = 0
    for k in master_dict.keys():
        sum += len(string_to_list(k))
        count += 1
    return float(sum)/count


def string_to_list(str):
    new_list = []
    items = str.split()
    for j in items:
        j = j.translate(None, '[],')
        new_list.append(j.translate(None, "'[],'"))
    return new_list

print get_max_length(make_dict("class_list_" + variable + "_starred.csv"))
print get_min_length(make_dict("class_list_" + variable + "_starred.csv"))
print get_avg_length(make_dict("class_list_" + variable + "_starred.csv"))
# print is_k_anon(make_dict("test.csv"))
# delete_entries("test.csv")
# delete_entries("class_list_" + variable + "_starred.csv")
# get_min_class({"chem": 5, "bio": 2, "math": 1})