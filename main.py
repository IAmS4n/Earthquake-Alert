import math
import time

from data import get_list_eq
from utils import now, alarm

if __name__ == "__main__":
    latitude = None
    longitude = None

    max_dis = 0.75

    while True:
        max_mag = 0
        max_dis_scale = 0.
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

            dis = math.sqrt((longitude - round(eq["long"])) ** 2. + (latitude - round(eq["lat"])) ** 2.)
            if dis < max_dis:
                dis_scale = 1. - min(dis / max_dis, 1.)

                now_hour = ((year * 12 + month) * 31 + day) * 24 + hour
                now_minute = now_hour * 60 + minute

                eq_hour = ((eq["year"] * 12 + eq["month"]) * 31 + eq["day"]) * 24 + eq["hour"]
                eq_minute = eq_hour * 60 + eq["minute"]

                dif_min = abs(now_minute - eq_minute)

                dh = math.floor(dif_min / 60)
                dm = dif_min - dh * 60
                if dh <= 12:
                    print("[!] %f Earthquake, %d hour and %d minute ago" % (eq["mag"], dh, dm))
                    print("https://www.google.com/maps/place/@%f,%f,10z" % (eq["lat"], eq["long"]))
                    print(eq)

                if dif_min < 30:
                    max_mag = max(max_mag, eq["mag"])
                    max_dis_scale = dis_scale
        if max_mag > 0:
            print("!" * 50)
            print(max_mag)
            print("!" * 50)

            alarm(max_mag, max_dis_scale + 0.25)
            time.sleep(60 * 10)

        time.sleep(60)
