import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import smtplib
import ssl

sender_email = "jmc.python.test@gmail.com"
receiver_email = "jmartic@gmail.com"

# Password to enter connect into the gmail account to send email
port = 465  # For SSL
password = input("Type your password and press enter: ")

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
weather_df.to_csv('weather.csv')

weather_text = weather_df.to_string(col_space=10, justify='center')

email_text = '''\
Subject: El Temps


''' + weather_text
print(email_text)

# Create a secure SSL context
context = ssl.create_default_context()
# prepare to send the email
with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, email_text)
