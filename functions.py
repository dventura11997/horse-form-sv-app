# def test_fn(racing_url):
#     return f"Received URL: {racing_url}"

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
from datetime import datetime

# URL to scrape
def get_url(racing_url):
    return racing_url

def get_track_conditions(track_conditions):
    return track_conditions

def create_file_name(racing_url):
    try:
        #Create date variables for folder paths
        current_date = datetime.now()
        day = current_date.day
        month = current_date.month
        year = current_date.year

        print(f"Successfully created date variables")

        # Extract state and track name from url for folder paths
        state = re.search(r"Key=\d{4}\w+%2C([A-Z]+)%2C", racing_url).group(1)
        track = re.search(r"Key=\d{4}\w+%2C[A-Z]+%2C(.+)$", racing_url).group(1).replace('%20', ' ')
        print(f"Successfully found {state} and {track} in url")

        return day, month, year, state, track

    except Exception as e:
        print(f"Error getting this getting folder path params")

def get_request(racing_url):
    # Send a GET request
    racing_url = get_url(racing_url)
    response = requests.get(racing_url)
    #soup = BeautifulSoup(response.content, 'html.parser')
    try:
        print(f"Successfully accessed url: {response.status_code}")
    except Exception as e:
        print(f"Error accessing url: {e}")

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"Successfully parsed html")
    except Exception as e:
        print(f"Error parsing html: {e}")
    return soup

def raceday_meta(soup):
    try:
        # Locate the table element
        raceday_meta_tag = soup.find_all('table', class_='race-title')
        raceday_meta_data = []
        #print(f"Successfully found raceday meta element: {raceday_meta_tag[0]}")
    except Exception as e:
        print(f"Error finding raceday meta element: {e}")
    

    for table in raceday_meta_tag:
        # Extract race number
        race_numbers = table.find_all('span', class_='raceNum')
        event_numbers = [race.text for race in race_numbers]
        #print(numbers)
        stripped_numbers = [re.sub(r'Race\s*', '', number) for number in event_numbers]
        #print(stripped_numbers)
        track_elements = table.find_all('b', text='Track Condition:')
        tracks = [track.next_sibling.strip() for track in track_elements if track.next_sibling]
        if len(tracks) > 0:
            track_con = tracks[0]
        else: 
            track_con = 'Unlisted'

        # Extract and clean race event information
        race_event = table.find_all('th')
        event = [event.text for event in race_event]
        cleaned_text = [re.sub(r'Race \d+ - ', '', full_text).strip() for full_text in event]
        cleaned_text = [re.sub(r'Times displayed.*', '', text).strip() for text in cleaned_text]

        # Combine race number and event into dictionaries
        for race_num, event_num, event_text, trck in zip(stripped_numbers, event_numbers, cleaned_text, track_con):
            raceday_meta_data.append({
                'RaceNumber': race_num,
                'EventNumber': event_num,
                'Event': event_text,
                'Track conditions': track_con
            })

    # Convert to DataFrame for structured data
    raceday_meta_df = pd.DataFrame(raceday_meta_data)
    #print(raceday_meta_df)
    return raceday_meta_df
    #raceday_meta_df.to_excel(subfolder / f"raceday_meta_raw_{day}_{month}_{year}_{state}_{track}.xlsx", index=False)

