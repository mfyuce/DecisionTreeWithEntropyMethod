import math
from asciitree import LeftAligned
import random


def find_initial_entropy(target, data):
    distinct = {}
    total = 0
    for v in data:
        attr_value = v[target]
        if distinct.get(attr_value) is None:
            distinct[attr_value] = 0
        distinct[attr_value] += 1
        total += 1

    ent = 0
    for attr, cnt in distinct.items():
        n = cnt / total
        ent += -n * math.log(n, 2)

    return ent, distinct


def find_entropy(attribute, target, data):
    distinct = {}

    total = {}
    for target_values in data:
        attr_value = target_values[attribute]
        target_value = target_values[target]
        if distinct.get(attr_value) is None:
            distinct[attr_value] = {}
            total[attr_value] = 0
            distinct[attr_value][target_value] = 0
        if distinct[attr_value].get(target_value) is None:
            distinct[attr_value][target_value] = 0
        distinct[attr_value][target_value] += 1
        total[attr_value] += 1
    ent = {}
    all_distinct_keys = set()
    for attr, target_values in distinct.items():
        for target_value, target_value_count in target_values.items():
            all_distinct_keys.add(target_value)
    for target_value_count in all_distinct_keys:
        for attr, target_values in distinct.items():
            if target_value_count not in target_values:
                target_values[target_value_count] = 0
    for attr, target_values in distinct.items():
        if ent.get(attr) is None:
            ent[attr] = 0
        for distinct_key in all_distinct_keys:
            # for o, p in target_values.items():
            # tot = sum([target_values[o] for s,
            # target_values in distinct.items()])
            n = target_values[distinct_key] / total[attr]
            if n > 0:
                ent[attr] += -n * math.log(n, 2)

    total_count = len(data)
    calc_ent = 0
    for j in ent.keys():
        calc_ent += (total[j] / total_count) * ent[j]
    return calc_ent, distinct


def read_file(file_in):
    with open(file_in) as f:
        lines = f.readlines()

    data = []
    attributes = lines[0].strip().split(",")
    for v in range(1, len(lines)):
        vs_t = lines[v].strip()
        if vs_t:
            vs = vs_t.split(",")
            a = {}
            for i in range(0, len(attributes)):
                a[attributes[i]] = vs[i]
            data.append(a)
    return data, attributes


def split_data_and_decide(attribute,
                          data,
                          target,
                          attributes_in,
                          collected_attributes_in,
                          tree,
                          entropies_in=None):
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
    collected_attributes_in.append(attribute)
    for d in t:
        cont = not entropies_in
        if not cont:
            cont = entropies_in[attribute] is not None \
                   and entropies_in[attribute] > 0
        # if cont:
        decision_tree(target,
                      tree[attribute][d]["data"],
                      attributes_in,
                      collected_attributes_in,
                      t[d],
                      d)
        del tree[attribute][d]["data"]
    return tree


def decision_tree(target,
                  data,
                  attributes_in,
                  collected_attributes_in=None,
                  tree=None,
                  current_attribute=None):
    if not collected_attributes_in:
        collected_attributes_in = []
    class_entropy, class_counts = find_initial_entropy(target, data)
    print("TARGET ({}) Entropy/Counts: {}/{}\n"
          .format(target, class_entropy, class_counts))
    attribute_entropies = {}
    attribute_counts = {}
    attr_difference = set(attributes_in).difference(collected_attributes_in)
    for a in attr_difference:
        if a != target:
            attribute_entropies[a], attribute_counts[a] \
                = find_entropy(a, target, data)
            print("{} Entropy/Counts: {}/{}"
                  .format(a, attribute_entropies[a], attribute_counts[a]))
    print("\n")
    # information gains
    max_info_gain = 0
    max_info_gain_attr = ""
    for a in attr_difference:
        if a != target:
            attribute_entropies[a], attribute_counts[a] \
                = find_entropy(a, target, data)
            info_gain = class_entropy - attribute_entropies[a]
            if info_gain > max_info_gain:
                max_info_gain = info_gain
                max_info_gain_attr = a
            print("Information gain {}: {} ".format(a, info_gain))
    print("\n")
    print("Max Information gain {} with {} "
          .format(max_info_gain, max_info_gain_attr))
    print("\n")
    if not max_info_gain_attr:
        print("Leaf with {} \n===================================\n"
            .format( current_attribute if current_attribute else target))
        # assert len(set([i[target] for i in data])) < 2
        tree[target] = {data[0][target]: {}}
        return tree
    else:
        print("\n===================================\n")
    return split_data_and_decide(max_info_gain_attr,
                                 data,
                                 target,
                                 attributes_in,
                                 collected_attributes_in,
                                 tree,
                                 attribute_entropies)


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


# Set 1
TARGET = "Covid-19 Teshisi"
file = 'corona.csv'

# Set 2 https://medium.com/coinmonks/what-is-entropy-and-why-information-gain-is-matter-4e85d46d2f01
# TARGET = "Speed"
# file = 'self_driving_car.csv'
# TARGET = "play"
# file = 'weather.csv'
# file = 'weather_v2.csv'
# file = 'weather_v3.csv'
# file = 'contactlenses.csv'
# TARGET='Infected'
# file = 'covid.csv'
# TARGET='class'
# file = 'iris.csv'
data_in, attributes_in = read_file(file)
last = math.ceil(len(data_in) / 3 * 1)
# data_test = data_in[:last]
data_test = random.sample(data_in, last)
data_train = data_in
# data_train = [i for i in data_in if i not in data_test] + [j for j in data_test if j not in data_in]#[last:]
resulting_tree = decision_tree(TARGET, data_train, attributes_in)
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
