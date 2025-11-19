import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Base URL of the good practices page
base_url = "https://circulareconomy.europa.eu/platform/en/good-practices"

def get_good_practices(session, page_url, retries=3, delay=5):
    for attempt in range(retries):
        print(f"Fetching URL: {page_url}, Attempt: {attempt + 1}")
        try:
            response = session.get(page_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                practices = soup.find_all('div', class_='node--type-cecon-good-practice')
                print(f"Found {len(practices)} practices on the page")
                data = []
                for practice in practices:
                    title_tag = practice.find('h2')
                    title = title_tag.get_text(strip=True) if title_tag else 'N/A'
                    link = title_tag.find('a')['href'] if title_tag and title_tag.find('a') else 'N/A'
                    
                    description_tag = practice.find('div', class_='field-wrapper field field-node--field-cecon-abstract field-name-field-cecon-abstract field-type-text-long field-label-hidden')
                    description = description_tag.get_text(strip=True) if description_tag else 'N/A'
                    
                    organization_tag = practice.find('div', class_='field-wrapper field field-node--field-cecon-organisation-company field-name-field-cecon-organisation-company field-type-link field-label-above')
                    organization = organization_tag.find('a').get_text(strip=True) if organization_tag and organization_tag.find('a') else 'N/A'
                
                    type_of_org_tag = practice.find('div', class_='field-wrapper field field-node--field-cecon-contributor-category field-name-field-cecon-contributor-category field-type-entity-reference field-label-above')
                    type_of_org = type_of_org_tag.find('a').get_text(strip=True) if type_of_org_tag and type_of_org_tag.find('a') else 'N/A'
                    
                    country_tag = practice.find('div', class_='field-wrapper field field-node--field-cecon-country field-name-field-cecon-country field-type-country field-label-above')
                    country = country_tag.find('div', class_='field-item').get_text(strip=True) if country_tag else 'N/A'
                    
                    language_tag = practice.find('div', class_='field-wrapper field field-node--field-cecon-main-language field-name-field-cecon-main-language field-type-entity-reference field-label-above')
                    language = language_tag.find('a').get_text(strip=True) if language_tag and language_tag.find('a') else 'N/A'
                    
                    key_area_tag = practice.find('div', class_='field-wrapper field field-node--field-cecon-key-area field-name-field-cecon-key-area field-type-entity-reference field-label-above')
                    key_area = ', '.join([a.get_text(strip=True) for a in key_area_tag.find_all('a')]) if key_area_tag else 'N/A'
                    
                    sector_tag = practice.find('div', class_='field-wrapper field field-node--field-cecon-sector field-name-field-cecon-sector field-type-entity-reference field-label-above')
                    sector = ', '.join([a.get_text(strip=True) for a in sector_tag.find_all('a')]) if sector_tag else 'N/A'
                    
                    scope_tag = practice.find('div', class_='field-wrapper field field-node--field-cecon-scope field-name-field-cecon-scope field-type-entity-reference field-label-above')
                    scope = ', '.join([a.get_text(strip=True) for a in scope_tag.find_all('a')]) if scope_tag else 'N/A'
                    
                    data.append({
                        'Title': title,
                        'Description': description,
                        'Link': f"https://circulareconomy.europa.eu{link}",
                        'Organisation': organization,
                        'Type of Organisation': type_of_org,
                        'Country': country,
                        'Language': language,
                        'Key Area': key_area,
                        'Sector': sector,
                        'Scope': scope
                    })

                    # Debugging each entry
                    print(f"Title: {title}")
                    print(f"Description: {description}")
                    print(f"Link: {link}")
                    print(f"Organisation: {organization}")
                    print(f"Type of Organisation: {type_of_org}")
                    print(f"Country: {country}")
                    print(f"Language: {language}")
                    print(f"Key Area: {key_area}")
                    print(f"Sector: {sector}")
                    print(f"Scope: {scope}")
                    print("---")

                return data
            else:
                print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        
        print(f"Retrying in {delay} seconds...")
        time.sleep(delay)
    
    print(f"Failed to retrieve data after {retries} attempts.")
    return []

# Scraping multiple pages (pagination handling)
def scrape_all_pages(skip_pages=[]):
    session = requests.Session()
    all_data = []
    page = 0
    while True:
        if page in skip_pages:
            print(f"Skipping page {page} as requested.")
            page += 1
            continue
        page_url = f"{base_url}?page={page}"
        page_data = get_good_practices(session, page_url)
        if not page_data:
            print(f"No data found on page {page}, stopping.")
            break
        all_data.extend(page_data)
        print(f"Page {page} data extracted. Total records so far: {len(all_data)}")
        page += 1
        # Assuming there are around 80 pages
        if page >= 80:
            break
    return all_data

# Main execution
if __name__ == "__main__":
    print("Starting the scraping process...")
    skip_pages = [64]  # Add pages you want to skip here
    data = scrape_all_pages(skip_pages=skip_pages)
    if data:
        df = pd.DataFrame(data)
        df.to_csv('good_practices.csv', index=False)
        print("Data has been successfully extracted and saved to 'good_practices.csv'")
    else:
        print("No data was extracted.")
