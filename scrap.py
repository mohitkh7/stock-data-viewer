import re
import redis
import json
import os
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile


def scrap():
    """
    Scraps latest copy of equity bhaav from bseindia websites
    and parse csv file scrapped to store result in redis DB
    """
    URL = "https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx"

    print("Fetching Data ...")
    try:
        # db = redis.from_url(os.environ.get("REDIS_URL"))
        db = redis.Redis()
        stock_count = 0
        website = urlopen(URL)
        if website.status == 200:
            # Read HTML content of weblink
            html = website.read().decode('utf-8')

            # Search for given pattern URL
            pattern = '"(http://www.bseindia.com/download/BhavCopy/Equity/.*?)"'
            links = re.findall(pattern, html)

            # Download and extract zip file
            response = urlopen(links[0])
            zipfile = ZipFile(BytesIO(response.read()))

            # Reset db to avoid multiple writes
            db.delete("data");        
            for csvfilename in zipfile.namelist():
                # Read csv file and store stock data to db as json string
                for line in zipfile.open(csvfilename).readlines()[1:]:
                    arr = line.decode('utf-8').split(",")
                    dic = {
                        "CODE": arr[0],
                        "NAME": arr[1],
                        "OPEN": arr[4],
                        "HIGH": arr[5],
                        "LOW": arr[6],
                        "CLOSE": arr[7],
                    }
                    stock_count += 1
                    json_string = json.dumps(dic)
                    db.sadd("data", json_string)
            print("Data write Complete");
            return stock_count
        else:
            print("Website not reachable")
            return stock_count

    except Exception as e:
        print(e)
        print("Error while fetching data")
        return 0


if __name__ == "__main__":
    scrap()