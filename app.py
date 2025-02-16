# Startup: 
# cd "C:\Users\danie\OneDrive\Work\Career\Coding\Folio\Horse Racing Form\horse-form-gh-rep" 
# env/scripts/activate
# streamlit run app.py

import streamlit as st
from pathlib import Path
import functions

st.set_page_config(page_title="Horse form app", layout="wide")

# Path to the CSS file
css_file_path = Path("styles.css")

# Read the CSS file
with open(css_file_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(f"""
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css?family=Libre+Bodoni|New+Amsterdam|Fredoka|Vollkorn SC" rel="stylesheet">
        <link href="styles.css" rel="stylesheet">
    </head>
            
    <div class="major-heading">
        Horse Racing Form App
    </div>
    <div class="homepage-text">
        This is a front-end for you to download the form, simply copy in a valid URL from Racing Australia (needs to have form data published), begin data transformation and output the csv to your downloads.
    </div>
""", unsafe_allow_html=True)


# Place the text input in the first column
racing_url = st.text_input("Copy in the URL:")

track_condition_options = ['Good', 'Soft', 'Heavy', 'Soft/Heavy']
track_conditions = st.selectbox('Track conditions for the day:', track_condition_options)

# Button to trigger the function once the URL is entered
if st.button("Begin data transformation"):
    if (racing_url and track_conditions):
        # Fetch and parse HTML once
        soup = functions.get_request(racing_url)

        if soup is None:
            st.error("Error fetching the URL.")

        meta_output = functions.raceday_meta(soup)
        meta_rows = len(meta_output)
        field_output = functions.raceday_field(soup)
        field_rows = len(field_output)
        form_output = functions.horse_form(soup)
        form_rows = len(form_output)

        st.write(f"Metadata rows: {meta_rows}, field rows: {field_rows}, form rows: {form_rows}")

        if meta_output.empty:
            st.error("No raceday metadata information")
        elif field_output.empty:
            st.error("No raceday field information")
        elif form_output.empty:
            st.error("No raceday form information")
        else:
            trn_form_output = functions.raw_to_trn_form(soup)
            trn_form_rows = len(trn_form_output)
            trn_field_output = functions.raw_to_trn_field(soup)
            trn_field_rows = len(trn_field_output)
            trn_meta_output = functions.raw_to_trn_meta(soup)
            trn_meta_rows = len(trn_meta_output)

            st.write(f"Trn rows: form: {trn_form_rows} field: {trn_field_rows}, meta: {trn_meta_rows}")

            int_output = functions.join_datasets(soup)
            int_columns = int_output.columns
            
            int_rows = len(int_output)
            if int_rows > 0:
                st.write(f"Successfully joined tables, int rows: {int_rows}")
                st.write(f"Columns from int output: {int_columns}")

            up_ratio = functions.up_ratio(soup)
            st.write(f"Up ratio created")
            output_df = functions.conditional_col_deletes(track_conditions, soup)
            #output_df = functions.drop_col(track_conditions, soup)
            #output_df = functions.conditional_col_deletes(track_conditions, soup)
            
            day, month, year, state, track = functions.create_file_name(racing_url)

            st.write(f"Outputting dataset for: {track} on {day}_{month}_{year}")

            #Convert DataFrame to CSV
            csv_data = output_df.to_csv(index=False)
            
            # Create a download button
            st.download_button(
                label="Download output racing form CSV",
                data=csv_data,
                file_name=f"racing_data_{day}_{month}_{year}_{state}_{track}.csv",
                mime="text/csv"
            )
   
    else:
        st.write("Please enter a valid URL.")