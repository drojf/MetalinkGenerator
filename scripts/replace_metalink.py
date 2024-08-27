import re
from urllib.request import urlopen

from requests import Request

with open('installdata.json', encoding='utf-8') as f:
    lines = f.readlines()

    unique_urls = {}

    for line in lines:
        match = re.search('"(https:[^"]*)"', line)
        if match:
            unique_urls[match.group(1)] = None

    for baseURL, replacement in unique_urls.items():
        testURL = baseURL + '.meta4'
        print(f"Testing {testURL}...", end='')
        try:
            httpResponse = urlopen(testURL)
        except:
            print('FAIL')
            continue

        print('OK')
        unique_urls[baseURL] = testURL

with open('installdata.json', encoding='utf-8') as f:
    all_text = f.read()

    for (originalURL, replacementURL) in unique_urls.items():
        if replacementURL is not None:
            print(f"Replacing {originalURL} -> {replacementURL}")
            all_text = all_text.replace(originalURL, replacementURL)

with open('out.json', 'w', encoding='utf-8') as out:
    out.write(all_text)