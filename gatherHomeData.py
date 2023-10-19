# Script to get data from the wesite of my choice, get the follwoing data: location, price and area

import requests
from bs4 import BeautifulSoup
import re
import time
import csv

BASE_URL = "XXXX"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
}
MAX_PAGES = 10  # Set the maximum number of pages you want to scrape

# Open the CSV file for writing
with open('property_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Location', 'Price', 'Rooms', 'Area']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()  # Write the header row

    for page_num in range(1, MAX_PAGES + 1):
        print(f"Scraping page {page_num}...")
        URL = f"{BASE_URL}?ep={page_num}&ipd=true"

        response = requests.get(URL, headers=HEADERS)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract and process locations based on the address tag
            raw_locations = soup.find_all('address', translate="no")
            locations = []
            for loc in raw_locations:
                match = re.search(r'\d{4}\s*(.*)', loc.text)
                if match:
                    location_name = match.group(1).strip()
                    location_name = location_name.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
                    locations.append(location_name)

            # Extract prices
            prices = soup.find_all('span', class_='HgListingCard_price_sIIoV')

            # Extract room numbers and living area
            details = soup.find_all('div', class_='HgListingRoomsLivingSpace_roomsLivingSpace_FiW9E')

            min_len = min(len(locations), len(prices), len(details))

            for i in range(min_len):
                location = locations[i]
                raw_price = prices[i].text.strip()

                if "Preis auf Anfrage" in raw_price:
                    cleaned_price = "N/A"
                else:
                    cleaned_price = raw_price.replace("CHF", "").replace("’", "").replace(".", "").replace("–", "").strip()

                # Extracting rooms and living area
                detail_spans = details[i].find_all('span')
                
                if len(detail_spans) > 0:
                    room_text = detail_spans[0].text.strip()
                    match = re.search(r'(\d+\.?\d*)', room_text)  # Extract numeric value using regex
                    rooms = match.group(1) if match else 'N/A'   # Store only the numeric value
                else:
                    rooms = 'N/A'

                if len(detail_spans) > 1:
                    area_text = detail_spans[1].text.strip()
                    match = re.search(r'(\d+\.?\d*)', area_text)  # Extract numeric value using regex
                    area = match.group(1) if match else 'N/A'    # Store only the numeric value
                else:
                    area = 'N/A'

                # Write to CSV
                writer.writerow({'Location': location, 'Price': cleaned_price, 'Rooms': rooms, 'Area': area})

        else:
            print(f"Failed to retrieve page {page_num}. Status code:", response.status_code)

        # Optionally add a delay to prevent hitting the server too quickly
        time.sleep(2)

print("Scraping completed. Data saved to property_data.csv.")
