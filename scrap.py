from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import re
import requests
import redis
import json


def scrap():
    print("Fetching Data ...")
    try:
        db = redis.from_url(os.environ.get("REDIS_URL"))
        stock_count = 0
        URL = "https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx"
        website = urlopen(URL)
        if website.status == 200:
            html = website.read().decode('utf-8')
            pattern = '"(http://www.bseindia.com/download/BhavCopy/Equity/.*?)"'
            links = re.findall(pattern, html)

            response = urlopen(links[0])

            zipfile = ZipFile(BytesIO(response.read()))
            db.delete("data");        
            for csvfilename in zipfile.namelist():
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
            print("Data write Completed");
            return stock_count
        else:
            print("Website not reachable")
            return stock_count
    except:
        print("Error while fetching data")
        return 0


if __name__ == "__main__":
    scrap()