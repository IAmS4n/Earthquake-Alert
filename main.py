import os
import time
from datetime import datetime
from xml.etree import ElementTree as etree
import math

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
            print("requests error: " + str(e))
            time.sleep(30)
            
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
    for voice_try in range(100):
        try:
            myobj = gTTS(text=text, lang="en", slow=False)
            myobj.save("./eq_tmp.mp3")
            break
        except Exception as e:
            print("say_text error: " + str(e))
            if voice_try%10==0:
                os.system("omxplayer -o local alarm.mp3")
        time.sleep(10)

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
        print("%d/%d/%d" % (year, month, day), "%d:%d" % (hour, minute))

        eq_data = None
        while eq_data is None:
            try:
                eq_data = get_list_eq()
            except Exception as e:
                print("get_list_eq error: " + str(e))
                time.sleep(5)

        for eq in eq_data:
            if (min_long < eq["long"] < max_long) and (min_lat < eq["lat"] < max_lat):

                now_hour = ((year*12 + month)*30 + day)*24 + hour
                now_minute = now_hour*60 + minute

                eq_hour   = ((eq["year"]*12 + eq["month"])*30 + eq["day"])*24 + eq["hour"]
                eq_minute = eq_hour*60 + eq["minute"]

                dif_min = abs(now_minute - eq_minute)

                dh = math.floor(dif_min/60)
                dm = dif_min - dh*60
                if dh<=12:
                    print("[!] %f Earthquake, %d hour and %d minute ago" % (eq["mag"], dh, dm))

                if dif_min < 30:
                    max_mag = max(max_mag, eq["mag"])
        if max_mag > 0:
            print("!" * 50)
            print(max_mag)
            print("!" * 50)
            
            say_text("Earthquake. Magnitude is %.1f" % max_mag)
            time.sleep(60 * 10)

        time.sleep(60)
