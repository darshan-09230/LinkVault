import requests
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("google_safe_browsing")

def check(url):
  endpoint = (
      "https://safebrowsing.googleapis.com/v4/"
      f"threatMatches:find?key={API_KEY}"
  )

  payload = {
      "client": {
          "clientId": "discord-link-bot",
          "clientVersion": "1.0"
      },
      "threatInfo": {
          "threatTypes": [
              "MALWARE",
              "SOCIAL_ENGINEERING",
              "UNWANTED_SOFTWARE"
          ],
          "platformTypes": [
              "ANY_PLATFORM"
          ],
          "threatEntryTypes": [
              "URL"
          ],
          "threatEntries": [
              {
                  "url": url
              }
          ]
      }
  }

  response = requests.post(endpoint, json=payload)

  # return("Status:", response.status_code)
  # return("Response:", response.text)

  if response.status_code == 200:
      data = response.json()

      if "matches" in data:
          return("Unsafe URL")
      else:
          return("Safe URL")
  else:
      return("Request failed")