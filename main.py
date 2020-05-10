import os
import time
from datetime import datetime
from xml.etree import ElementTree as etree

import pytz
import requests
from gtts import gTTS


def get_list_eq():
    url = "http://irsc.ut.ac.ir/events_list_fa.xml"
    xml = None
    while xml is None:
        try:
            xml = requests.get(url, timeout=120).content.decode('utf-8')
        except Exception as e:
            print("type error: " + str(e))
            
    reddit_root = etree.fromstring(xml)

    res = []
    for row in reddit_root:

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


def now():
    # https://github.com/slashmili/python-jalali/blob/master/jdatetime/jalali.py

    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]

    tz = pytz.timezone('Asia/Tehran')
    tehran_dt = datetime.now(tz)  # UTC time
    dt = tehran_dt.astimezone()  # local time
    gmonth, gday, gyear, hour, minute = map(int, dt.strftime("%m/%d/%Y/%H/%M").split("/"))

    gy = gyear - 1600
    gm = gmonth - 1
    gd = gday - 1

    g_day_no = 365 * gy + (gy + 3) // 4 - (gy + 99) // 100 + (gy + 399) // 400

    for i in range(gm):
        g_day_no += g_days_in_month[i]
    if gm > 1 and ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
        # leap and after Feb
        g_day_no += 1
    g_day_no += gd

    j_day_no = g_day_no - 79

    j_np = j_day_no // 12053
    j_day_no %= 12053
    jy = 979 + 33 * j_np + 4 * int(j_day_no // 1461)

    j_day_no %= 1461

    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    for i in range(11):
        if not j_day_no >= j_days_in_month[i]:
            i -= 1
            break
        j_day_no -= j_days_in_month[i]

    jm = i + 2
    jd = j_day_no + 1

    return jy, jm, jd, hour, minute


def say_text(text):
    myobj = gTTS(text=text, lang="en", slow=False)
    myobj.save("./eq_tmp.mp3")

    for _ in range(3):
        os.system("omxplayer -o local alarm.mp3")
        os.system("omxplayer --vol 500 -o local eq_tmp.mp3")
        time.sleep(10)


if __name__ == "__main__":

    Tehran_Latitude = 35.715298
    Tehran_Longitude = 51.404343

    min_long = Tehran_Longitude - 2
    max_long = Tehran_Longitude + 2
    min_lat = Tehran_Latitude - 2
    max_lat = Tehran_Latitude + 2

    while True:
        max_mag = 0
        year, month, day, hour, minute = now()
        print(year, month, day, hour, minute)
        for eq in get_list_eq():
            if eq["year"] == year and eq["month"] == month and eq["day"] == day:
                if (min_long < eq["long"] < max_long) and (min_lat < eq["lat"] < max_lat):
                    dif_min = abs((hour * 60 + minute) - (eq["hour"] * 60 + eq["minute"]))
                    if dif_min <= 31:
                        max_mag = max(max_mag, eq["mag"])
        if max_mag > 0:
            print("!!!", max_mag)
            say_text("Earthquake, magnitude is %.1f" % max_mag)

        time.sleep(60 * 5)
