import time
from xml.etree import ElementTree as etree

import requests


def get_list_eq():
    url = "http://irsc.ut.ac.ir/events_list_fa.xml"
    xml = None
    while xml is None:
        try:
            xml = requests.get(url, timeout=120).content.decode('utf-8')
        except Exception as e:
            print("requests error: " + str(e))
            time.sleep(30)

    res = []
    for row in etree.fromstring(xml):
        tmp = {x.tag: x.text for x in row}

        try:
            tmp["mag"] = float(tmp["mag"])
            tmp["long"] = float(tmp["long"].split(" ")[0])
            tmp["lat"] = float(tmp["lat"].split(" ")[0])

            ymd, hms = tmp["date"].split(" ")
            tmp["year"], tmp["month"], tmp["day"] = map(int, ymd.split("/"))
            tmp["hour"], tmp["minute"] = map(int, hms.split(":")[:2])

            res.append(tmp)
        except:
            pass

    return res


if __name__ == "__main__":
    print(get_list_eq())
