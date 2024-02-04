import pandas as pd
import streamlit as st
from store import get_shopify_credentials, set_month, set_year
import calendar
from datetime import datetime

def Menu(Display_list, result_df, Score, contact, Address, tax, invoice_url):
    if invoice_url != '':
        with tax:
            st.markdown(f'<a href="{invoice_url}" target="_blank">Download Tax Invoice</a>', unsafe_allow_html=True)
    else:
        with tax:
            st.error('No Tax Invoice Available')
             
    Scores = [2,1,2,3,5,8,8,8,13,5,5,3,6]
    with Score:
        finalScore = 10-(sum([Display_list[x][2]*y for x,y in zip(range(len(result_df)), Scores)])*2.5/len(result_df))
        st.metric('RMS',round(finalScore*100), delta=str(round((finalScore/6.5)-1,2))+'%')

    csv_data = result_df[['Email','Phone Number']].rename_axis('Name')
    csv_data.index = '#' + csv_data.index.astype(str)+' - '+ get_shopify_credentials()['shop_name']
    csv_data = csv_data.to_csv(index=True).encode('utf-8')
    contact.download_button(
        label="Dowload Contact List",
        data=csv_data,
        file_name='Contacts.csv',
        mime='text/csv'
    )
    contact.markdown("[Upload here](https://contacts.google.com/)")

    address_confirmation_message = result_df.apply(
        lambda row: f"Hi {row['Name'].split()[0]},\n"
                    "Thank you for your order! If you'd like to make any changes to your delivery address, "
                    "please let us know for a seamless delivery experience.\n\n"
                    f"*Your Current Delivery Address is*: {row['Complete Address']}\n\n"
                    "Looking forward to serving you soon!",
        axis=1
    )

    # Create a new DataFrame with the 'Address confirmation message' column, using the same index as 'df'
    address_csv_data = pd.DataFrame({'Address confirmation message': address_confirmation_message}, index=result_df.index)
    address_csv_data = address_csv_data.sort_index(ascending=False)
    address_csv_data = address_csv_data.to_csv(index=True).encode('utf-8')
    Address.download_button(
        label="Address Confirmation Message",
        data=address_csv_data,
        file_name='AddressConfirmation.csv',
        mime='text/csv'
    )

def topmenu(month_,year_):
    # Current date
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Year selector
    with year_:
        year = st.selectbox("Year", range(2020, current_year + 1), index=current_year - 2020)

    # Month selector
    month_names = list(calendar.month_name)[1:]  # Skipping the first entry as it is empty
    
    # Disable future months for the current year
    if year == current_year:
        month_names = month_names[:current_month]
        with month_:
            month = st.selectbox("Month", month_names, index=current_month - 1)
        selected_month = month_names.index(month) + 1
    
    else:
        with month_:
            month = st.selectbox("Month", month_names, index=current_month - 1)
        selected_month = month_names.index(month) + 1
        
    set_month(selected_month)
    set_year(year)