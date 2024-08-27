import streamlit as st
import pandas as pd
from openai import OpenAI

# Show title and description.
st.title("This is the a beta of the Sales Monitor app")
st.write(
    "Upload a .csv document with data below and view the charts. "
    "We are also including an option to write a question about it – GPT will answer! "
    "To use this feature, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

st.write("Please first put in a password")
password = st.text_input("Password", type="password")
if not password == 'cislokleslo':
    st.info("Please type in your personal password to continue.", icon="🗝️")
else:
    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader("Upload a document (.csv)", type="csv")

    if uploaded_file is not None:
        # Read the CSV file into a pandas DataFrame.
        df = pd.read_csv(uploaded_file)

        # Display the DataFrame in Streamlit.
        st.write("Here's a preview of your data:")
        st.dataframe(df)  # Display the DataFrame in an interactive table.

        # Ensure that the 'ASIN' column exists in the DataFrame.
        if 'ASIN' in df.columns:
            # Extract unique ASINs for the dropdown menu.
            unique_asins = df['ASIN'].unique()

            # Count the occurrences of each ASIN.
            asin_counts = df['ASIN'].value_counts()

            # Identify ASINs with more than one occurrence.
            multiple_occurrences = asin_counts[asin_counts > 1]

            # Display the number of products with multiple occurrences.
            st.write(f"There are {len(multiple_occurrences)} products with multiple occurrences in the dataset.")

            # Extract unique ASINs for the dropdown menu.
            unique_asins = df['ASIN'].unique()

            # Allow the user to select an ASIN from the dropdown.
            selected_asin = st.selectbox("Select an ASIN to filter:", unique_asins)

            # Filter the DataFrame based on the selected ASIN.
            filtered_df = df[df['ASIN'] == selected_asin]

            # Display the filtered DataFrame.
            st.write(f"Occurrences of ASIN {selected_asin}:")
            st.dataframe(filtered_df)
        else:
            st.error("The CSV file does not contain an 'ASIN' column.")


    # Ask user for their OpenAI API key via `st.text_input`.
    # Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
    # via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
    else:

        # Create an OpenAI client.
        client = OpenAI(api_key=openai_api_key)
        # Ask the user for a question via `st.text_area`.
        question = st.text_area(
            "Now ask a question about the document!",
            placeholder="Can you give me a short summary?",
            disabled=not uploaded_file,
        )

        if uploaded_file and question:

            # Process the uploaded file and question.
            document = uploaded_file.read().decode()
            messages = [
                {
                    "role": "user",
                    "content": f"Here's a document: {document} \n\n---\n\n {question}",
                }
            ]

            # Generate an answer using the OpenAI API.
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=True,
            )

            # Stream the response to the app using `st.write_stream`.
            st.write_stream(stream)
