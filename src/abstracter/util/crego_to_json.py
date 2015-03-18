#!/usr/bin/python3
import re
import json

def crego_to_json(file):
    data = []
    with open(file, "r") as f:
        for line in f:
            for word in line.split(" "):
                word_details = word.split("-|-")

                tags = {"relations":[]}
                for t in word_details[3].split(";"):
                    r = re.match(r"(.+)=(.+)", t)
                    if r is not None:
                        v = r.group(2)
                        if v[0] == '@':
                            v = int(v[1:])
                        tags[r.group(1)] = v
                    else:
                        x = map(int, t.split("_@_"))
                        tags["relations"].append(tuple(x))

                data.append({
                    "id": len(data),
                    "name": word_details[0],
                    "norm": word_details[1],
                    "type": word_details[2],
                    "tags": tags
                })

    return data

if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    data = crego_to_json(file)
    print(json.dumps(data))
