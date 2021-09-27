import requests
import urllib3
http = urllib3.PoolManager()
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
from io import BytesIO
import PIL.Image as Image
from html.parser import HTMLParser
from html.entities import name2codepoint
import os, sys, re
from tqdm import tqdm
import string
import argparse


parser = argparse.ArgumentParser(description='Google image scraper')
parser.add_argument("-p","--path", type=str,help="Path to store images")
parser.add_argument("-q","--query", type=str,help="name of image to scrape")
args = parser.parse_args()

class SrcExtractor(HTMLParser):
    src = []
    def handle_starttag(self, tag, attrs):
        if tag == "img":
            for each in attrs:
                if each[0] == "data-src":
                  # print(each[1])
                  self.src.append(each[1])

src_extractor = SrcExtractor()

headers = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    } 

#----------------------------------------------------------------------------------



def get_images(search, limit=-1, suffix="", prefix=""):
    # Make a directory to store the images
    try:
        os.mkdir(search)
    except:
        pass

  # Create the URL
    if suffix != "" and suffix[-1] != " ":
        suffix = " " + suffix
    if prefix != "" and prefix[0] != " ":
        prefix += " "

    query = f"{prefix}{search}{suffix}".strip()
    url = f"https://www.google.com/search?tbm=isch&q={query}"
    url = re.sub(' ', "%20", url)
    # print(url)

    # Get the source code for the webpage and store src attrib of img tags
    response = requests.request("GET", url, headers=headers)
    src_extractor.src = [] 
    src_extractor.feed(response.text)
    len_src = len(src_extractor.src)

  # Look through the collected src URLs and collect the images
    count = 0
    for each_src in src_extractor.src[:limit]:
        response = http.request('GET', each_src)

        try:
            img_data = BytesIO(response.data)
            image = Image.open(img_data).convert("RGBA")
            image.save(f"{search}/{count+1}.png")
        except:
            pass

        count+=1



if __name__ == "__main__":
        os.chdir(args.path)
        get_images(args.query)
        print("'{}' has been scraped and stored in {}/{}".format(args.query,args.path,args.query))