def raceday_field(soup):
    #soup = get_request(racing_url)
    try:
        raceday_field_tag = soup.find_all('table', class_='race-strip-fields')
        raceday_field_data = []
        #print(f"Successfully found raceday field element: {raceday_field_tag[0]}")
    except Exception as e:
        print(f"Error finding raceday field element: {e}")
    # Initialize a race number counter
    race_number = 1

    for table in raceday_field_tag:
        horse_number_cells = table.find_all('td', class_='no')
        horse_numbers = [horse.text for horse in horse_number_cells]
        last_10_cells = table.find_all('td', class_='last')
        last_10 = [horse.text for horse in last_10_cells]
        horse_name_cells = table.find_all('td', class_='horse')
        horse_names = [horse.find('a').text for horse in horse_name_cells if horse.find('a')]
        horse_trainer_cells = table.find_all('td', class_='trainer')
        horse_trainers = [horse.find('a').text for horse in horse_trainer_cells if horse.find('a')]
        horse_jockey_cells = table.find_all('td', class_='jockey')
        horse_jockeys = [horse.find('a').text for horse in horse_jockey_cells if horse.find('a')]
        horse_barrier_cells = table.find_all('td', class_='barrier')
        horse_barriers = [horse.text for horse in horse_barrier_cells]
        horse_weight_cells = table.find_all('td', class_='weight')
        horse_weights = [horse.text for horse in horse_weight_cells]
        horse_hcp_cells = table.find_all('td', class_='hcp')
        horse_hcp = [horse.text for horse in horse_hcp_cells]

        for num, lst, name, train, jock, bar, weigh, hcp in zip(horse_numbers, last_10, horse_names, horse_trainers, horse_jockeys, horse_barriers, horse_weights, horse_hcp):
            raceday_field_data.append({
                'RaceNumber': race_number,
                'HorseNumber': num,
                'LastTen': lst,
                'HorseName': name,
                'HorseTrainer': train,
                'HorseJockey': jock,
                'HorseBarrier': bar,
                'HorseWeight': weigh,
                'HorseHcp': hcp
            })
        
        # Increment race number after processing each table
        race_number += 1

    raceday_field_df = pd.DataFrame(raceday_field_data)
    return raceday_field_df
    #raceday_field_df.to_excel(subfolder / f"raceday_field_raw_{day}_{month}_{year}_{state}_{track}.xlsx", index=False)

def horse_form(soup):
    try:
        horse_form_tag = soup.find_all('table', class_='horse-form-table')
        horse_form_data = []
        missing_data_horses = []
        #print(f"Successfully found horse form element: {horse_form_tag[0]}")
    except Exception as e:
        print(f"Error finding horse form element: {e}")

    for table in horse_form_tag:
        horse_number_cells = table.find_all('span', class_='horse-number')
        horse_numbers = [horse.text for horse in horse_number_cells] if horse_number_cells else ["No value"]
        horse_name_cells = table.find_all('span', class_='horse-name')
        horse_names = [horse.find('a').text for horse in horse_name_cells if horse.find('a')] if horse_name_cells else ["No value"]
        record_all_elements = table.find_all('b', string='Record:')
        records_all = [record.next_sibling.strip() for record in record_all_elements if record.next_sibling] if record_all_elements else ["No value"]
        first_up_elements = table.find_all('b', string='1st Up:')
        first_up = [record.next_sibling.strip() for record in first_up_elements if record.next_sibling] if first_up_elements else ["No value"]
        second_up_elements = table.find_all('b', string='2nd Up:')
        second_up = [record.next_sibling.strip() for record in second_up_elements if record.next_sibling] if second_up_elements else ["No value"]
        record_track_elements = table.find_all('b', string='Track:')
        record_track = [record.next_sibling.strip() for record in record_track_elements if record.next_sibling] if record_track_elements else ["No value"]
        dist_elements = table.find_all('b', string='Dist:')
        dist = [record.next_sibling.strip() for record in dist_elements if record.next_sibling] if dist_elements else ["No value"]
        firm_elements = table.find_all('b', string='Firm:')
        firm = [record.next_sibling.strip() for record in firm_elements if record.next_sibling] if firm_elements else ["No value"]
        good_elements = table.find_all('b', string='Good:')
        good = [record.next_sibling.strip() for record in good_elements if record.next_sibling] if good_elements else ["No value"]
        soft_elements = table.find_all('b', string='Soft:')
        soft = [record.next_sibling.strip() for record in soft_elements if record.next_sibling] if soft_elements else ["No value"]
        heavy_elements = table.find_all('b', string='Heavy:')
        heavy = [record.next_sibling.strip() for record in heavy_elements if record.next_sibling] if heavy_elements else ["No value"]
        synthetic_elements = table.find_all('b', string='Synthetic:')
        synthetic = [record.next_sibling.strip() for record in synthetic_elements if record.next_sibling] if synthetic_elements else ["No value"]
        
        #print(f"Lengths - horse_numbers: {len(horse_numbers)}, horse_names: {len(horse_names)}, records_all: {len(records_all)}, record_track: {len(record_track)}, record_good: {len(record_good)}")

        for num, name, rall, fup, sup, rtrk, dst, frm, gd, sft, hvy, syn in zip(horse_numbers, horse_names, records_all, first_up, second_up, record_track, dist, firm, good, soft, heavy, synthetic):
            hf_data = ({
                'HorseNumber': num,
                'HorseName': name,
                'Record': rall,
                'FirstUp': fup,
                'SecondUp': sup,
                'RecordTrack': rtrk,
                'RecordDistance': dst,
                'RecordFirm': frm,
                'RecordGood': gd,
                'RecordSoft': sft,
                'RecordHeavy': hvy,
                'RecordSynthetic': syn
            })
        if "No value" in hf_data.values():
            missing_data_horses.append(hf_data)
        horse_form_data.append(hf_data)
    horse_form_df = pd.DataFrame(horse_form_data)
    print(horse_form_df)
    # Return the CSV as a downloadable file
    return  horse_form_df

