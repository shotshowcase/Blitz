from datetime import datetime, timedelta
import streamlit as st

def offers():

    festivals = {
        'New Year': datetime(2024, 1, 1),
        'Lohri': datetime(2024, 1, 14),
        'Subhas Chandra Bose Jayanti': datetime(2024, 1, 23),
        'Republic Day': datetime(2024, 1, 26),
        'Valentine\'s Day': datetime(2024, 2, 14),
        'Chhatrapati Shivaji Maharaj Jayanti': datetime(2024, 2, 19),
        'Maha Shivaratri': datetime(2024, 3, 8),
        'Holi': datetime(2024, 3, 25),
        'Chhatrapati Shivaji Maharaj Jayanti': datetime(2024, 3, 28),
        'Good Friday': datetime(2024, 3, 29),
        'Easter': datetime(2024, 3, 31),
        'Rama Navami': datetime(2024, 4, 17),
        'Hanuman Jayanti': datetime(2024, 4, 23),
        'Mother\'s Day': datetime(2024, 5, 12),
        'Independence Day': datetime(2024, 8, 15),
        'Raksha Bandhan': datetime(2024, 8, 19),
        'Krishna Janmashtami': datetime(2024, 8, 26),
        'Ganesh Chaturthi': datetime(2024, 9, 7),
        'Gandhi Jayanti': datetime(2024, 10, 2),
        'Dussehra': datetime(2024, 10, 12),
        'Halloween': datetime(2024, 10, 31),
        'Diwali': datetime(2024, 11, 1),
        'Christmas': datetime(2024, 12, 25),
    }

    festivalsDelays = {
        'New Year': 60,
        'Lohri': 10,
        'Subhas Chandra Bose Jayanti': 40,
        'Republic Day': 15,
        'Valentine\'s Day': 10,
        'Chhatrapati Shivaji Maharaj Jayanti': 40,
        'Maha Shivaratri': 40,
        'Holi': 40,
        'Chhatrapati Shivaji Maharaj Jayanti': 40,
        'Good Friday': 15,
        'Easter': 15,
        'Rama Navami': 20,
        'Hanuman Jayanti': 40,
        'Mother\'s Day': 20,
        'Independence Day': 15,
        'Raksha Bandhan': 30,
        'Krishna Janmashtami': 40,
        'Ganesh Chaturthi': 40,
        'Gandhi Jayanti': 25,
        'Dussehra': 20,
        'Halloween': 20,
        'Diwali': 60,
        'Christmas': 60,
    }

    today = datetime.now()
    for name, date in festivals.items():
        if 0 <= (date - today).days <= festivalsDelays[name]:
            with st.chat_message("User"):
                st.write(f"**{name}** is coming up on **{date.strftime('%d %b')}** - **{(date - today).days}** days left.")