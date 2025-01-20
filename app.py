import os
import streamlit as st
import requests
import pandas as pd

# Set the page configuration with a custom favicon
st.set_page_config(
    page_title="Shortify API Front End",
    page_icon="favicon.ico",  # Path to your favicon
    layout="wide"
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #4A90E2;
        color: white;
    }
    .stButton>button {
        background-color: #50E3C2;
        color: white;
        border: None;
        padding: 5px 10px;
        white-space: nowrap;
    }
    .stButton>button:hover {
        background-color: #F5A623;
        color: white;
    }
    h1 {
        color: #4A90E2;
    }
    .stTextInput>div>input {
        background-color: #F5A623;
        color: white;
    }
    .stTextInput>div>input:focus {
        background-color: #50E3C2;
    }
    /* div[data-testid="stAppViewContainer"] > div:nth-child(1) {
        display: none;
    } */
    .stFullScreenFrame {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 20px;
    }
    .delete-button {
        white-space: nowrap;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------------------------------
# BE SURE TO SET this Environment Variable --> SHORTIFY_API_URL  |
#   ON WINDOWS                                                   |
#	    $env:SHORTIFY_API_URL="https://your_url.com"             |
#   ON LINUX                                                     |
#	    export SHORTIFY_API_URL="https://your_url.com"           |
#   ON CLOUD                                                     |
#	    Follow the cloud provider's instructions                 |
# ----------------------------------------------------------------
BASE_URL = os.environ.get('SHORTIFY_API_URL')

# Function definitions
def create_short_link(project_name, destination_url):
    response = requests.post(f"{BASE_URL}/create", json={
        "project_name": project_name,
        "destination_url": destination_url
    })
    return response.json()

def redirect_to_destination(unique_id):
    response = requests.get(f"{BASE_URL}/{unique_id}")
    return response.status_code, response.url

def get_redirect_logs(unique_id):
    response = requests.get(f"{BASE_URL}/logs/{unique_id}")
    return response.json()

def get_all_redirect_logs():
    response = requests.get(f"{BASE_URL}/logs/0")
    return response.json()

def get_all_short_links():
    response = requests.get(f"{BASE_URL}/all_links")
    return response.json()

def update_short_link(unique_id, project_name, destination_url):
    response = requests.put(f"{BASE_URL}/update/{unique_id}", json={
        "project_name": project_name,
        "destination_url": destination_url
    })
    return response.json()

def delete_short_link(unique_id):
    response = requests.delete(f"{BASE_URL}/delete/{unique_id}")
    return response.status_code

def flatten_json(y):
    """Flatten a nested JSON object."""
    out = {}

    def flatten(x, name=''):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + '_')
        elif isinstance(x, list):
            for i, a in enumerate(x):
                flatten(a, name + str(i) + '_')
        else:
            out[name[:-1]] = x  # Remove trailing underscore

    flatten(y)
    return out

def format_json_as_table(data, key):
    """Convert JSON data to a flattened Pandas DataFrame for display."""
    if key in data:
        flattened_data = [flatten_json(item) for item in data[key]]
        return pd.DataFrame(flattened_data)
    return pd.DataFrame()

# Sidebar for navigation
st.sidebar.image("https://raw.githubusercontent.com/dtsoden/shortifyapi/main/MarketingLogo.png", width=200)
st.sidebar.title("Menu")
menu_selection = st.sidebar.radio("Select an Option", [
    "Create Short Link",
    "Redirect to Destination",
    "Get Redirect Logs",
    "Get All Redirect Logs",
    "Get All Short Links",
    "Update Short Link",
    "Delete Short Link"
])

# Create Short Link
if menu_selection == "Create Short Link":
    st.header("Create Short Link")
    project_name = st.text_input("Project Name")
    destination_url = st.text_input("Destination URL")
    if st.button("Create Short Link"):
        result = create_short_link(project_name, destination_url)

        # Check if the result contains the expected data
        if 'short_url' in result and 'unique_id' in result:
            unique_id = result['unique_id']
            short_url = result['short_url']
            st.success(f"Your unique ID: {unique_id}")
            st.success(f"Your short URL: {short_url}")

            # URL of the image
            image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={short_url}"
            # Display the image
            st.image(image_url, caption='Right Click --> Save image as...', width=250)

        else:
            st.error("No links returned in the response. Please check the API response.")

# Redirect to Destination
elif menu_selection == "Redirect to Destination":
    st.header("Redirect to Destination")
    unique_id_redirect = st.text_input("Unique ID for Redirect")
    if st.button("Redirect"):
        status_code, url = redirect_to_destination(unique_id_redirect)
        st.write(f"Status Code: {status_code}, Redirected URL: {url}")

# Get Redirect Logs
elif menu_selection == "Get Redirect Logs":
    st.header("Get Redirect Logs")
    unique_id_logs = st.text_input("Unique ID for Logs")
    if st.button("Get Redirect Logs"):
        logs = get_redirect_logs(unique_id_logs)
        st.dataframe(format_json_as_table(logs, 'logs'))

# Get All Redirect Logs
elif menu_selection == "Get All Redirect Logs":
    if st.button("Get All Redirect Logs"):
        all_logs = get_all_redirect_logs()
        st.dataframe(format_json_as_table(all_logs, 'logs'))

# Get All Short Links
elif menu_selection == "Get All Short Links":
    st.header("All Short Links")

    all_links = get_all_short_links()
    if "links" in all_links and isinstance(all_links["links"], list):
        df_links = pd.DataFrame(all_links["links"])

        if not df_links.empty:
            df_links = df_links[["project_name", "destination_url", "redirect_count", "unique_id"]]
            df_links.columns = ["Project Name", "Destination URL", "Redirect Count", "Unique ID"]

            # Render the table with a delete button in each row
            st.markdown('<div class="stFullScreenFrame">', unsafe_allow_html=True)
            for index, row in df_links.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3, 4, 2, 2, 1])
                col1.write(row["Project Name"])
                col2.write(row["Destination URL"])
                col3.write(row["Redirect Count"])
                col4.write(row["Unique ID"])
                unique_key = f"delete_{row['Unique ID']}"
                if col5.button("Delete", key=unique_key):  # Move this inside the loop
                    status_code = delete_short_link(row["Unique ID"])
                    if status_code == 200:
                        st.success(f"Deleted row with Unique ID: {row['Unique ID']}")
                        # Clear and reload session state
                        if "links_data" in st.session_state:
                            del st.session_state["links_data"]
                        st.rerun()  # Force the page to reload
                    else:
                        st.error(f"Failed to delete row with Unique ID: {row['Unique ID']}")

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No short links found.")
    else:
        st.error("Failed to fetch short links.")

# Update Short Link
elif menu_selection == "Update Short Link":
    st.header("Update Short Link")
    unique_id_update = st.text_input("Unique ID for Update")
    new_project_name = st.text_input("New Project Name")
    new_destination_url = st.text_input("New Destination URL")
    if st.button("Update Short Link"):
        result = update_short_link(unique_id_update, new_project_name, new_destination_url)
        st.dataframe(format_json_as_table(result, 'links'))

# Delete Short Link
elif menu_selection == "Delete Short Link":
    st.header("Delete Short Link")
    unique_id_delete = st.text_input("Unique ID for Deletion")
    if st.button("Delete Short Link"):
        status_code = delete_short_link(unique_id_delete)
        st.write("Delete Status Code:", status_code)
