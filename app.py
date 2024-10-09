import streamlit as st
import requests
import time
import os

base_url = os.getenv('BASE_URL')
# Set page configuration
st.set_page_config(
    page_icon='👨‍💻',
    page_title="RESEARCH AGENT",
)

# Hide Streamlit default menu and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.markdown(
    r"""
    <style>
    .stDeployButton {
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True
)

# Initialize session state for images_data
if 'images_data' not in st.session_state:
    st.session_state.images_data = []

# Retrieve query parameters
query_params = st.query_params

# Check if both 'access_key' and 'app_id' are present in the query parameters
if 'access_key' in query_params and 'app_id' in query_params:
    access_key = query_params["access_key"]  # Get the access_key
    app_id = query_params["app_id"]  # Get the app_id
    
    # Store the token in session state
    st.session_state.token = f'Bearer {access_key}'
    st.session_state.app_id = app_id

else:
    st.write("Access denied: Insufficient permissions to view this page")

# Only render the page if the token is present in session state
if 'token' in st.session_state:
    token = st.session_state.token
    app_id = st.session_state.app_id
    def refresh_product(taskId):
        url = f'{base_url}/api/v1/user/products/{app_id}/refresh/{taskId}'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': token    
        }
        
        start_time = time.time()
        with st.spinner("Generating Research"):
            while True:
                response = requests.get(url, headers=headers)
                data = response.json()
                # st.write(data)
                if data['data']['status'] != 'Pending':
                    st.title(data["data"]["result"]["data"][0])

                    if data["data"]["result"]["data"][1] != "":
                        st.title("Introduction")
                        st.write(data["data"]["result"]["data"][1])

                    if data["data"]["result"]["data"][2] != "":
                        st.title("Quantitative Facts")
                        st.write(data["data"]["result"]["data"][2])

                    if data["data"]["result"]["data"][3] != "":
                        st.title("Publications")
                        st.write(data["data"]["result"]["data"][3])

                    if data["data"]["result"]["data"][4] != "":
                        st.title("Books")
                        st.write(data["data"]["result"]["data"][4])

                    if data["data"]["result"]["data"][5] != "":
                        st.title("Youtube Links")
                        st.write(data["data"]["result"]["data"][5])
                    break
                
                elif time.time() - start_time > 160:  # Check if 120 seconds have passed
                    st.error("Timeout reached without success.")
                    return []
                    break
                
                else:
                    time.sleep(2)  # Wait for 2 seconds before retrying

    # Set the title of the app
    st.title('Research Assistant 👨‍💻')

    # Define the subheaders
    subheaders = ['Introduction', 'Quantitative Facts', 'Publications', 'Books', 'YouTube Links']

    # Initialize an empty list to store the selected subheaders
    selected_subheaders = []

    # Create checkboxes for each subheader directly under the title
    for subheader in subheaders:
        if st.checkbox(subheader):
            selected_subheaders.append(subheader)

    # User input field
    userInput = st.text_area(label="User Input")

    # Check if at least one subheader is selected and the user input is not empty
    if len(selected_subheaders) > 0 and userInput.strip() != "":
        # Generate button
        if st.button("Generate"):
            payload = {
                "method": "generate_research",
                "payload": {
                    "userInput": userInput,
                    "selected_subheaders": selected_subheaders
                }
            }
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token    
            }
            response = requests.post(f'{base_url}/api/v1/user/products/{app_id}/use', json=payload, headers=headers)
            
            if response.status_code == 201:
                parsed_response_dict = response.json()
                taskId = parsed_response_dict.get('data', {}).get('taskId', "not found")
                data = refresh_product(taskId)
                
            else:
                st.write(response.json())
                st.error(f"Failed to generate. Status code: {response.status_code}")
    else:
        st.info("Please select at least one subheader and provide some input.")

    # If the spinner is active, display it
    if st.session_state.get('spinner'):
        st.spinner('Generating...')
else:
    st.title("Please open this page via the AI Marketplace")
