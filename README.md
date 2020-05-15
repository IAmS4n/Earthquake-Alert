# Earthquake Alert
This script checks near earthquakes **in Iran** using the Iranian Seismological Center. The audio alert is prepared for raspberry pi.

[Foreshock activity has been detected for about 40% of all moderate to large earthquakes, and about 70% for events of M>7.0.](https://en.wikipedia.org/wiki/Foreshock#Occurrence) So, Awareness of small earthquakes can be effective.

## Running on Raspberry Pi
1. Connect an external speaker to Raspberry Pi.
2. Install requirements:
    ~~~
    pip3 install -r requirements.txt
    ~~~
3. Set latitude and longitude in the `main.py` file.
4. Check the accuracy of your Raspberry Pi Clock using the `date` command.
5. Run the `main.py` .