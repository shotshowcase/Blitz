import streamlit as st

def set_shopify_credentials(api_key, password_shopify, shop_name):
    if 'shopifyCRED' not in st.session_state:
        st.session_state.shopifyCRED = {"shop_name": shop_name,
                                        "api_key": api_key,
                                        "password_shopify": password_shopify}
    else:
        st.session_state.shopifyCRED = {"shop_name": shop_name,
                                        "api_key": api_key,
                                        "password_shopify": password_shopify}
        
def set_shiprocket_credentials(email,password):
    if 'shiprocketCRED' not in st.session_state:
        st.session_state.shiprocketCRED = {"email":email,
                                            "password": password}
    else:
        st.session_state.shiprocketCRED = {"email":email,
                                            "password": password}
     
def set_prevPassword(prevpass):
    if 'previousPassword' not in st.session_state:
        st.session_state.previousPassword = prevpass
    else:
        st.session_state.previousPassword = prevpass    

def set_month(month):
    if 'month' not in st.session_state:
        st.session_state.month = month
    else:
        st.session_state.month = month
             
def set_year(year):
    if 'year' not in st.session_state:
        st.session_state.year = year
    else:
        st.session_state.year = year
        
def get_shopify_credentials():
    return st.session_state.get('shopifyCRED', None)

def get_shiprocket_credentials():
    return st.session_state.get('shiprocketCRED', None)

def get_prevPassword():
    if 'previousPassword' not in st.session_state:
        return ''
    else:
        return st.session_state.get('previousPassword', None) 

def get_month():
    return st.session_state.get('month', None)
             
def get_year():
    return st.session_state.get('year', None)
