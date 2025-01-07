import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import re

# URL to scrape
url = "{url_required}"

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


#Function to integrate the datasets and join them together
def join_datasets():
    try:
        df_meta = pd.read_excel(subfolder / f"raceday_meta_raw_{day}_{month}_{year}_{state}_{track}.xlsx")
        df_field = pd.read_excel(subfolder / f"raceday_field_trn_{day}_{month}_{year}_{state}_{track}.xlsx")
        df_form = pd.read_excel(subfolder / f"horse_form_trn_{day}_{month}_{year}_{state}_{track}.xlsx")

        df_meta_field = pd.merge(df_meta, df_field, how='left', on='RaceNumber')

        df_mff = pd.merge(df_meta_field, df_form, how='left', on='HorseName')

        print(f"Joined tables into one: {subfolder}")
        return df_mff       
    
    except Exception as e:
        print(f"Error producing reporting data joins: {e}")

#Function to create a conditional ratio which feeds into the suitability index based on whether a horse is first up, second up or neither.
#Logic:
# If first up = first_up + track + distance (combined ratio, max 1)
# If second up = second_up + track + distance (combined ratio, max 1)
# Else = track + distance (combined ratio, max 1)
def up_ratio():
    try:
        df_mff = join_datasets()

        # Compute UpRatio based on the 'FirstSecondUp' condition
        df_mff['UpRatio'] = np.where(
            df_mff['FirstSecondUp'] == 'First Up',
            (df_mff['Record_fup_sum_places'] + df_mff['Record_trk_sum_places'] + df_mff['Record_dist_sum_places']) /
            (df_mff['Record_fup_total'] + df_mff['Record_trk_total'] + df_mff['Record_dist_total']).replace(0, np.nan),
            np.where(
                df_mff['FirstSecondUp'] == 'Second Up',
                (df_mff['Record_sup_sum_places'] + df_mff['Record_trk_sum_places'] + df_mff['Record_dist_sum_places']) /
                (df_mff['Record_sup_total'] + df_mff['Record_trk_total'] + df_mff['Record_dist_total']).replace(0, np.nan),
                (df_mff['Record_trk_sum_places'] + df_mff['Record_dist_sum_places']) /
                (df_mff['Record_trk_total'] + df_mff['Record_dist_total']).replace(0, np.nan)
            )
        )

        return df_mff
    
    except Exception as e:
        print(f"Error creating Up Ratio: {e}")

track_conditions = 'Good'

#Function to conditionally delete columns and create Suitability index
def conditional_col_deletes():
    try:
        df_mff = up_ratio()

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
                    return round(row['UpRatio'] + (row['Record_good_sum_places'] / row['Record_good_total']), 2)
            
            # Apply the helper function row-wise
            df_mff['Suitability_index'] = df_mff.apply(calculate_suitability, axis=1)

        elif track_conditions == 'Soft/Heavy':

            # Drop unnecessary columns
            df_mff.drop(
                ['RecordFirm', 'RecordGood', 'RecordSynthetic', 
                 'Record_firm_place_rate', 'Record_good_place_rate', 'Record_syn_place_rate'], 
                axis=1, inplace=True
            )

            def calculate_suitability(row):
                if row['Record_soft_total'] == 0 and row['Record_heavy_total'] == 0:
                    return round(row['UpRatio'] + 0.5, 2)
                elif row['Record_soft_total'] == 0 and row['Record_heavy_total'] != 0:
                    return round(row['UpRatio'] + row['Record_heavy_place_rate'], 2)
                elif row['Record_soft_total'] != 0 and row['Record_heavy_total'] == 0:
                    return round(row['UpRatio'] + row['Record_soft_place_rate'], 2)
                else:
                    return round(
                        row['UpRatio'] + 
                        ((row['Record_soft_sum_places'] + row['Record_heavy_sum_places']) / 
                            (row['Record_soft_total'] + row['Record_heavy_total'])), 2
                    )

            # Apply the helper function row-wise
            df_mff['Suitability_index'] = df_mff.apply(calculate_suitability, axis=1)
        
        return df_mff
    
    except Exception as e:
        print(f"Error processing condtional columns: {e}")

#Function to drop unnecessary columns
def drop_col():
    df_trn = conditional_col_deletes()
    #print(df_trn.columns)

    df_trn.drop(['Record_total',
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

    df_trn.to_excel(subfolder / f"horse_form_int_{day}_{month}_{year}_{state}_{track}.xlsx", index=False)


drop_col()