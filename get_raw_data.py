import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from pathlib import Path

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

    print(f"Checking folder: {subfolder}")
    if not subfolder.exists():
        print("Folder does not exist. Creating...")
        subfolder.mkdir(parents=True, exist_ok=True)
        print(f"Folder created: {subfolder}")
    else:
        print(f"Folder already exists: {subfolder}")
    
    # Confirm folder existence
    if subfolder.exists():
        print("Confirmed: Folder exists.")
    else:
        print("Error: Folder creation failed.")

    return subfolder

subfolder = make_folder()



# Send a GET request
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

def get_request():
    try:
        print(f"Successfully accessed url: {response.status_code}")
    except Exception as e:
        print(f"Error accessing url: {e}")

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"Successfully parsed html")
    except Exception as e:
        print(f"Error parsing html: {e}")

get_request()

def raceday_meta():
    try:
        # Locate the table element
        raceday_meta_tag = soup.find_all('table', class_='race-title')
        raceday_meta_data = []
        print(f"Successfully found raceday meta element: {raceday_meta_tag[0]}")
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
    raceday_meta_df.to_excel(subfolder / f"raceday_meta_raw_{day}_{month}_{year}_{state}_{track}.xlsx", index=False)

#

def raceday_field():
    try:
        raceday_field_tag = soup.find_all('table', class_='race-strip-fields')
        raceday_field_data = []
        print(f"Successfully found raceday field element: {raceday_field_tag[0]}")
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
    raceday_field_df.to_excel(subfolder / f"raceday_field_raw_{day}_{month}_{year}_{state}_{track}.xlsx", index=False)
    


def horse_form():
    try:
        horse_form_tag = soup.find_all('table', class_='horse-form-table')
        horse_form_data = []
        missing_data_horses = []
        print(f"Successfully found horse form element: {horse_form_tag[0]}")
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
    #print(horse_form_df)
    print(missing_data_horses)
    horse_form_df.to_excel(subfolder / f"horse_form_raw_{day}_{month}_{year}_{state}_{track}.xlsx", index=False)

#print(horse_form_df)
raceday_meta()
raceday_field()
horse_form()


