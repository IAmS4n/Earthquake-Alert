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

        eq_mag = None
        eq_long = None
        eq_lat = None
        eq_date = None

        for x in row:
            if x.tag == "mag":
                eq_mag = x.text
            elif x.tag == "long":
                eq_long = x.text
            elif x.tag == "lat":
                eq_lat = x.text
            elif x.tag == "date":
                eq_date = x.text

        if (eq_long is not None) and (eq_lat is not None) and (eq_date is not None):
            tmp = {}
            tmp["mag"] = float(eq_mag)
            tmp["long"] = float(eq_long.split(" ")[0])
            tmp["lat"] = float(eq_lat.split(" ")[0])

            ymd, hms = eq_date.split(" ")
            tmp["year"], tmp["month"], tmp["day"] = map(int, ymd.split("/"))
            tmp["hour"], tmp["minute"] = map(int, hms.split(":")[:2])

            res.append(tmp)

    return res