def raw_to_trn_form(soup):
    df = horse_form(soup)
    try:
        #Split columns by delimeter to get a column with places and one with totals
        df[['Record_total', 'Record_places']] = df['Record'].str.split(':', expand=True)
        df[['Record_fup_total', 'Record_fup_places']] = df['FirstUp'].str.split(':', expand=True)
        df[['Record_sup_total', 'Record_sup_places']] = df['SecondUp'].str.split(':', expand=True)
        df[['Record_trk_total', 'Record_trk_places']] = df['RecordTrack'].str.split(':', expand=True)
        df[['Record_dist_total', 'Record_dist_places']] = df['RecordDistance'].str.split(':', expand=True)
        df[['Record_firm_total', 'Record_firm_places']] = df['RecordFirm'].str.split(':', expand=True)
        df[['Record_good_total', 'Record_good_places']] = df['RecordGood'].str.split(':', expand=True)
        df[['Record_soft_total', 'Record_soft_places']] = df['RecordSoft'].str.split(':', expand=True)
        df[['Record_heavy_total', 'Record_heavy_places']] = df['RecordHeavy'].str.split(':', expand=True)
        df[['Record_syn_total', 'Record_syn_places']] = df['RecordSynthetic'].str.split(':', expand=True)

        #Split each column so that you get 1st, 2nd and 3rd places in their own column
        df[['Record_1st', 'Record_2nd', 'Record_3rd']] = df['Record_places'].str.split('-', expand=True)
        df[['Record_fup_1st', 'Record_fup_2nd', 'Record_fup_3rd']] = df['Record_fup_places'].str.split('-', expand=True)
        df[['Record_sup_1st', 'Record_sup_2nd', 'Record_sup_3rd']] = df['Record_sup_places'].str.split('-', expand=True)
        df[['Record_trk_1st', 'Record_trk_2nd', 'Record_trk_3rd']] = df['Record_trk_places'].str.split('-', expand=True)
        df[['Record_dist_1st', 'Record_dist_2nd', 'Record_dist_3rd']] = df['Record_dist_places'].str.split('-', expand=True)
        df[['Record_firm_1st', 'Record_firm_2nd', 'Record_firm_3rd']] = df['Record_firm_places'].str.split('-', expand=True)
        df[['Record_good_1st', 'Record_good_2nd', 'Record_good_3rd']] = df['Record_good_places'].str.split('-', expand=True)
        df[['Record_soft_1st', 'Record_soft_2nd', 'Record_soft_3rd']] = df['Record_soft_places'].str.split('-', expand=True)
        df[['Record_heavy_1st', 'Record_heavy_2nd', 'Record_heavy_3rd']] = df['Record_heavy_places'].str.split('-', expand=True)
        df[['Record_syn_1st', 'Record_syn_2nd', 'Record_syn_3rd']] = df['Record_syn_places'].str.split('-', expand=True)

        #Convert each column to float
        cols_to_float = [
            'Record_1st', 'Record_2nd', 'Record_3rd',
            'Record_fup_1st', 'Record_fup_2nd', 'Record_fup_3rd',
            'Record_sup_1st', 'Record_sup_2nd', 'Record_sup_3rd',
            'Record_trk_1st', 'Record_trk_2nd', 'Record_trk_3rd',
            'Record_dist_1st', 'Record_dist_2nd', 'Record_dist_3rd',
            'Record_firm_1st', 'Record_firm_2nd', 'Record_firm_3rd',
            'Record_good_1st', 'Record_good_2nd', 'Record_good_3rd',
            'Record_soft_1st', 'Record_soft_2nd', 'Record_soft_3rd',
            'Record_heavy_1st', 'Record_heavy_2nd', 'Record_heavy_3rd',
            'Record_syn_1st', 'Record_syn_2nd', 'Record_syn_3rd'
        ]
        df[cols_to_float] = df[cols_to_float].astype(float)

        #Sum each of the place columns into one column
        df['Record_sum_places'] = df[['Record_1st', 'Record_2nd', 'Record_3rd']].sum(axis=1)
        df['Record_fup_sum_places'] = df[['Record_fup_1st', 'Record_fup_2nd', 'Record_fup_3rd']].sum(axis=1)
        df['Record_sup_sum_places'] = df[['Record_sup_1st', 'Record_sup_2nd', 'Record_sup_3rd']].sum(axis=1)
        df['Record_trk_sum_places'] = df[['Record_trk_1st', 'Record_trk_2nd', 'Record_trk_3rd']].sum(axis=1)
        df['Record_dist_sum_places'] = df[['Record_dist_1st', 'Record_dist_2nd', 'Record_dist_3rd']].sum(axis=1)
        df['Record_firm_sum_places'] = df[['Record_firm_1st', 'Record_firm_2nd', 'Record_firm_3rd']].sum(axis=1)
        df['Record_good_sum_places'] = df[['Record_good_1st', 'Record_good_2nd', 'Record_good_3rd']].sum(axis=1)
        df['Record_soft_sum_places'] = df[['Record_soft_1st', 'Record_soft_2nd', 'Record_soft_3rd']].sum(axis=1)
        df['Record_heavy_sum_places'] = df[['Record_heavy_1st', 'Record_heavy_2nd', 'Record_heavy_3rd']].sum(axis=1)
        df['Record_syn_sum_places'] = df[['Record_syn_1st', 'Record_syn_2nd', 'Record_syn_3rd']].sum(axis=1)

        #Convert total columns to float, replacing the No Value string
        tot_cols_to_float = [
            'Record_total', 'Record_fup_total', 'Record_sup_total', 'Record_trk_total', 'Record_dist_total',
            'Record_firm_total', 'Record_good_total', 'Record_soft_total', 'Record_heavy_total', 'Record_syn_total'
        ]
        df[tot_cols_to_float] = df[tot_cols_to_float].replace('No value', np.nan).astype(float)

        #Create place rate columns
        df['Record_place_rate'] = df['Record_sum_places'] / df['Record_total'].replace(0, pd.NA)
        df['Record_trk_place_rate'] = df['Record_fup_sum_places'] / df['Record_trk_total'].replace(0, pd.NA)
        df['Record_dist_place_rate'] = df['Record_sup_sum_places'] / df['Record_dist_total'].replace(0, pd.NA)
        df['Record_trk_place_rate'] = df['Record_trk_sum_places'] / df['Record_trk_total'].replace(0, pd.NA)
        df['Record_dist_place_rate'] = df['Record_dist_sum_places'] / df['Record_dist_total'].replace(0, pd.NA)
        df['Record_firm_place_rate'] = df['Record_firm_sum_places'] / df['Record_firm_total'].replace(0, pd.NA)
        df['Record_good_place_rate'] = df['Record_good_sum_places'] / df['Record_good_total'].replace(0, pd.NA)
        df['Record_soft_place_rate'] = df['Record_soft_sum_places'] / df['Record_soft_total'].replace(0, pd.NA)
        df['Record_heavy_place_rate'] = df['Record_heavy_sum_places'] / df['Record_heavy_total'].replace(0, pd.NA)
        df['Record_syn_place_rate'] = df['Record_syn_sum_places'] / df['Record_syn_total'].replace(0, pd.NA)

        df_form_trn = df
        return df_form_trn
    except Exception as e:
        print(f"Error transforming horse form raw data: {e}")

