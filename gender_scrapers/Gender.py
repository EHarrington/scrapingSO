import requests, json, time
from bs4 import BeautifulSoup
import csv
import re
import sys
import StackUtils

ATTRIBUTES = ['full_name', 'url', 'first_name', 'gender', 'probability', 'count']
BASE_URL = 'http://www.stackoverflow.com'
GENDER_FILE = 'StackoverflowGenderInformation12.csv'
PAUSE_TIME = 0.7
WAIT_TIME = 1000


def make_soup(url):
  try:
    html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'})
    return BeautifulSoup(html.text, "lxml")
  except:
    #send('Denial on ' + url, urls_visited)
    time.sleep(WAIT_TIME)
    html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'})
    return BeautifulSoup(html.text, "lxml")

def record_gender_information(users):
  gender_url = ""
  index = 0
  for user in users.keys():
    if gender_url == "":
      gender_url = "name[0]=" + user
    else:
      index += 1
      gender_url = gender_url + "&name[" + str(index) + "]=" + user

  print gender_url

  request = requests.get("http://api.genderize.io?" + gender_url)

  # NOTE LIMITED TO 8190 bytes
  print sys.getsizeof(gender_url)

  results = json.loads(request.text)

  filtered_user_info = []
  fd = open(GENDER_FILE,'a')
  csv_writer = csv.writer(fd, delimiter=',', quotechar='|')

  for result in results:
    if result["gender"] != None:
      first_name = str(result["name"])
      row = users[first_name] + [str(result["name"]), str(result["gender"]),
                                 str(result["probability"]), str(result["count"])]
      csv_writer.writerow(row)
      print ','.join(row)
      del users[first_name]

  for name, urls in users.items():
    row = users[name] + [name, 'neither', '', '']
    csv_writer.writerow(row)
    print ','.join(row)


if __name__ == '__main__':
  # print out column headers
  print(",".join(ATTRIBUTES))

  page_of_users = BASE_URL + '/users?page=21593&tab=reputation&filter=all'
  while True:
    users = {}
    for page in range(0,10):
      time.sleep(PAUSE_TIME)
      soup = make_soup(page_of_users)
      for div in soup.findAll("div", "user-details"):
        try:
          full_name = str(div.a.get_text())
          first_name = full_name[:1] + re.split(r'[\W,A-Z]', full_name[1:])[0]
          url = str(div.a["href"])
          users[first_name] = [url, full_name]
        except:
          try:
            users[first_name] = [url, full_name]
          except:
            print 'Problem parsing user: ' + first_name + str(sys.exc_info()[0])
            #send('Problem parsing users: ' + str(sys.exc_info()[0]), urls_visited)

      # Move to the next page of users
      page_number = int(soup.find("span", "page-numbers current").get_text())
      print 'PAGE NUMBER: ' + str(page_number)
      page_of_users = BASE_URL + soup.find("a", {"title": "go to page " + str(page_number + 1)})["href"]

    record_gender_information(users)
