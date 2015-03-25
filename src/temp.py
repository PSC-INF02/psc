import re
import json
import os.path


def check():
    tags = {}
    types = {}
    dossier = "../systran/2015_01_29/"
    i = 0
    j = 0
    while(os.path.exists(dossier + i.__str__()+"/"+j.__str__()+".clean.wsd.linear")):
        j = 0
        while(os.path.exists(dossier + i.__str__()+"/"+j.__str__()+".clean.wsd.linear")):
            with open(dossier + i.__str__()+"/"+j.__str__()+".clean.wsd.linear", "r") as f:
                for line in f:
                    for word in line.split(" "):
                        word_details = word.split("-|-")
                        for t in word_details[3].split(";"):
                            r = re.match(r"(.+)=(.+)", t)
                            if r is not None:
                                v = r.group(2)
                                if v[0] == '@':
                                    v = int(v[1:])
                                # if r.group(1) not in tags:
                                #     tags[r.group(1)] = None
                                # if v == "1" and r.group(1) not in tags:
                                #    tags.append(r.group(1))
                                if v == "1" and r.group(1) not in tags:
                                    tags[r.group(1)] = {"keep": True, "cor": r.group(1).upper(), "is_rel": False, "example": word_details[0]}
                                else:
                                    if type(v) == int and r.group(1) not in tags:
                                        tags[r.group(1)] = {"keep": True, "cor": r.group(1).upper(), "is_rel": True, "example": word_details[0]}
                                #    if (v== "1" or type(v)==int) and len(tags[r.group(1)]) < 5:
                                #        tags[r.group(1)].append(word_details[0])
                                #     tags[r.group(1)] = word_details[0]
                                # if type(v) == int and r.group(1) not in tags:
                                #    tags[r.group(1)] = v
                                #    tags.append(r.group(1))
                            else:
                                x = map(int, t.split("_@_"))
                                # tags["relations"].append(tuple(x))
                        if word_details[2] not in types:
                            types[word_details[2]] = word_details[1]
            j += 1
        i += 1
    with open("types.json", "w") as file:
        json.dump([(i) for i in sorted(types)], file)
    with open("tags.txt", "w") as file:
        file.write("{\n")
        for i in sorted(tags):
            # file.write("\"%s\": " + tags[i].__str__() + ",\n")
            # print(tags[i]["is_rel"])
            # file.write("\"%s\": {\"keep\": True, \"cor\": \"%s\"},\n" % (i, i.upper()))
            file.write("\"%s\": {\"keep\": True, \"cor\": \"%s\", \"is_rel\": %s},\n" % (i, i.upper(), tags[i]["is_rel"].__str__()))
            # file.write("\"%s\": {\"keep\": True, \"cor\": \"%s\", \"examples\": %s},\n" % (i, i.upper(), tags[i].__str__()))
        file.write("}")
        # json.dump([(i,{"keep": True, "cor": i.upper(), "examples": tags[i]}) for i in sorted(tags)], file)

check()