def first_second_up_handler(value, soup):
    df = raceday_field(soup)
    df['LastTen'] = df['LastTen'].fillna('').astype(str)
    try:
        value = str(value) if value else 'NaN'
        if not value:  # If the value is empty or None, return ''
            return ''
        if value[-1] == 'x':  # Check the rightmost character
            return 'First Up'
        elif len(value) > 1 and value[-2] == 'x':  # Check the second rightmost character
            return 'Second Up'
        else:
            return ''
    except Exception as e:
        print(f"Error handling first and second up values in Last 10 column: {e}")

def raw_to_trn_field(soup):
    try:
        df = raceday_field(soup)
        df['HorseWeight'] = df['HorseWeight'].str.replace('kg', '').astype(float)
        df['FirstSecondUp'] = df['LastTen'].apply(lambda value: first_second_up_handler(value, soup))

        df_field_trn = df
        return df_field_trn
    except Exception as e:
        print(f"Error transforming raceday field raw data: {e}")

def raw_to_trn_meta(soup):
    df = raceday_meta(soup)
    df['RaceNumber'] = df['RaceNumber'].astype(int)

    df_trn_meta = df
    return df_trn_meta

def join_datasets(soup):
    try:
        df_meta = raw_to_trn_meta(soup)
        df_field = raw_to_trn_field(soup)
        df_form = raw_to_trn_form(soup)

        df_meta_field = pd.merge(df_meta, df_field, how='left', on='RaceNumber')

        df_mff = pd.merge(df_meta_field, df_form, how='left', on='HorseName')

        print(f"Joined tables into one")
        return df_mff       
    except Exception as e:
        print(f"Error producing reporting data joins: {e}")

