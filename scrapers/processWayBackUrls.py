import re
import csv
import requests
import sys

def read_from_source_and_write_to_dest(file_name):
  source = open(file_name, 'r')
  dest = open('WayBackMachineUrlsAndTimes.csv', 'w')

  csv_writer = csv.writer(dest, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
  line_num = 0
  for raw_line in source:
    print raw_line
    line = re.sub(r',',"", raw_line)
    url = re.search(r'\<(?P<url>\S+)\>', line).group('url')
    line_num = line_num + 1
    if (line_num > 3 and url.find("ga.") == -1 and url.find("/js/") == -1 and url.find("?tab=") == -1 and url.find("aboutpage.click") == -1):
      print line
      timestamp = re.search(r'/web/(?P<time>\d+)/', url).group('time')
      datetime = re.search(r'datetime="(?P<datetime>[\w\d :]+)"', line).group('datetime')
      print ','.join([url, timestamp, datetime])
      csv_writer.writerow([url, timestamp, datetime])

if __name__ == '__main__':
  given_range = sys.argv
  for i in range(int(given_range[1]), int(given_range[2])):
    print str(i)
    read_from_source_and_write_to_dest("Stack" + str(i) + '.raw')





