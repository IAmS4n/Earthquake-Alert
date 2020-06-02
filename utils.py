import math
import os
import time
from datetime import datetime

import pytz
from gtts import gTTS


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


def alarm(magnitude, volume):
    assert 0.05 <= volume <= 2.
    param = round(2000 * (math.log(float(volume))))

    for voice_try in range(100):
        try:
            myobj = gTTS(text="Earthquake. Magnitude is %.1f" % magnitude, lang="en", slow=False)
            myobj.save("./eq_tmp.mp3")
            break
        except Exception as e:
            print("say_text error: " + str(e))
            if voice_try % 10 == 0:
                os.system("omxplayer --vol %d -o local alarm.mp3" % param)
        time.sleep(10)

    for _ in range(3):
        os.system("omxplayer --vol %d -o local alarm.mp3" % param)
        os.system("omxplayer --vol %d -o local eq_tmp.mp3" % param)
        time.sleep(10)
