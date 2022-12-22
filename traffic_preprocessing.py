from datetime import datetime

def preprocess():
    f_out = open("traffic_accidents_2018_pp.csv", "w")
    f_out.write("Accident Number,Date and Time,Number of Motor Vehicles,Number of Injuries,Number of Fatalities,Property Damage,Hit and Run,Reporting Officer,Collision Type Code,Collision Type Description,Weather Code,Weather Description,Illumination Code,Illumination Description,Harmful Code,Harmful Code Description,Street Address,City,State,ZIP,RPA,Precinct,Latitude,Longitude,New Georeferenced Column,")
    f_out.write("Hour,Week,Month,Year\n")

    with open("dataset.csv", "r") as f:
        for i, line in enumerate(f.readlines()):
            if (i == 0): continue

            a = line.split(",")
            t = a[1]
            line = line.replace("\n", "")

            FORMAT_FROM = "%m/%d/%Y %I:%M:%S %p"
            FORMAT_TO = "%Y-%m-%d %H:%M:%S"

            hour = datetime.strftime(
                datetime.fromtimestamp(
                    int(datetime.timestamp(datetime.strptime(t, FORMAT_FROM)) % (24 * 60 * 60)) + 315532800
                    ), FORMAT_TO)
            
            week = datetime.strftime(
                datetime.fromtimestamp(
                    int(datetime.timestamp(datetime.strptime(t, FORMAT_FROM)) % (24 * 60 * 60 * 7)) + 315532800
                    ), FORMAT_TO)

            month = datetime.strftime(
                datetime.fromtimestamp(
                    int(datetime.timestamp(datetime.strptime(t, FORMAT_FROM)) % (24 * 60 * 60 * 30)) + 315532800
                    ), FORMAT_TO)

            year = datetime.strftime(
                datetime.fromtimestamp(
                    int(datetime.timestamp(datetime.strptime(t, FORMAT_FROM)) % (24 * 60 * 60 * 30 * 2000))
                    ), FORMAT_TO)

            f_out.write(f"{line},{hour},{week},{month},{year}\n")

    f_out.close()

if __name__ == "__main__":
    preprocess()