# def up_ratio(soup):
#     try:
#         df_mff = join_datasets(soup)

#         # Compute UpRatio based on the 'FirstSecondUp' condition
#         df_mff['UpRatio'] = np.where(
#             df_mff['FirstSecondUp'] == 'First Up',
#             (df_mff['Record_fup_sum_places'] + df_mff['Record_trk_sum_places'] + df_mff['Record_dist_sum_places']) /
#             (df_mff['Record_fup_total'] + df_mff['Record_trk_total'] + df_mff['Record_dist_total']).replace(0, np.nan),
#             np.where(
#                 df_mff['FirstSecondUp'] == 'Second Up',
#                 (df_mff['Record_sup_sum_places'] + df_mff['Record_trk_sum_places'] + df_mff['Record_dist_sum_places']) /
#                 (df_mff['Record_sup_total'] + df_mff['Record_trk_total'] + df_mff['Record_dist_total']).replace(0, np.nan),
#                 (df_mff['Record_trk_sum_places'] + df_mff['Record_dist_sum_places']) /
#                 (df_mff['Record_trk_total'] + df_mff['Record_dist_total']).replace(0, np.nan)
#             )
#         )

#         print(f"Added up ratio")
#         return df_mff
    
#     except Exception as e:
#         print(f"Error creating Up Ratio: {e}")

