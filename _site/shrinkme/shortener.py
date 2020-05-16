"""
GET https://shrinkme.io/api?api=73935256bd1d27be538ab113cb9b065e8e5e5fa9&url=yourdestinationlink.com&alias=CustomAlias

return JSON
{"status":"success","shortenedUrl":"https:\/\/shrinkme.io\/xxxxx"}
"""
import requests
API = "73935256bd1d27be538ab113cb9b065e8e5e5fa9"


def log_links(response, url):
    col1 = response["shortenedUrl"]
    col2 = url
    with open("url_logs.csv", "a") as f:
        if response["status"].lower() == "success":
            f.write(col1+","+col2+"\n")


def shorten(dest_link):
    API = "73935256bd1d27be538ab113cb9b065e8e5e5fa9"
    url2 = f"https://shrinkme.io/api?api=73935256bd1d27be538ab113cb9b065e8e5e5fa9&url={dest_link}"
    url = f"https://shrinkme.io/api"
    params = {'api': API, 'url': dest_link, }
    r = requests.get(url, params=params)
    print(r.url)
    print(url2)
    response = r.json()
    log_links(response, dest_link)
    print(response)


if __name__ == '__main__':
    from argparse import ArgumentParser
    ps = ArgumentParser()
    ps.add_argument('-l', action='store', dest='s_url',
                    help="Url to shorten", type=str)
    pargs = ps.parse_args()
    shorten(pargs.s_url)
