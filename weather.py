import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from time import time

# Initialize email variables
SENDER_EMAIL = "jmc.python.test@gmail.com"
RECEIVER_EMAIL = "jmartic@gmail.com"
# Password to enter connect into the gmail account to send email
port = 465  # For SSL
password = input('Type your password and press enter: ')

while True:
    message = MIMEMultipart('alternative')
    message["Subject"] = 'El Temps'
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL

    # meteocat.cat url
    URL = 'https://www.meteo.cat/prediccio/municipal/080961'

    # Retrieve the page and parse the html content
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Store the weather info we want of today and tomorrow
    days = []
    today = soup.find(id="tabs-dia1")
    tomorrow = soup.find(id="tabs-dia2")
    days.append(today)
    days.append(tomorrow)

    # Extract the data
    titles = []
    data = []
    for day in days:
        th = day.find_all('th')
        for t_header in th:
            if t_header.text.strip() != '':
                titles.append(t_header.text.strip())

        td = day.find_all('td')
        for t_data in td:
            if t_data.text.strip() != '':
                data.append(t_data.text.strip())

    while 'Cel' in titles:
        titles.remove('Cel')

    rows = [titles[1][:4] + ' (C)  ', titles[2] + ' (k/h)']
    cols = [x for x in data if ' h' in x]
    temp = [x.split()[0] for x in data if '°C' in x]
    wind = [x.split()[0] for x in data if 'km/h' in x]

    weather_data = [temp, wind]
    weather_data = np.array(weather_data)

    weather_df = DataFrame(weather_data, index=rows, columns=cols)

    weather_html = weather_df.to_html(justify='center', col_space=35)
    weather_html = weather_html.replace('<tr>', '<tr align="center">')

    # Create the plain-text and HTML version of your message
    email_text = f' ' * 10
    for col in cols:
        email_text += f'{col:>5}'
    email_text += f'\n{rows[0]:>9}'

    for temp in weather_df.loc['Temp (C)  ', :]:
        email_text += f'{temp:>5}'
    email_text += f'\n{rows[1]:>9}'

    for wind in weather_df.loc['Vent (k/h)', :]:
        email_text += f'{wind:>5}'
    email_text += f'\n'

    email_html = '''\
    <html>
      <body>
    ''' + weather_html + '''\
      </body>
    </html>
    '''

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(email_text, "plain")
    part2 = MIMEText(email_html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create a secure SSL context
    context = ssl.create_default_context()
    # prepare to send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(SENDER_EMAIL, password)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())

    # sleep for 12 hours
    time.sleep(12 * 60 * 60)
