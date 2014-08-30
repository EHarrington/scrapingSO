import requests, json, time
from bs4 import BeautifulSoup
import csv
import re
import sys
import StackUtils

ATTRIBUTES = ['full_name', 'url', 'first_name', 'gender', 'probability', 'count']
GENDER_FILE = '2012StackGender.csv'
USER_FILE = '2012StackUsers.csv'

def make_soup(url):
  try:
    html = requests.get(url, headers=HEADER)
    return BeautifulSoup(html.text, "lxml")
  except:
    print 'SLEEPING 10 seconds'
    time.sleep(10)
    html = requests.get(url, headers=HEADER)
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
  if sys.getsizeof(gender_url) > 8190:
    raise TypeError("GENDER URL TOO BIG")

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
    del users[name]

  fd.close()

if __name__ == '__main__':
  # print out column headers
  print(",".join(ATTRIBUTES))

  users = {}
  index = 0
  with open(USER_FILE) as user_file:
    for line in user_file:
      user_attributes = line.split(',')
      url = user_attributes[0]

      if (len(user_attributes) < 2 or len(user_attributes[1]) == 0):
        try:
          full_name = str(re.sub(r'\W', " ", re.search(r'users/\d+/(?P<name>.+)', url).group('name')).strip())
        except:
          continue
      else:
        full_name = user_attributes[1]

      first_name = full_name[:1] + re.split(r'[\W,A-Z]', full_name[1:])[0]
      users[first_name] = [url, full_name]

      if index % 400 == 0:
        record_gender_information(users)

      index = index + 1

  record_gender_information(users)
