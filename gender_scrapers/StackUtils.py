import re
import smtplib # Support for sending warning emals

denied_access = 0
power = 1

def processWayBackUrls(wayback_file):
  users = []
  url_file = open(wayback_file, 'rU')

  for line in url_file:
    if line in ['\n', '\r\n']:
      url_file.close()
      return users
    else:
      url, dow, user_num = line.split(',')
      time_stamp = re.search(r'(?P<time>\d+)/http', url).group('time')
      users.append([url, str(time_stamp), str(dow)])
  
  url_file.close()

  return users

def send(body, urls_visited):
  global denied_access, power
  denied_access = denied_access + 1

  if denied_access % power == 0:
    try:
      power = power * 10
      FROM = 'eh3@williams.edu'
      TO = ['eh3@williams.edu']
      SUBJECT = body
      TEXT = 'Denied Access: ' + str(denied_access) + ' times. Urls-visited: ' + str(urls_visited)

      # Prepare actual message
      message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
                """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

      server = smtplib.SMTP('smtp.gmail.com',587) #port 465 or 587
      server.ehlo()
      server.starttls()
      server.login('eh3@williams.edu','Monkey8166!4!!')
      server.sendmail('eh3@williams.edu','eh3@williams.edu', message)
      server.close()
    except:
      print 'Error sending email'
