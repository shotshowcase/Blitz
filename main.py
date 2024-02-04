import datetime
import streamlit as st
from ProcessData import PostProcessSheetsData, Process_Data
from analytics import Analytics
from festival import offers
from firebaseAPI import initialize_firebase, fetch_credentials_from_firebase
from menuItems import Menu, topmenu
from shopifyAPI import get_shopify_data
from shiprocketAPI import get_shiprocket_data
from store import get_prevPassword, set_prevPassword

st.set_page_config(layout="wide")
initialize_firebase()
password, space,month_, year_, tax = st.columns([5.3,.15,2.4,2.4,2])
with password:
    st.text_input('Password', type='password', key='password')
topmenu(month_,year_)

# Use the fetched data
if st.session_state.password !='':
    
    refresh, contact, Address, gap, view, gap, Score = st.columns([.7,1,1,0.1,2.5,.2,.8])

    with refresh:
        if st.button("Refresh Data") or st.session_state.password != get_prevPassword() :
            st.cache_data.clear()
            fetch_credentials_from_firebase(st.session_state.password)
            df_shopify = get_shopify_data()
            df_shiprocket,invoice_url = get_shiprocket_data()
            set_prevPassword(st.session_state.password)

    fetch_credentials_from_firebase(st.session_state.password)
    df_shopify = get_shopify_data()
    df_shiprocket,invoice_url = get_shiprocket_data()
    set_prevPassword(st.session_state.password)

    with view:
        view_type = st.selectbox('View Type', ['Staging', 'Sheets', 'Analytics'])

    descripent,result_df,Display_list = Process_Data(df_shopify,df_shiprocket)
    Menu(Display_list, result_df, Score, contact, Address, tax, invoice_url)
    offers()
    def CopyOpenOrders():
        if len(descripent)>0:
            st.subheader('Copy Open Orders')
            st.dataframe(descripent[['Name','Email','Shipment Status',"All Order ID's"]],use_container_width=True)

    if view_type == 'Staging':
        st.markdown('---')
        CopyOpenOrders()
        st.title('Staging View')
        st.title('')
        showFullDatabase, simple, space = st.columns([3,2,8])
        with simple:
            if st.toggle("Simple view",value=True):
                simpleview = True
            else:
                simpleview = False
                
        with showFullDatabase:
            SFDToggle =  st.toggle("Show Full Database")
        if SFDToggle:    
            st.write(result_df)
        st.title('')
        
        def display_Table(i):
            st.subheader(f'{i[1]} : {i[2]}',help=i[3])
            if simpleview:
                st.dataframe(i[0][i[4]],use_container_width=True)
            else:
                st.dataframe(i[0],use_container_width=True)

        for i in Display_list:
            display_Table(i)

    if view_type == 'Sheets':
        st.markdown('---')
        CopyOpenOrders()
        st.title('Sheets View')
        st.title('')
        listed_columns = st.multiselect('Columns',list(filter(lambda x: x not in ['Name', 'Shipment Status','Tags', 'Cancel Reason'], list(result_df.columns))))
        styled_df = PostProcessSheetsData(result_df,Display_list,listed_columns)
        st.dataframe(styled_df,use_container_width=True,height=1800)

    if view_type == 'Analytics':
        st.markdown('---')
        st.title('Analytics')
        st.title('')
        Analytics(result_df, Display_list)
        

