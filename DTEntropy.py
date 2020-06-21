import math
from asciitree import LeftAligned
import random


def find_entropy(attribute, target, data):
    distinct = {}

    if target:
        total = {}
    else:
        total = 0
    tl = None
    for v in data:
        l = v[attribute]
        if target:
            tl = v[target]
        if distinct.get(l) is None:
            if target:
                distinct[l] = {}
                total[l] = 0
                distinct[l][tl] = 0
            else:
                distinct[l] = 0
        if target:
            if distinct[l].get(tl) is None:
                distinct[l][tl] = 0
            distinct[l][tl] += 1
            total[l] += 1
        else:
            distinct[l] += 1
            total += 1
    if target:
        ent = {}
    else:
        ent = 0
    #
    all_distinct_keys = set()
    if target:
        for k, v in distinct.items():
            for k1, v1 in v.items():
                all_distinct_keys.add(k1)
        for d in all_distinct_keys:
            for k, v in distinct.items():
                if d not in v:
                    v[d] = 0
        for k, m in distinct.items():
            if ent.get(k) is None:
                ent[k] = 0
            for distinct_key in all_distinct_keys:
                # for o, p in m.items():
                # tot = sum([m[o] for s, m in distinct.items()])
                n = m[distinct_key] / total[k]
                if n > 0:
                    ent[k] += -n * math.log(n, 2)
    else:
        for k, m in distinct.items():
            n = m / total
            ent += -n * math.log(n, 2)

    total_count = len(data)
    if target:
        calc_ent = 0
        for j in ent.keys():
            calc_ent += (total[j] / total_count) * ent[j]
        return calc_ent, distinct
    return ent, distinct


def read_file(file_in):
    with open(file_in) as f:
        lines = f.readlines()

    data = []
    attributes = lines[0].strip().split(",")
    for v in range(1, len(lines)):
        a = {}
        vs = lines[v].strip().split(",")
        for i in range(0, len(attributes)):
            a[attributes[i]] = vs[i]
        data.append(a)
    return data, attributes


def split_data_and_decide(attribute, data, target, attributes_in, tree, entropies_in=None):
    if not tree:
        tree = {}
    tree[attribute] = {}
    for a in data:
        v = a[attribute]
        if not tree[attribute].get(v):
            tree[attribute][v] = {}
            tree[attribute][v]["data"] = []
        tree[attribute][v]["data"].append(a)
    t = tree[attribute]
    for d in t:
        cont = not entropies_in
        if not cont:
            cont = entropies_in[attribute] is not None and entropies_in[attribute] > 0
        # if cont:
        decision_tree(target, tree[attribute][d]["data"], attributes_in, t[d], d)
        del tree[attribute][d]["data"]
    return tree


def decision_tree(target, data, attributes_in, tree=None, current_attribute=None):
    class_entropy, class_counts = find_entropy(target, None, data)
    print("TARGET ({}) Entropy/Counts: {}/{}\n".format(target, class_entropy, class_counts))
    attribute_entropies = {}
    attribute_counts = {}
    for a in attributes_in:
        if a != target:
            attribute_entropies[a], attribute_counts[a] = find_entropy(a, target, data)
            print("{} Entropy/Counts: {}/{}".format(a, attribute_entropies[a], attribute_counts[a]))
    print("\n")
    # information gains
    max_info_gain = 0
    max_info_gain_attr = ""
    for a in attributes_in:
        if a != target:
            attribute_entropies[a], attribute_counts[a] = find_entropy(a, target, data)
            info_gain = class_entropy - attribute_entropies[a]
            if info_gain > max_info_gain:
                max_info_gain = info_gain
                max_info_gain_attr = a
            print("Information gain {}: {} ".format(a, info_gain))
    print("\n")
    print("Max Information gain {} with {} ".format(max_info_gain, max_info_gain_attr))
    print("\n")
    if not max_info_gain_attr:
        print("Leaf with {} \n===================================\n".format(
            current_attribute if current_attribute else target))
        assert len(set([i[target] for i in data])) < 2
        tree[target] = {data[0][target]: {}}
        return tree
    else:
        print("\n===================================\n")
    return split_data_and_decide(max_info_gain_attr, data, target, attributes_in, tree, attribute_entropies)


def test_tree(tree, row, target):
    for k, v in tree.items():
        ret = row[k]
        if k == target:
            return v.get(row[target]) is not None

        if ret in v:
            return test_tree(v[ret], row, target)
        else:
            return False
    return False


TARGET = "Covid-19 Teshisi"
file = 'corona.csv'
# TARGET = "play"
# file = 'weather.csv'
# file = 'contactlenses.csv'
data_in, attributes = read_file(file)
last = math.ceil(len(data_in) / 3 * 1)
# data_test = data_in[:last]
data_test = random.sample(data_in, last)
data_train = data_in  # [i for i in data_in if i not in data_test] + [j for j in data_test if j not in data_in]#[last:]
resulting_tree = decision_tree(TARGET, data_train, attributes)
# resulting_tree = decision_tree("play", data_train, attributes)
# resulting_tree = decision_tree("contact-lenses", data_train, attributes)
# print("{}".format(resulting_tree))
cnt_ok = 0
for i in data_test:
    if test_tree(resulting_tree, i, TARGET):
        cnt_ok += 1
print("Success {}".format((cnt_ok / len(data_test))))
tr = LeftAligned()
print("{}".format(tr(resulting_tree)))
