# Import the necessary Python libraries and functions
from streamlit_option_menu import option_menu
import streamlit as st


from Home import home
from Upload_CSV import Upload
from Upload_feedback import upload_feedback
# from Google_Cloud_Storage import google_cloud_storage
# from Azure_database import azure_database
# from Databricks_CSV import csv_databricks


# st.set_page_config(layout="wide")
# hide_streamlit_style = """ <style> #MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>"""
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Add a heading to the home page
# st.markdown("""
#     <div style='text-align: center; margin-top:-70px; margin-bottom: 5px;margin-left: -50px;'>
#     <h2 style='font-size: 40px; font-family: Courier New, monospace;
#                     letter-spacing: 2px; text-decoration: none;'>
#     <img src="https://acis.affineanalytics.co.in/assets/images/logo_small.png" alt="logo" width="70" height="60">
#     <span style='background: linear-gradient(45deg, #ed4965, #c05aaf);
#                             -webkit-background-clip: text;
#                             -webkit-text-fill-color: transparent;
#                             text-shadow: none;'>
#                     AFFINE Emailyzer
#     </span>
#     <span style='font-size: 40%;'>
    
#     </span>
#     </h2>
#     </div>
#     """, unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; margin-top:-70px; margin-bottom: 5px;margin-left: -50px;'>
        <h2 style='font-size: 40px; font-family: Courier New, monospace;
                    letter-spacing: 2px; text-decoration: none;'>
            <img src="https://acis.affineanalytics.co.in/assets/images/logo_small.png" alt="logo" width="70" height="60">
            <span style='background: linear-gradient(45deg, #ed4965, #c05aaf);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            text-shadow: none;'>
                    Affine
            </span>
        </h2>
        <h2 style='font-size: 40px; font-family: Courier New, monospace;
                    letter-spacing: 2px; text-decoration: none; text-align: center;'>
            Emailyzer
        </h2>
    </div>
    """, unsafe_allow_html=True)

# Use Streamlit to create a sidebar with multiple flow options
with st.sidebar:
    # Define an option menu with flow choices
    choose = option_menu("", ["Home", "Upload csv file",  'Upload email'],  # "Databricks CSV", "Google Cloud Storage", 'Azure SQL Database',
                         icons=['house', 'filetype-csv', 'bar-chart-steps',
                                'cloud-arrow-down', 'database-down'],
                         menu_icon="app-indicator", default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": "#fafafa"},
        "icon": {"color": "black", "font-size": "25px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#fa2a54"},
    }

    )

# Depending on the selected flow, call the respective function
if choose == "Home":
    home()

elif choose == "Upload csv file":
    Upload()

# elif choose == "Databricks CSV":
#     csv_databricks()

# elif choose == "Google Cloud Storage":
#     google_cloud_storage()

# elif choose == "Azure SQL Database":
#     azure_database()

elif choose == "Upload email":
    upload_feedback()

else:
    st.write('yet not written')
