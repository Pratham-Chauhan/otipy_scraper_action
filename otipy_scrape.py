import pdb
import os.path
import requests
import json

import pandas as pd
from datetime import datetime
from time import sleep, time

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

saved_location = './Flash_deal_product_list.csv'
if os.path.exists(saved_location):
    FD = pd.read_csv(saved_location)
else:
    column = ['ID', 'Start_time', 'End_time', 'Start_time_String',
              'End_time_string', 'Item', 'Price', 'Normal Price', 'Diff.', 'Quantity', 'Quantity (in kg)','Price per kg','Normal Price per kg']
    FD = pd.DataFrame(columns=column)

current_deal_items = []
count = 0

def extract_info(i):
    global count, current_deal_items
    price = i['price']  # Limited Price
    
    # keep these, it's easier that way to read datetime
    start_time, end_time = i['start_time'], i['end_time']
    start_time_string = datetime.fromtimestamp(start_time)
    end_time_string = datetime.fromtimestamp(end_time)

    prod = i['normal_product']
    id = prod['id'] # ID is of no use now.
    name, quantity, quantity_in_kg, normal_price = prod['name'], prod['pack_qt'], prod['in_kg'], prod['price']


    price_per_kg = price/quantity_in_kg
    normal_price_per_kg = normal_price/quantity_in_kg
    # print((name, price))
    # save all the items in current deal no matter price got changed or not
    current_deal_items.append(name)
    if not FD.empty:
        for row in FD.to_numpy():
            # Note: ID is no longer identify an Item, that means, one item can change its ID over time :(
            if (start_time == row[1]) & (name == row[5]): # that is, (Start_time-Name) is primary key and unique
                # print('item already stored.', (id, name))
                return


    d = [id, start_time, end_time, start_time_string, end_time_string,
         name, price, normal_price, (normal_price-price), quantity, quantity_in_kg, price_per_kg, normal_price_per_kg]
    # print("{:35s} | {:10s} | ₹{:5d} | ₹{:5d}".format(*d))
    FD.loc[len(FD)] = d
    count += 1

def scrape():
    global count
    headers = {
        'authority': 'gcptest.crofarm.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,hi;q=0.8',
        'access-token': 'e31306fb27e6172c8be9672ea7e95ee5a7eccb7a9b788d282d65a56ed91c3878',
        'client': 'web',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://www.otipy.com',
        'referer': 'https://www.otipy.com/',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }

    params = {
        'page': '1',
        'feed_type': 'web',
        'latitude': '28.45170162',
        'longitude': '77.01849746',
    }

    x = requests.get('https://gcptest.crofarm.com/otipy/web/feed/v1/',
                     params=params, headers=headers)
    if x.status_code != 200:
        print('Request Error:', x.status_code)
        return

    jdata = x.json()['data']['widget_list']
    flash_deal = jdata[1]['data']['items']

    print('Flash Deal Items:', len(flash_deal))
    for item in flash_deal:
        extract_info(item)
    if count == 0:
        print('No Update bro.\n')
    else:
        print(f'{count} items added & price changed.\n')

if __name__ == '__main__':
    #for t in range(1):
    while True: # infinite loop forever

        # reset count and current-deal-items
        count, current_deal_items = 0, []

        scrape()
        # print(FD)
        FD.to_csv(saved_location, index=False)

        # saving item's name in current flash deal
        with open('items_list_current_deal.txt', 'w',encoding='utf-8') as ff:
            ff.write('\n'.join(current_deal_items))

        next_deal_time = FD['End_time_string'].iloc[-1]
        print('Come back at around %s'%next_deal_time)


        endt = int(FD['End_time'].iloc[-1])
        current_time = int(datetime.now().timestamp())

        wait_time_second = endt - current_time
        print('Auto Refresh On: Waiting... %s sec'%wait_time_second)

        sleep(wait_time_second + 60)







# some insight from the data
# df = FD
# # Calculate discount percentage
# df['Discount'] = (df['Diff.']/df['Normal Price'])*100
# df['Discount'] = df.Discount.round(1)

# print(current_deal_items)


