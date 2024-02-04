import datetime
import streamlit as st
import shopify
import pandas as pd
from store import get_month, get_shopify_credentials, get_year

@st.cache_data
def get_shopify_data():
    
    year = get_year()
    month = get_month()
    start_date = datetime.datetime(year, month, 1)
    if month == 12:
        end_date = datetime.datetime(year + 1, 1, 1)
    else:
        end_date = datetime.datetime(year, month + 1, 1)
    end_date = end_date - datetime.timedelta(milliseconds=1)

    API_KEY = get_shopify_credentials()['api_key']
    PASSWORD_SHOPIFY = get_shopify_credentials()['password_shopify']
    SHOP_NAME = get_shopify_credentials()['shop_name']
    shop_url = f"https://%s:%s@{SHOP_NAME}.myshopify.com/admin" % (API_KEY, PASSWORD_SHOPIFY)
    shopify.ShopifyResource.set_site(shop_url)
    
    Allorders = []
    orders = shopify.Order.find(limit=250, status='any', created_at_min=start_date, created_at_max=end_date)
    while orders:
        Allorders += orders
        if orders.has_next_page():
            orders = orders.next_page()
        else:
            break

    order_data = [(o.order_number, o.total_price, o.financial_status, o.fulfillment_status, o.cancel_reason, o.created_at, o.tags) for o in Allorders]
    columns = ['OrderID', 'Price','Financial Status','Fulfillment Status', 'Cancel Reason', 'Created On', 'Tags']

    df_shopify = pd.DataFrame(order_data, columns=columns)
    return df_shopify