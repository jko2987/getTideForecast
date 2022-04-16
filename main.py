import requests as req
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

locations = ['Half Moon Bay, California', 'Huntington Beach, California', 'Providence, Rhode Island', 'Wrightsville Beach, North Carolina']
data = []

for location in locations:

    loc = location.replace(' ', '-').replace(',', '')
    url = f'https://www.tide-forecast.com/locations/Half-Moon-Bay-California/tides/latest'.format(loc)

    page = req.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    tide_days = soup.find_all('div', class_='tide-day')

    for tide_day in tide_days:
        day_str = tide_day.find('h4', class_='tide-day__date').text.split(': ')[1].strip()
        day = datetime.strptime(day_str, '%A %d %B %Y')

        sun_moon_cells= tide_day.find_all('td', class_='tide-day__sun-moon-cell')
        sunrise = ''
        sunset = ''
        for cell in sun_moon_cells:
            if 'Sunrise' in cell.text:
                sun_time = cell.text.split(': ')[1]
                sunrise = datetime.strptime(day_str + ' ' + sun_time, '%A %d %B %Y %I:%M%p')
            elif 'Sunset' in cell.text:
                sun_time = cell.text.split(': ')[1]
                sunset = datetime.strptime(day_str + ' ' + sun_time, '%A %d %B %Y %I:%M%p')
            else:
                pass

        tide_table = tide_day.find('table', class_='tide-day-tides')
        for row in tide_table.find_all('tr'):
            tds = row.find_all('td')
            if len(tds) > 0:
                tide_name = tds[0].text
                if tds[1].text.strip().split(':')[0] == '00':
                    tide_time = ''.join(['12', ':', tds[1].text.strip().split(':')[1]])
                elif len(tds[1].text.strip().split(':')[0]) < 2:
                    tide_time = ''.join(['0', tds[1].text.strip().split(':')[0], ':', tds[1].text.strip().split(':')[1]])
                else:
                    tide_time = tds[1].text


                tide_time = datetime.strptime(tide_time + ' ' + str(day.year), '%I:%M %p(%a %d %B) %Y')
                if tide_time > sunrise and tide_time < sunset and tide_name == 'Low Tide':
                    data.append({'Location': location
                                 , 'Date': day.strftime('%m/%d/%Y')
                                    , 'Sunrise': sunrise.strftime('%H:%M')
                                    , 'Sunset': sunset.strftime('%H:%M')
                                    , 'Low Tide': tide_time.strftime('%H:%M')})

results = pd.DataFrame(data)
print(results)
