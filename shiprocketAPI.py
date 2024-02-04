import datetime
import requests
import json
import streamlit as st
from store import get_month, get_shiprocket_credentials, get_year
import pandas as pd

@st.cache_data
def get_shiprocket_data():
    
    year = get_year()
    month = get_month()
    start_date = datetime.datetime(year, month, 1)
    if month == 12:
        end_date = datetime.datetime(year + 1, 1, 1)
    else:
        end_date = datetime.datetime(year, month + 1, 1)
    end_date = end_date - datetime.timedelta(milliseconds=1)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # shiprocket login
    url = "https://apiv2.shiprocket.in/v1/external/auth/login"

    EMAIL = get_shiprocket_credentials()['email']
    PASSWORD = get_shiprocket_credentials()['password']
    payload = json.dumps({
    "email": EMAIL,
    "password": PASSWORD
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # shiprocket orders fetching
    next_url = "https://apiv2.shiprocket.in/v1/external/orders"

    params = {'from': start_date_str, 'to': end_date_str,'per_page': 100}
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {response.json()["token"]}'
    }

    all_order_data = []
    while next_url:
        response = requests.get(next_url, headers=headers, params=params)
        data = response.json()
        all_order_data.extend(data['data'])
        next_url = data.get('meta', {}).get('pagination', {}).get('links', {}).get('next', None)
        
    order_data = [(o['channel_order_id'], o['customer_email'], o['customer_name'], o['customer_phone'], o['status'], o['activities'], o['products'][0]['name'], o['payment_method'],
                o['shipments'][0]['pickup_scheduled_date'], o['picked_up_date'], o['shipments'][0]['shipped_date'], o['etd_date'], o['out_for_delivery_date'],
                o['delivered_date'], o['shipments'][0]['rto_delivered_date'], o['shipments'][0]['rto_initiated_date'], o['rto_edd'], o['channel_order_id'],o['shipments'][0]['awb'],o['id'],
                o['customer_address'],o['customer_address_2'],o['customer_city'],o['customer_state'],o['customer_pincode'],o['customer_country']) for o in all_order_data]

    columns = ['OrderID', 'Email', 'Name','Phone Number','Shipment Status', 'Activities', 'Product', 'Payment Type','Pickup Scheduled Date','Pickedup Date','Shipped Date',
                'Estimated Delivery Date','Out For Delivery Date','Delivered Date','RTO Delivered Date','RTO Initiated Date','RTO Estimated Delivery Date',"All Order ID's",'AWB Number','ID',
                'customer_address','customer_address_2','customer_city','customer_state','customer_pincode','customer_country']

    df_shiprocket = pd.DataFrame(order_data, columns=columns)

    df_shiprocket['Complete Address'] = df_shiprocket.apply(
        lambda row: ', '.join(
            [str(row['customer_address']),
            str(row['customer_address_2']),
            str(row['customer_city']),
            str(row['customer_state']),
            str(row['customer_pincode']),
            str(row['customer_country'])]
        ),
        axis=1
    )

    # Drop the original address columns
    df_shiprocket = df_shiprocket.drop(['customer_address', 'customer_address_2', 'customer_city', 'customer_state', 'customer_pincode', 'customer_country'], axis=1)

    remitted = []
    for i in all_order_data:
        if 'expected_remittance_date' not in i.keys():
            remitted.append(i['channel_order_id'])
    df_shiprocket['Shipment Status'][df_shiprocket["All Order ID's"].isin(remitted)] = ['REMITTED']
    df_shiprocket.loc[(df_shiprocket['Payment Type'] == 'prepaid') & (df_shiprocket['Shipment Status'] == 'DELIVERED'), 'Shipment Status'] = ['DELIVERED-PREPAID'] * len(df_shiprocket.loc[(df_shiprocket['Payment Type'] == 'prepaid') & 
                                                                                                                                                                                        (df_shiprocket['Shipment Status'] == 'DELIVERED')])

    remittance_initiated = []
    df_shiprocket['Remittance Date'] = ''
    for i in all_order_data:
        if 'expected_remittance_date' in i.keys():
            if i['expected_remittance_date']['start_date']:
                remittance_initiated.append(i['channel_order_id'])
                df_shiprocket['Remittance Date'][df_shiprocket["All Order ID's"] == i['channel_order_id']] = i['expected_remittance_date']['end_date']
    df_shiprocket['Shipment Status'][df_shiprocket["All Order ID's"].isin(remittance_initiated)] = ['REMITTANCE INITIATED']

    def custom_agg_activities(series):
        list = []
        for i in series.values:
            list = list+ i + ['  ']*19
        return list
    def joinByList(series):
        list = []
        for i in series.values:
            list.append(i)
        return list

    df_shiprocket = df_shiprocket.groupby(['Email', 'Product'], as_index=False).agg({'OrderID':'last', 'Email':'first', 'Name':'first','Phone Number':'first', 'Payment Type':'first','Shipment Status':joinByList, 'Activities':custom_agg_activities, 'Product':'first',
                                                                                    'Pickup Scheduled Date':joinByList,'Pickedup Date':joinByList,'Shipped Date':joinByList,'Estimated Delivery Date':joinByList,'Out For Delivery Date':joinByList,'Delivered Date':joinByList,
                                                                                    'RTO Delivered Date':joinByList,'RTO Initiated Date':joinByList,'RTO Estimated Delivery Date':joinByList, "All Order ID's":joinByList,'AWB Number':joinByList,'Remittance Date':joinByList,
                                                                                    'ID':joinByList, 'Complete Address':'first'})
    remitted_ids = []

    # Iterate over each row
    for index, row in df_shiprocket.iterrows():
        for status_index, status in enumerate(row['Shipment Status']):
            if status == 'REMITTED' or status == 'DELIVERED-PREPAID':
                # Get the corresponding ID
                remitted_id = row['ID'][status_index]
                remitted_ids.append(remitted_id)

    remitted_ids = [int(id) for id in remitted_ids]
    url = "https://apiv2.shiprocket.in/v1/external/orders/print/invoice"
    if remitted_ids:
        payload = json.dumps({
        "ids": remitted_ids
        })
        response = requests.request("POST", url, headers=headers, data=payload)
        invoice_url = json.loads(response.text)['invoice_url']
    else:
        invoice_url = ''

    return df_shiprocket,invoice_url
