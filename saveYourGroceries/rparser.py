import json 
import time
from requests import get, post

from saveYourGroceries.config import azure_key

# Endpoint URL
endpoint = r"https://myreceiptrecognizer9027.cognitiveservices.azure.com/"
post_url = endpoint + "/formrecognizer/v2.0/prebuilt/receipt/analyze"


# Images less than 4 MB in size, .jpg 
headers = {
    # Request headers
    'Content-Type': 'image/jpeg',
    'Ocp-Apim-Subscription-Key': azure_key,
}

params = {
    "includeTextDetails": True
}

def analyze_receipt(source):
    data_bytes = source.read()

    try:
        resp = post(url = post_url, data = data_bytes, headers = headers, params = params)
        if resp.status_code != 202:
            print("POST analyze failed:\n%s" % resp.text)
            quit()
        print("POST analyze succeeded:\n%s" % resp.headers)
        get_url = resp.headers["operation-location"]
    except Exception as e:
        print("POST analyze failed:\n%s" % str(e))
        quit()


    n_tries = 10
    n_try = 0
    wait_sec = 5
    while n_try < n_tries:
        try:
            print(get_url)
            resp = get(url = get_url, headers = {"Ocp-Apim-Subscription-Key": azure_key})
            resp_json = json.loads(resp.text)
            if resp.status_code != 200:
                print("GET Receipt results failed:\n%s" % resp_json)
            status = resp_json["status"]
            if status == "succeeded":
                print("Receipt Analysis succeeded:\n") #%s" % resp_json)
                # receipt_name = resp_json['analyzeResult']['readResults'][0]['lines'][0]['text']
                # print(f"Dumping json response into {receipt_name}.json")
                # with open(f"{receipt_name}.json", 'w') as f:
                    # json.dump(resp_json, f)
                return resp_json
            if status == "failed":
                print("Analysis failed:\n%s" % resp_json)
            # Analysis still running. Wait and retry.
            time.sleep(wait_sec)
            n_try += 1     
        except Exception as e:
            msg = "GET analyze results failed:\n%s" % str(e)
            print(msg)

    print("Tried 10 times and did not get result... exiting")