#Function to conditionally delete columns and create Suitability index
def conditional_col_deletes(track_conditions, soup):
    track_conditions = get_track_conditions(track_conditions)
    try:
        df_mff = join_datasets(soup)

        if track_conditions == 'Good':
            # Drop unnecessary columns
            df_mff.drop(
                ['RecordFirm', 'RecordSoft', 'RecordHeavy', 'RecordSynthetic', 
                 'Record_firm_place_rate', 'Record_soft_place_rate', 'Record_heavy_place_rate', 'Record_syn_place_rate'], 
                axis=1, inplace=True
            )

            def calculate_suitability(row):
                if row['Record_good_total'] == 0:
                    return round(row['UpRatio'] + 0.5, 2)
                else:
                    return np.where(
                        row['FirstSecondUp'] == 'First Up',
                        (row['Record_fup_sum_places'] + row['Record_trk_sum_places'] + row['Record_dist_sum_places'] + row['Record_good_sum_places']) /
                        (row['Record_fup_total'] + row['Record_trk_total'] + row['Record_dist_total'] + row['Record_good_total']).replace(0, np.nan),
                        np.where(
                            row['FirstSecondUp'] == 'Second Up',
                            (row['Record_sup_sum_places'] + row['Record_trk_sum_places'] + row['Record_dist_sum_places'] + row['Record_good_sum_places']) /
                            (row['Record_sup_total'] + row['Record_trk_total'] + row['Record_dist_total'] + row['Record_good_total']).replace(0, np.nan),
                            (row['Record_trk_sum_places'] + row['Record_dist_sum_places'] + row['Record_good_sum_places']) /
                            (row['Record_trk_total'] + row['Record_dist_total'] + row['Record_good_total']).replace(0, np.nan)
                        )
                    )
                    # return round(row['UpRatio'] + (row['Record_good_sum_places'] / row['Record_good_total']), 2)
            
            # Apply the helper function row-wise
            df_mff['Suitability_index'] = df_mff.apply(calculate_suitability, axis=1)

        # elif track_conditions == 'Soft/Heavy':

        #     # Drop unnecessary columns
        #     df_mff.drop(
        #         ['RecordFirm', 'RecordGood', 'RecordSynthetic', 
        #          'Record_firm_place_rate', 'Record_good_place_rate', 'Record_syn_place_rate'], 
        #         axis=1, inplace=True
        #     )

        #     def calculate_suitability(row):
        #         if row['Record_soft_total'] == 0 and row['Record_heavy_total'] == 0:
        #             return round(row['UpRatio'] + 0.5, 2)
        #         elif row['Record_soft_total'] == 0 and row['Record_heavy_total'] != 0:
        #             return round(row['UpRatio'] + row['Record_heavy_place_rate'], 2)
        #         elif row['Record_soft_total'] != 0 and row['Record_heavy_total'] == 0:
        #             return round(row['UpRatio'] + row['Record_soft_place_rate'], 2)
        #         else:
        #             return round(
        #                 row['UpRatio'] + 
        #                 ((row['Record_soft_sum_places'] + row['Record_heavy_sum_places']) / 
        #                     (row['Record_soft_total'] + row['Record_heavy_total'])), 2
        #             )

        #     # Apply the helper function row-wise
        #     df_mff['Suitability_index'] = df_mff.apply(calculate_suitability, axis=1)
        
        print("Conditionally deleted columns and calculated suitability based off of conditions")
        return df_mff
    
    except Exception as e:
        print(f"Error processing condtional columns: {e}")

#Function to drop unnecessary columns
def drop_col(track_conditions, soup):
    df_output = conditional_col_deletes(track_conditions, soup)

    df_output.drop(['Record_total',
        'Record_places', 'Record_fup_total', 'Record_fup_places',
        'Record_sup_total', 'Record_sup_places', 'Record_trk_total',
        'Record_trk_places', 'Record_dist_total', 'Record_dist_places',
        'Record_firm_total', 'Record_firm_places', 'Record_good_total',
        'Record_good_places', 'Record_soft_total', 'Record_soft_places',
        'Record_heavy_total', 'Record_heavy_places', 'Record_syn_total',
        'Record_syn_places', 'Record_1st', 'Record_2nd', 'Record_3rd',
        'Record_fup_1st', 'Record_fup_2nd', 'Record_fup_3rd', 'Record_sup_1st',
        'Record_sup_2nd', 'Record_sup_3rd', 'Record_trk_1st', 'Record_trk_2nd',
        'Record_trk_3rd', 'Record_dist_1st', 'Record_dist_2nd',
        'Record_dist_3rd', 'Record_firm_1st', 'Record_firm_2nd',
        'Record_firm_3rd', 'Record_good_1st', 'Record_good_2nd',
        'Record_good_3rd', 'Record_soft_1st', 'Record_soft_2nd',
        'Record_soft_3rd', 'Record_heavy_1st', 'Record_heavy_2nd',
        'Record_heavy_3rd', 'Record_syn_1st', 'Record_syn_2nd',
        'Record_syn_3rd', 'Record_sum_places', 'Record_fup_sum_places',
        'Record_sup_sum_places', 'Record_trk_sum_places',
        'Record_dist_sum_places', 'Record_firm_sum_places',
        'Record_good_sum_places', 'Record_soft_sum_places',
        'Record_heavy_sum_places', 'Record_syn_sum_places', 'EventNumber', 'HorseNumber_y'], axis=1, inplace=True)

    return df_output


