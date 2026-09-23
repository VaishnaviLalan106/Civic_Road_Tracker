import streamlit as st
import pandas as pd
import os 
from datetime import datetime
from geopy.geocoders import Nominatim  

geolocator = Nominatim(user_agent="road_repair_tracker")
st.title("Community Road Repair Tracker")
st.write("Report broken roads and track how long they have been ignored by authorities.")

location = st.text_input("Where is the broken road?", 
    placeholder="e.g., Gokulam 3rd stage, or MG Road"
    )
years_broken = st.number_input("How many years has it been like this?", min_value=0, max_value=20, step=1)
description = st.text_area("Describe the condition (e.g., deep potholes, waterlogging)") 
submit_button = st.button("Submit Report")

CSV_FILE = "complaints.csv"

if submit_button:
    if location:
        with st.spinner("Looking up map coordinates..."):
            try:
                # Background trick: search the location text to find coordinates
                search_location = f"{location},Mysore, Karnataka, India"
                geo_data = geolocator.geocode(search_location, timeout=10)
                
                if geo_data:
                    latitude = geo_data.latitude
                    longitude = geo_data.longitude
                    report_id=f"CRR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    new_entry={
                        report_id: [report_id],
                        "location": [location],
                        "years_broken": [years_broken],
                        "description": [description],
                        "latitude": [latitude],
                        "longitude": [longitude],
                        "date_reported": [datetime.now().strftime('%Y-%m-%d')],
                        "status": ["Pending"]
                        }
                    new_df = pd.DataFrame(new_entry)
                    if not os.path.exists(CSV_FILE):
                        new_df.to_csv(CSV_FILE, index=False)
                    else:
                        new_df.to_csv(CSV_FILE, mode='a', header=False, index=False)
                    st.success("Report logged successfully!")
                    st.rerun()
                else:
                    st.error("We couldn't pinpoint that location on the map. Please add a city name or more details ")
            except Exception as e:
                st.error("Map service is currently busy. Please try submitting again.")
    else:
        st.error("Please enter a location before submitting.")
if os.path.isfile(CSV_FILE):
    st.subheader("Unresolved Reports Dashboard")
    all_reports = pd.read_csv(CSV_FILE)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("**Live Hazard Map**")
        st.map(all_reports)
    with col2:
        st.write("**Report Log Table**")
        st.dataframe(all_reports, use_container_width=True)  
    st.dataframe(all_reports)