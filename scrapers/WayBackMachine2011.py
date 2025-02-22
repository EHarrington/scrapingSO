from __future__ import with_statement
from bs4 import BeautifulSoup
import threading

import StackUtils
import requests
import re
from multiprocessing import Pool # be not so nice
import time
import sys
import csv

BASE_URL = 'http://web.archive.org/web/'
ATTRIBUTES = ['url', 'name', 'time_stamp', 'dow', 'rep',
              'Age', 'Website', 'Location', 'Member for', 'Last seen',
              'Questions', 'Answers', 'Votes', 'Tags',
              'Up', 'Down', 'Answer', 'Question']
URL_FILE = '2011CurStack.txt'
USER_FILE = '2011StackUsers.csv'
LOCK = threading.Lock()
HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'}
user_file = open(USER_FILE,'a')
user_writer = csv.writer(user_file, delimiter=',', quotechar='|')

def make_soup(url):
  try:
    html = requests.get(url, headers=HEADER)
    return BeautifulSoup(html.text, "lxml")
  except:
    print 'SLEEPING FOR 10 SECONDS'
    time.sleep(10)
    html = requests.get(url, headers=HEADER)
    return BeautifulSoup(html.text, "lxml")

def scrape_personal_info(soup):
  try:
    personal_info = re.sub(r'[<[^<]+?>]|,|[\t\r\f\v]', "", soup.find("table", "user-details").get_text())
  except:
    return ['', '', '', '', '']

  bio = []

  for attr in ['name', 'age', 'website', 'location', 'member for', 'seen']:
    try:
      pattern = re.compile(attr + "\n+(?P<value>[\S ]+)\n")
      potential_value = re.sub(r'  ', '', str(re.search(pattern, personal_info).group('value')))

      if potential_value == 'age' or potential_value == 'location':
        bio.append('')
      else:
        bio.append(potential_value)
    except:
      bio.append('')

  return bio

def scrape_vote_details(soup):
  try:
    vote_info = re.sub(r'[<[^<]+?>]|,', "", soup.find("table", "votes-cast-stats").get_text())
  except:
    return ['', '', '', '']

  vote_details = []

  for vote_type in ['up', 'down', 'answer', 'question']:
    try:
      pattern = re.compile("\s(?P<value>\d+)\s+" + vote_type)
      vote_details.append(re.sub(r'\D','',re.search(pattern, vote_info).group('value')))
    except:
      vote_details.append('')

  return vote_details

def scrape_activity_stats(soup):
  activities = []
  try:
    for stat in soup.find("table", "summary-title").findAll("span", "summarycount ar"):
      activities.append(re.sub(r',', '', stat.get_text()))
  except:
    return ['', '', '', '']

  return activities

def get_user_information(user_info):
  global user_writer, user_file

  url = user_info[0]
  soup = make_soup(BASE_URL + url)
  try:
    user_name = str(soup.find("div", "subheader").find("h1", "").get_text())
    if len(user_name) == 0:
      user_name = str(re.sub(r'\W', " ", re.search(r'users/\d+/(?P<name>.+)', url).group('name')).strip())
  except:
    try:
      user_name = str(re.sub(r'\W', " ", re.search(r'users/\d+/(?P<name>.+)', url).group('name')).strip())
    except:
      return None

  actual_time_stamp = "Unknown"

  for link in soup.findAll("link", ""):
    match = re.match(r'/web/(?P<time>\d+)', link['href'])
    if match == None:
      continue
    else:
      actual_time_stamp = match.group('time')

  try:
    rep = re.sub(r'\D', "", soup.find("div", "reputation").get_text())
  except:
    rep = ''

  user_url = re.sub(r'\d+/http://stackoverflow\.com/', "", url)

  user = [user_url, user_name, actual_time_stamp] + user_info[1:] + [rep]

  user += scrape_personal_info(soup)
  try:
    user += scrape_medals(soup)
  except:
    user += []
  user += scrape_activity_stats(soup)
  user += scrape_vote_details(soup)

  with LOCK:
    user_writer.writerow(user)
    print u','.join(user).encode('utf-8').strip()

if __name__ == '__main__':
  try:
    print(",".join(ATTRIBUTES))
    user_writer.writerow(ATTRIBUTES)

    users = StackUtils.processWayBackUrls(URL_FILE)
    pool = Pool(8)
    pool.map(get_user_information, users)
  finally:
    user_file.close()





