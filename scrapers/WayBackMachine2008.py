from __future__ import with_statement
from bs4 import BeautifulSoup

import threading
from bs4 import BeautifulSoup
import requests
import re
from multiprocessing import Pool # be not so nice
import time
import sys
import csv
import StackUtils

BASE_URL = 'http://web.archive.org/web/'
ATTRIBUTES = [
                'url', 'name', 'actual_time_stamp', 'requested_time_stamp','dow',
                'rep', 'questions', 'answers',
                'votes', 'tags', 'badges',
                'Age', 'Website', 'Location', 'Member for', 'Last seen',
                'up', 'down'
             ]
URL_FILE = '2008CurStack.txt'
USER_FILE = '2008StackUsers.csv'
LOCK = threading.Lock()
HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'}
user_writer = None

def make_soup(url):
  try:
    html = requests.get(url, headers=HEADER)
    return BeautifulSoup(html.text, "lxml")
  except:
    print 'SLEEPING 10 seconds'
    time.sleep(10)
    html = requests.get(url, headers=HEADER)
    return BeautifulSoup(html.text, "lxml")

def scrape_personal_info(soup):
  try:
    raw_personal_info = soup.find("table", "user-details").get_text()
  except:
    return ['NF', 'NF', 'NF', 'NF', 'NF']

  personal_info = re.sub(r'[<[^<]+?>]|,|[\t\r\f\v]', "", raw_personal_info)
  bio = []
  for attr in ['Age', 'Website', 'Location', 'Member for', 'Last seen']:
    try:
      pattern = re.compile(attr + "\s+(?P<val>[\S ]+)\s")
      potential_value = str(re.search(pattern, personal_info).group('val'))
      if potential_value == 'Age' or potential_value == 'Location':
        bio.append('')
      else:
        bio.append(potential_value)
    except:
      bio.append('')

  return bio

def scrape_activity_stats(soup):
  try:
    summary_info = [str(re.sub(r'\D', "", summary.get_text())) for summary in soup.findAll("div", "summarycount")]
    while len(summary_info) < 6:
      summary_info.append('NF')
    return summary_info
  except:
    return ['NF', 'NF', 'NF', 'NF', 'NF', 'NF']

def scrape_vote_details(soup):
  try:
    votes = [str(vote.find("span", "vote-count-post").get_text()) for vote in soup.findAll("div", "vote")]
    if len(votes) < 2:
      votes.append('?')
    return votes
  except:
    return ['NF', 'NF']

def get_user_information(user_info):
  global user_writer

  url = user_info[0]
  user_url = re.sub(r'\d+/http://stackoverflow\.com/', "", url)
  soup = make_soup(BASE_URL + url)

  actual_time_stamp = "Unknown"

  for link in soup.findAll("link", ""):
    match = re.match(r'/web/(?P<time>\d+)', link['href'])
    if match == None:
      continue
    else:
      actual_time_stamp = match.group('time')

  try:
    user_name = str(re.sub(r'[\n\t]', "", str(soup.find("div", {"id":"subheader"}).h1.get_text())).strip())
    if len(user_name) == 0:
      user_name = str(re.sub(r'\W', " ", re.search(r'users/\d+/(?P<name>.+)', url).group('name')).strip())
  except:
    try:
      user_name = str(re.sub(r'\W', " ", re.search(r'users/\d+/(?P<name>.+)', url).group('name')).strip())
    except:
      return None

  user = [user_url, user_name, actual_time_stamp] + user_info[1:]

  user += scrape_activity_stats(soup)
  user += scrape_personal_info(soup)
  user += scrape_vote_details(soup)

  with LOCK:
    user_writer.writerow(user)
    print u','.join(user).encode('utf-8').strip()

  return None


if __name__ == '__main__':
  global csv_writer
  # print out column headers
  print(",".join(ATTRIBUTES))

  user_file = open(USER_FILE,'a')

  try:
    user_writer = csv.writer(user_file, delimiter=',', quotechar='|')
    users = StackUtils.processWayBackUrls(URL_FILE)
    pool = Pool(8)
    pool.map(get_user_information, users)
  finally:
    user_file.close()




