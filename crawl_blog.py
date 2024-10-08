import re
from bs4 import BeautifulSoup
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Ignore insecure request warnings
warnings.simplefilter('ignore', InsecureRequestWarning)

# Fetch the page content
url = "http://blog.naver.com/osr_77/223608227369"
response = requests.get(url, verify=False)

# Parse the HTML
soup = BeautifulSoup(response.text, 'html.parser')

# if soup:
#     print(soup)
# else:
#     print("Tag not found")

# Find the specific span tag by style and class
span_tag = soup.find("div", {"id": "whole-body"})

# Extract text from the span tag
if span_tag:
    print(span_tag)
else:
    print("Tag not found")
