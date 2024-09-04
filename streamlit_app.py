import streamlit as st
import pandas as pd
import plotly.express as px

# Assuming you have a combined DataFrame 'df_combined' available here
# For demonstration, let's assume 'df_combined' is already loaded and structured correctly

# Ask for password to secure the application
st.write("Please first put in a password")
password = st.text_input("Password", type="password")
if password == 'cislokleslo':
    # Let the user upload multiple files via `st.file_uploader`.
    uploaded_files = st.file_uploader("Upload documents (.csv, .xlsx)", type=["csv", "xlsx"], accept_multiple_files=True)

    if uploaded_files is not None and len(uploaded_files) > 0:
        data_frames = []
        for uploaded_file in uploaded_files:
            if uploaded_file.type == "text/csv":
                df_temp = pd.read_csv(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                df_temp = pd.read_excel(uploaded_file)
            # Remove the file extension for display purposes
            df_temp['Filename'] = uploaded_file.name.rsplit('.', 1)[0]
            data_frames.append(df_temp)

        df_combined = pd.concat(data_frames, ignore_index=True)

        if 'Product ID' in df_combined.columns:
            # Count the occurrences of each 'Product ID'.
            product_id_counts = df_combined['Product ID'].value_counts()

            # Identify 'Product IDs' with more than one occurrence.
            multiple_occurrences = product_id_counts[product_id_counts > 1].index.tolist()

            if len(multiple_occurrences) > 0:
                selected_product_id = st.selectbox(
                    "Select a Product ID to filter (only showing Product IDs with multiple occurrences):",
                    multiple_occurrences)

                # Filter DataFrame based on the selected 'Product ID'.
                df_filtered = df_combined[df_combined['Product ID'] == selected_product_id]

                # Plotting using Plotly
                if not df_filtered.empty:
                    fig = px.scatter(df_filtered, x='Filename', y='Cost', color='Filename',
                                     title=f"Cost by Vendor for Product ID {selected_product_id}",
                                     labels={"Filename": "Vendor", "Cost": "Cost"})
                    st.plotly_chart(fig, use_container_width=True)
                    # Display the entire DataFrame section below the figure
                    st.dataframe(df_filtered)
                else:
                    st.write("No data available for the selected Product ID.")
            else:
                st.warning("No Product IDs with multiple occurrences found in the dataset.")
        else:
            st.error("The CSV file does not contain a 'Product ID' column.")

    # Handling OpenAI API key input
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
            disabled=not uploaded_files,
        )

        if uploaded_files and question:
            # Since multiple files might be uploaded, consider how you handle the document variable
            # For simplicity, here is an example of how you might process a single file's content.
            # This needs to be adapted if multiple files' contents need to be included.
            document = next(iter(uploaded_files)).read().decode()
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

else:
    st.info("Please type in your personal password to continue.", icon="🗝️")
