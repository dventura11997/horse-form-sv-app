import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import re

# URL to scrape
url = "https://racingaustralia.horse/FreeFields/Form.aspx?Key=2025Jan01%2CVIC%2CFlemington"

try:
    #Create date variables for folder paths
    current_date = datetime.now()
    day = current_date.day
    month = current_date.month
    year = current_date.year

    print(f"Successfully created date variables")

    # Extract state and track name from url for folder paths
    state = re.search(r"Key=\d{4}\w+%2C([A-Z]+)%2C", url).group(1)
    track = re.search(r"Key=\d{4}\w+%2C[A-Z]+%2C(.+)$", url).group(1).replace('%20', ' ')
    print(f"Successfully found {state} and {track} in url")

except Exception as e:
    print(f"Error getting this getting folder path params")

def make_folder():
    parent_folder = Path("C:/Users/danie/OneDrive/Work/Career/Coding/Folio/Horse Racing Form/data")
    subfolder = parent_folder / f"{day}_{month}_{year}_{state}_{track}"

    if subfolder.exists:
        print("Folder already exists")
    else:
        subfolder.mkdir(parents=True, exist_ok=True)

    return subfolder

subfolder = make_folder()

df = pd.read_excel(subfolder / f"horse_form_raw_{day}_{month}_{year}_{state}_{track}.xlsx")


def raw_to_trn_form():
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

        #print(df)

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

        #Output trn data
        df.to_excel(subfolder / f"horse_form_trn_{day}_{month}_{year}_{state}_{track}.xlsx", index=False)
    except Exception as e:
        print(f"Error transforming horse form raw data: {e}")

raw_to_trn_form()

def first_second_up_handler(value):
    df = pd.read_excel(subfolder / f"raceday_field_raw_{day}_{month}_{year}_{state}_{track}.xlsx")
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

def raw_to_trn_field():
    try:
        df = pd.read_excel(subfolder / f"raceday_field_raw_{day}_{month}_{year}_{state}_{track}.xlsx")
        df['HorseWeight'] = df['HorseWeight'].str.replace('kg', '').astype(float)
        df['FirstSecondUp'] = df['LastTen'].apply(first_second_up_handler)

        df.to_excel(subfolder / f"raceday_field_trn_{day}_{month}_{year}_{state}_{track}.xlsx", index=False)
    except Exception as e:
        print(f"Error transforming raceday field raw data: {e}")

raw_to_trn_field()




