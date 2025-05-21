pip install "pandas>=1.3.0" "numpy>=1.20.0" "matplotlib>=3.4.0" "beautifulsoup4>=4.9.0" "requests>=2.25.0" "regex>=2021.4.4" "sqlalchemy>=1.4.0"
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse
import argparse
import sys # Import the sys module

# Constants definition
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "dnt": "1",
    "priority": "i",
    "Referer": "http://www.wikipedia.org/",
    "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "image",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "same-origin",
    "sec-fetch-storage-access": "active",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
}
# Define different types of data sources
DATA_SOURCES = {
    "mens_swimming": [
        (
            "College of Staten Island",
            "https://csidolphins.com/sports/mens-swimming-and-diving/roster",
        ),
        (
            "York College",
            "https://yorkathletics.com/sports/mens-swimming-and-diving/roster",
        ),
        (
            "Baruch College",
            "https://athletics.baruch.cuny.edu/sports/mens-swimming-and-diving/roster",
        ),
        (
            "Brooklyn College",
            "https://www.brooklyncollegeathletics.com/sports/mens-swimming-and-diving/roster",
        ),
        (
            "Lindenwood University",
            "https://lindenwoodlions.com/sports/mens-swimming-and-diving/roster",
        ),
        (
            "Mckendree University",
            "https://mckbearcats.com/sports/mens-swimming-and-diving/roster",
        ),
        (
            "Ramapo College",
            "https://ramapoathletics.com/sports/mens-swimming-and-diving/roster",
        ),
        (
            "SUNY Oneonta",
            "https://oneontaathletics.com/sports/mens-swimming-and-diving/roster",
        ),
        (
            "SUNY Binghamton",
            "https://bubearcats.com/sports/mens-swimming-and-diving/roster/2021-22",
        ),
        (
            "Albright College",
            "https://albrightathletics.com/sports/mens-swimming-and-diving/roster/2021-22",
        ),
    ],
    "womens_swimming": [
        (
            "College of Staten Island",
            "https://csidolphins.com/sports/womens-swimming-and-diving/roster",
        ),
        (
            "Queens College",
            "https://queensknights.com/sports/womens-swimming-and-diving/roster",
        ),
        (
            "York College",
            "https://yorkathletics.com/sports/womens-swimming-and-diving/roster",
        ),
        (
            "Baruch College",
            "https://athletics.baruch.cuny.edu/sports/womens-swimming-and-diving/roster/2021-22?path=wswim",
        ),
        (
            "Brooklyn College",
            "https://www.brooklyncollegeathletics.com/sports/womens-swimming-and-diving/roster",
        ),
        (
            "Lindenwood University",
            "https://lindenwoodlions.com/sports/womens-swimming-and-diving/roster",
        ),
        (
            "Mckendree University",
            "https://mckbearcats.com/sports/womens-swimming-and-diving/roster",
        ),
        (
            "Ramapo College",
            "https://ramapoathletics.com/sports/womens-swimming-and-diving/roster",
        ),
        (
            "Kean University",
            "https://keanathletics.com/sports/womens-swimming-and-diving/roster",
        ),
        (
            "SUNY Oneonta",
            "https://oneontaathletics.com/sports/womens-swimming-and-diving/roster",
        ),
    ],
    "mens_volleyball": [
        (
            "City College of New York",
            "https://ccnyathletics.com/sports/mens-volleyball/roster",
        ),
        ("Lehman College", "https://lehmanathletics.com/sports/mens-volleyball/roster"),
        (
            "Brooklyn College",
            "https://www.brooklyncollegeathletics.com/sports/mens-volleyball/roster",
        ),
        (
            "John Jay College",
            "https://johnjayathletics.com/sports/mens-volleyball/roster",
        ),
        (
            "Baruch College",
            "https://athletics.baruch.cuny.edu/sports/mens-volleyball/roster",
        ),
        (
            "Medgar Evers College",
            "https://mecathletics.com/sports/mens-volleyball/roster",
        ),
        (
            "Hunter College",
            "https://www.huntercollegeathletics.com/sports/mens-volleyball/roster",
        ),
        ("York College", "https://yorkathletics.com/sports/mens-volleyball/roster"),
        ("Ball State", "https://ballstatesports.com/sports/mens-volleyball/roster"),
    ],
    "womens_volleyball": [
        ("BMCC", "https://bmccathletics.com/sports/womens-volleyball/roster"),
        ("York College", "https://yorkathletics.com/sports/womens-volleyball/roster"),
        ("Hostos CC", "https://hostosathletics.com/sports/womens-volleyball/roster"),
        ("Bronx CC", "https://bronxbroncos.com/sports/womens-volleyball/roster/2021"),
        ("Queens College", "https://queensknights.com/sports/womens-volleyball/roster"),
        ("Augusta College", "https://augustajags.com/sports/wvball/roster"),
        (
            "Flagler College",
            "https://flaglerathletics.com/sports/womens-volleyball/roster",
        ),
        ("USC Aiken", "https://pacersports.com/sports/womens-volleyball/roster"),
        (
            "Penn State - Lock Haven",
            "https://www.golhu.com/sports/womens-volleyball/roster",
        ),
    ],
}

def parse_height_to_inches(height_str):
    """
    Convert height string to inches
    Supported formats:
    - X'Y" (e.g., 6'2")
    - X-Y (e.g., 6-2)
    - X' (e.g., 6')
    - X' Y'' (e.g., 6' 0'')
    """
    try:
        # Ensure it's a string type and not empty
        if not isinstance(height_str, str) or not height_str.strip():
            return None

        height_str = height_str.strip()

        # Special handling for X' Y'' format, such as "6' 0''"
        pattern_double_quotes = re.search(r"(\d+)'\s*(\d+)''", height_str)
        if pattern_double_quotes:
            feet = int(pattern_double_quotes.group(1))
            inches = int(pattern_double_quotes.group(2))
            return (feet * 12) + inches

        # Handle X'Y" format
        if "'" in height_str and '"' in height_str:
            parts = height_str.split("'")
            feet = int(parts[0])
            inches = int(parts[1].replace('"', ""))
            return (feet * 12) + inches

        # Handle X-Y format
        elif "-" in height_str:
            parts = height_str.split("-")
            feet = int(parts[0])
            inches = int(parts[1])
            return (feet * 12) + inches

        # Handle X' format (e.g., 6')
        elif (
            "'" in height_str and not "'" in height_str[height_str.index("'") + 1 :]
        ):  # Ensure there's only one single quote
            feet_str = height_str.replace("'", "").strip()
            if feet_str.isdigit():  # Extra check if it's a pure number
                feet = int(feet_str)
                return feet * 12

        # Try to convert directly to integer, assuming it's already in inches or other units
        if height_str.isdigit():
            return int(height_str)

        # If none of the above conditions are met, return None
        print(f"Unable to parse height: {height_str}")
        return None

    except Exception as e:
        print(f"Error processing height: {height_str}, error: {str(e)}")
        return None

def fetch_html(url, max_retries=3, retry_delay=5):
    """
    Get webpage HTML content with retry mechanism

    Args:
        url: URL to fetch
        max_retries: Maximum number of retries
        retry_delay: Retry interval (seconds)

    Returns:
        HTML content on success, None on failure
    """
    retry_count = 0
    while retry_count <= max_retries:
        try:
            print(f"Attempting to fetch {url}")
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                retry_count += 1
                if retry_count <= max_retries:
                    print(
                        f"Server error (500), will retry in {retry_delay} seconds ({retry_count}/{max_retries})"
                    )
                    time.sleep(retry_delay)
                else:
                    print(f"Failed to fetch {url}, maximum retries reached: {e}")
                    return None
            else:
                print(f"Error fetching {url}: {e}")
                return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

def extract_data(html, school_name, url):
    """
    Extract athlete data from HTML
    Returns a list of tuples containing names and heights
    """
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    players_data = []
    domain = urlparse(url).netloc

    # Decide which parsing method to use based on URL
    if "athletics.com" in domain or "dolphins.com" in domain or "lions.com" in domain:
        # Handle websites using sidearm-roster-player class
        players_data = extract_sidearm_roster_player(soup, domain)

    elif "yorkathletics.com" in domain:
        # Handle websites using table layout
        players_data = extract_york_athletics(soup)

    elif "oneontaathletics.com" in domain or "queensknights.com" in domain:
        # Handle websites using sidearm-list-card-item class
        players_data = extract_sidearm_card_item(soup)

    elif "ballstatesports.com" in domain:
        # Handle Ball State special case
        players_data = extract_ballstate(soup)

    else:
        # Generic parsing method, try common patterns
        players_data = extract_generic(soup, domain)

    print(f"Extracted {len(players_data)} athlete records from {school_name}")
    return players_data

def extract_sidearm_roster_player(soup, domain):
    """Handle websites using sidearm-roster-player class"""
    players_data = []

    # Find all player entries
    player_items = soup.find_all("li", class_="sidearm-roster-player")

    for player in player_items:
        name = height = None

        # Extract name
        name_elem = player.find("h3")
        if name_elem:
            # Could be an <a> tag or direct text
            name_link = name_elem.find("a")
            if name_link:
                name = name_link.get_text(strip=True)
            else:
                name = name_elem.get_text(strip=True)

        # Extract height
        height_elem = player.find("span", class_="sidearm-roster-player-height")
        if height_elem:
            height = height_elem.get_text(strip=True)

        # Add to results if valid data is found
        if name:
            players_data.append((name, height))

    return players_data

def extract_york_athletics(soup):
    """Handle websites using table layout"""
    players_data = []

    # Find all rows
    rows = soup.find_all("tr", role="row")

    for row in rows:
        name = height = None

        # Extract name
        name_cell = row.find("td", class_="sidearm-table-player-name")
        if name_cell and name_cell.find("a"):
            name = name_cell.find("a").get_text(strip=True)

        # Extract height
        height_cell = row.find("td", class_="height")
        if height_cell:
            height = height_cell.get_text(strip=True)

        # Add to results if valid data is found
        if name:
            players_data.append((name, height))

    return players_data

def extract_sidearm_card_item(soup):
    """Handle websites using sidearm-list-card-item class"""
    players_data = []

    # Find all player cards
    player_cards = soup.find_all("li", class_="sidearm-list-card-item")

    for card in player_cards:
        name = height = None

        # Extract name - could be two parts combined or a single link
        first_name = card.find("span", class_="sidearm-roster-player-first-name")
        last_name = card.find("span", class_="sidearm-roster-player-last-name")

        if first_name and last_name:
            name = f"{first_name.get_text(strip=True)} {last_name.get_text(strip=True)}"
        else:
            # Try to find the name link
            name_link = card.find("a", class_="sidearm-roster-player-name")
            if name_link:
                name = name_link.get_text(strip=True)

        # Extract height
        height_span = card.find("span", class_="sidearm-roster-player-height")
        if height_span:
            height = height_span.get_text(strip=True)

        # Add to results if valid data is found
        if name:
            players_data.append((name, height))

    return players_data

def extract_ballstate(soup):
    """Handle Ball State special case"""
    players_data = []

    # Find all divs that might contain player information
    player_cards = soup.find_all("div", class_="s-person-card__content")

    for card in player_cards:
        name = height = None

        # Extract name
        h3_elem = card.find("h3")
        if h3_elem:
            name = h3_elem.get_text(strip=True)

        # Find span element containing height
        # Ball State uses special data test ID
        height_span = card.find(
            "span", attrs={"data-test-id": "s-person-details__bio-stats-person-season"}
        )
        if height_span:
            text = height_span.get_text(strip=True)
            # Extract height part, usually containing feet and inches
            height_match = re.search(r"(\d+'\s*\d+'')", text)
            if height_match:
                height = height_match.group(1)

        # Add to results if valid data is found
        if name:
            players_data.append((name, height))

    return players_data

def extract_generic(soup, domain):
    """Generic parsing method, try common patterns"""
    players_data = []

    # First try known structures
    # 1. Try sidearm-roster-player
    player_items = soup.find_all("li", class_="sidearm-roster-player")
    if player_items:
        return extract_sidearm_roster_player(soup, domain)

    # 2. Try table rows
    rows = soup.find_all("tr", role="row")
    if rows:
        return extract_york_athletics(soup)

    # 3. Try card items
    cards = soup.find_all("li", class_="sidearm-list-card-item")
    if cards:
        return extract_sidearm_card_item(soup)

    # If all above fail, use more generic selectors
    # Look for elements likely to contain player names
    player_elements = soup.find_all(
        ["h3", "td", "div"],
        class_=lambda c: c and ("player" in c.lower() or "name" in c.lower()),
    )

    for elem in player_elements:
        name = height = None

        # Try to get name
        name = elem.get_text(strip=True)

        # Try to find related height element
        # Start from current element and traverse up, looking for possible parent container
        parent = elem.parent
        for _ in range(3):  # Look up max 3 levels
            if not parent:
                break

            # Look for height element in this container
            height_elem = parent.find(
                ["span", "td", "div"], class_=lambda c: c and "height" in c.lower()
            )
            if height_elem:
                height = height_elem.get_text(strip=True)
                break

            parent = parent.parent

        # Add to results if valid data is found
        if name:
            players_data.append((name, height))

    return players_data

def scrape_single_url(school_name, url, team_type):
    """
    Scrape athlete data from a single URL and save to CSV

    Args:
        school_name: School name
        url: URL to scrape
        team_type: Team type

    Returns:
        Success status
    """
    print(f"Scraping data for {school_name}, URL: {url}")
    html = fetch_html(url, max_retries=5, retry_delay=10)

    if not html:
        print(f"Unable to get data for {school_name}")
        return False

    players = extract_data(html, school_name, url)
    if not players:
        print(f"No athlete data extracted from {school_name}")
        return False

    # Add school name to each player's data
    players_with_school = [(name, height, school_name) for name, height in players]

    # Create DataFrame and save
    df = pd.DataFrame(players_with_school, columns=["Name", "Height", "School"])
    df["Height_Inches"] = df["Height"].apply(parse_height_to_inches)

    # Generate filename
    filename = f"single_{team_type}_{school_name.replace(' ', '_').lower()}.csv"
    df.to_csv(filename, index=False)
    print(f"Successfully saved {school_name} data to {filename}")

    return True

def scrape_team_data(team_type, school_filter=None, delay=2):
    """
    Scrape data for all schools of a specified team type

    Args:
        team_type: Team type ('mens_swimming', 'womens_swimming', 'mens_volleyball', 'womens_volleyball')
        school_filter: If provided, only scrape data for schools matching this name
        delay: Scraping interval (seconds)

    Returns:
        List containing athlete data
    """
    all_data = []

    for school_name, url in DATA_SOURCES[team_type]:
        # If school filter is specified, only process matching schools
        if school_filter and school_filter.lower() not in school_name.lower():
            continue

        print(f"Scraping data for {school_name}...")
        html = fetch_html(url)
        if html:
            players = extract_data(html, school_name, url)

            # Add school name to each player's data
            players_with_school = [
                (name, height, school_name) for name, height in players
            ]
            all_data.extend(players_with_school)

            # Sleep politely to avoid putting too much pressure on servers
            time.sleep(delay)
        else:
            print(f"Failed to get data for {school_name}, skipping")

    return all_data

def create_dataframe(data):
    """Convert scraped data to DataFrame"""
    # Create DataFrame containing name, height, and school
    df = pd.DataFrame(data, columns=["Name", "Height", "School"])

    # Convert height to inches
    df["Height_Inches"] = df["Height"].apply(parse_height_to_inches)

    return df

def save_to_csv(df, filename):
    """Save DataFrame to CSV file"""
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Scrape college athlete height data")

    # Add parameter group to select operation mode
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--all", action="store_true", help="Scrape all data")
    group.add_argument(
        "--team",
        choices=[
            "mens_swimming",
            "womens_swimming",
            "mens_volleyball",
            "womens_volleyball",
        ],
        help="Only scrape data for specified team type",
    )
    group.add_argument(
        "--single", action="store_true", help="Scrape data from a single URL"
    )

    # Parameters needed for single URL scraping
    parser.add_argument("--url", help="Single URL to scrape (use with --single)")
    parser.add_argument("--school", help="School name (use with --single)")
    parser.add_argument(
        "--type",
        choices=[
            "mens_swimming",
            "womens_swimming",
            "mens_volleyball",
            "womens_volleyball",
        ],
        help="Team type for single URL (use with --single)",
    )

    # Team scraping filter parameter
    parser.add_argument("--filter", help="Filter by school name (use with --team)")

    # Other options
    parser.add_argument(
        "--delay", type=int, default=2, help="Scraping interval (seconds)"
    )
    parser.add_argument("--retries", type=int, default=3, help="Maximum retry attempts")

    # In a notebook environment, sys.argv might not contain expected arguments.
    # We can check if we are running in an interactive environment (like Jupyter)
    # and provide empty args to prevent SystemExit.
    if 'ipykernel' in sys.modules:
        args = parser.parse_args([]) # Pass an empty list of args
    else:
        args = parser.parse_args() # Parse command-line args in a script environment

    # If no mode specified, default to scrape all
    if not (args.all or args.team or args.single):
        args.all = True

    return args

def main():
    """Main function"""
    try:
        args = parse_args()

        # Single URL scraping mode
        if args.single:
            if not args.url or not args.school or not args.type:
                print(
                    "When using --single mode, you must provide --url, --school, and --type parameters"
                )
                return

            success = scrape_single_url(args.school, args.url, args.type)
            if success:
                print("Single URL scraping successful")
            else:
                print("Single URL scraping failed")
            return

        # Scrape specific team type
        if args.team:
            print(f"Starting to scrape {args.team} team data...")
            team_data = scrape_team_data(args.team, args.filter, args.delay)
            if team_data:
                team_df = create_dataframe(team_data)
                # Include filter in filename if provided
                filename = f"{args.team}{'_' + args.filter if args.filter else ''}.csv"
                save_to_csv(team_df, filename)
                print(f"{args.team} team data scraping complete")
            else:
                print(f"No {args.team} team data obtained")
            return

        # Scrape all types of data
        if args.all:
            # 1.1 Scrape men's swimming team data
            print("Starting to scrape men's swimming team data...")
            mens_swimming_data = scrape_team_data("mens_swimming", delay=args.delay)
            mens_swimming_df = create_dataframe(mens_swimming_data)
            save_to_csv(mens_swimming_df, "mens_swimming.csv")

            # 1.2 Scrape women's swimming team data
            print("\nStarting to scrape women's swimming team data...")
            womens_swimming_data = scrape_team_data("womens_swimming", delay=args.delay)
            womens_swimming_df = create_dataframe(womens_swimming_data)
            save_to_csv(womens_swimming_df, "womens_swimming.csv")

            # 1.3 Scrape men's volleyball team data
            print("\nStarting to scrape men's volleyball team data...")
            mens_volleyball_data = scrape_team_data("mens_volleyball", delay=args.delay)
            mens_volleyball_df = create_dataframe(mens_volleyball_data)
            save_to_csv(mens_volleyball_df, "mens_volleyball.csv")

            # 1.4 Scrape women's volleyball team data
            print("\nStarting to scrape women's volleyball team data...")
            womens_volleyball_data = scrape_team_data(
                "womens_volleyball", delay=args.delay
            )
            womens_volleyball_df = create_dataframe(womens_volleyball_data)
            save_to_csv(womens_volleyball_df, "womens_volleyball.csv")

            print("\nAll data scraping complete!")
    except Exception as e:
        print(f"An error occurred during program execution: {str(e)}")

if __name__ == "__main__":
    main()

import numpy as np

# Load CSV files
def load_data():
    print("Loading data files...")
    mens_swimming = pd.read_csv("mens_swimming.csv")
    womens_swimming = pd.read_csv("womens_swimming.csv")
    mens_volleyball = pd.read_csv("mens_volleyball.csv")
    womens_volleyball = pd.read_csv("womens_volleyball.csv")

    return mens_swimming, womens_swimming, mens_volleyball, womens_volleyball

# Calculate average heights
def calculate_average_heights(
    mens_swimming, womens_swimming, mens_volleyball, womens_volleyball
):
    print("\nTask 2.1: Calculate average heights for each team")
    print("-" * 50)

    # Calculate average using Height_Inches column, ignoring NaN values
    mens_swimming_avg = mens_swimming["Height_Inches"].mean()
    womens_swimming_avg = womens_swimming["Height_Inches"].mean()
    mens_volleyball_avg = mens_volleyball["Height_Inches"].mean()
    womens_volleyball_avg = womens_volleyball["Height_Inches"].mean()

    # Print average heights (in inches and centimeters)
    print(
        f"Men's Swimming Team Average Height: {mens_swimming_avg:.2f} inches ({(mens_swimming_avg * 2.54):.2f} cm)"
    )
    print(
        f"Women's Swimming Team Average Height: {womens_swimming_avg:.2f} inches ({(womens_swimming_avg * 2.54):.2f} cm)"
    )
    print(
        f"Men's Volleyball Team Average Height: {mens_volleyball_avg:.2f} inches ({(mens_volleyball_avg * 2.54):.2f} cm)"
    )
    print(
        f"Women's Volleyball Team Average Height: {womens_volleyball_avg:.2f} inches ({(womens_volleyball_avg * 2.54):.2f} cm)"
    )

    # Calculate differences between teams
    swimming_diff = mens_swimming_avg - womens_swimming_avg
    volleyball_diff = mens_volleyball_avg - womens_volleyball_avg
    mens_diff = mens_volleyball_avg - mens_swimming_avg
    womens_diff = womens_volleyball_avg - womens_swimming_avg

    print("\nDifference Analysis:")
    print(
        f"Men vs Women Swimming Teams: {swimming_diff:.2f} inches ({(swimming_diff * 2.54):.2f} cm)"
    )
    print(
        f"Men vs Women Volleyball Teams: {volleyball_diff:.2f} inches ({(volleyball_diff * 2.54):.2f} cm)"
    )
    print(
        f"Men's Volleyball vs Men's Swimming: {mens_diff:.2f} inches ({(mens_diff * 2.54):.2f} cm)"
    )
    print(
        f"Women's Volleyball vs Women's Swimming: {womens_diff:.2f} inches ({(womens_diff * 2.54):.2f} cm)"
    )

# Find tallest and shortest athletes
def find_extreme_heights(
    mens_swimming, womens_swimming, mens_volleyball, womens_volleyball
):
    print("\nTask 2.2: Find the 5 tallest and shortest athletes for each team")
    print("-" * 50)

    # Filter out records with NaN heights
    mens_swimming_valid = mens_swimming.dropna(subset=["Height_Inches"])
    womens_swimming_valid = womens_swimming.dropna(subset=["Height_Inches"])
    mens_volleyball_valid = mens_volleyball.dropna(subset=["Height_Inches"])
    womens_volleyball_valid = womens_volleyball.dropna(subset=["Height_Inches"])

    # Men's Swimming Team
    print("\nMen's Swimming Team - Tallest Athletes:")
    tallest_men_swimming = mens_swimming_valid.nlargest(5, "Height_Inches")
    for i, (_, player) in enumerate(tallest_men_swimming.iterrows(), 1):
        print(
            f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
        )

    print("\nMen's Swimming Team - Shortest Athletes:")
    shortest_men_swimming = mens_swimming_valid.nsmallest(5, "Height_Inches")
    for i, (_, player) in enumerate(shortest_men_swimming.iterrows(), 1):
        print(
            f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
        )

    # Men's Volleyball Team
    print("\nMen's Volleyball Team - Tallest Athletes:")
    tallest_men_volleyball = mens_volleyball_valid.nlargest(5, "Height_Inches")
    for i, (_, player) in enumerate(tallest_men_volleyball.iterrows(), 1):
        print(
            f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
        )

    print("\nMen's Volleyball Team - Shortest Athletes:")
    shortest_men_volleyball = mens_volleyball_valid.nsmallest(5, "Height_Inches")
    for i, (_, player) in enumerate(shortest_men_volleyball.iterrows(), 1):
        print(
            f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
        )

    # Women's Swimming Team
    print("\nWomen's Swimming Team - Tallest Athletes:")
    tallest_women_swimming = womens_swimming_valid.nlargest(5, "Height_Inches")
    for i, (_, player) in enumerate(tallest_women_swimming.iterrows(), 1):
        print(
            f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
        )

    print("\nWomen's Swimming Team - Shortest Athletes:")
    shortest_women_swimming = womens_swimming_valid.nsmallest(5, "Height_Inches")
    for i, (_, player) in enumerate(shortest_women_swimming.iterrows(), 1):
        print(
            f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
        )

    # Women's Volleyball Team
    print("\nWomen's Volleyball Team - Tallest Athletes:")
    tallest_women_volleyball = womens_volleyball_valid.nlargest(5, "Height_Inches")
    for i, (_, player) in enumerate(tallest_women_volleyball.iterrows(), 1):
        print(
            f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
        )

    print("\nWomen's Volleyball Team - Shortest Athletes:")
    shortest_women_volleyball = womens_volleyball_valid.nsmallest(5, "Height_Inches")
    for i, (_, player) in enumerate(shortest_women_volleyball.iterrows(), 1):
        print(
            f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
        )

# Check for tie situations (if multiple athletes have the same height)
def check_ties(mens_swimming, womens_swimming, mens_volleyball, womens_volleyball):
    print("\nChecking for height tie situations")
    print("-" * 50)

    # Filter out records with NaN heights
    mens_swimming_valid = mens_swimming.dropna(subset=["Height_Inches"])
    womens_swimming_valid = womens_swimming.dropna(subset=["Height_Inches"])
    mens_volleyball_valid = mens_volleyball.dropna(subset=["Height_Inches"])
    womens_volleyball_valid = womens_volleyball.dropna(subset=["Height_Inches"])

    # Get the heights of the top 5 and bottom 5
    tallest_men_swimming_heights = mens_swimming_valid.nlargest(5, "Height_Inches")[
        "Height_Inches"
    ].values
    shortest_men_swimming_heights = mens_swimming_valid.nsmallest(5, "Height_Inches")[
        "Height_Inches"
    ].values

    tallest_men_volleyball_heights = mens_volleyball_valid.nlargest(5, "Height_Inches")[
        "Height_Inches"
    ].values
    shortest_men_volleyball_heights = mens_volleyball_valid.nsmallest(
        5, "Height_Inches"
    )["Height_Inches"].values

    tallest_women_swimming_heights = womens_swimming_valid.nlargest(5, "Height_Inches")[
        "Height_Inches"
    ].values
    shortest_women_swimming_heights = womens_swimming_valid.nsmallest(
        5, "Height_Inches"
    )["Height_Inches"].values

    tallest_women_volleyball_heights = womens_volleyball_valid.nlargest(
        5, "Height_Inches"
    )["Height_Inches"].values
    shortest_women_volleyball_heights = womens_volleyball_valid.nsmallest(
        5, "Height_Inches"
    )["Height_Inches"].values

    # Check if other athletes are tied with the top 5 or bottom 5
    # Men's Swimming Team
    if (
        len(
            mens_swimming_valid[
                mens_swimming_valid["Height_Inches"] >= tallest_men_swimming_heights[-1]
            ]
        )
        > 5
    ):
        print("\nMen's Swimming Team has height ties (tallest):")
        tied_players = mens_swimming_valid[
            mens_swimming_valid["Height_Inches"] >= tallest_men_swimming_heights[-1]
        ]
        print(
            f"Total of {len(tied_players)} athletes with height greater than or equal to {tallest_men_swimming_heights[-1]} inches"
        )
        print("These athletes are:")
        for i, (_, player) in enumerate(tied_players.iterrows(), 1):
            print(
                f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
            )

    if (
        len(
            mens_swimming_valid[
                mens_swimming_valid["Height_Inches"]
                <= shortest_men_swimming_heights[-1]
            ]
        )
        > 5
    ):
        print("\nMen's Swimming Team has height ties (shortest):")
        tied_players = mens_swimming_valid[
            mens_swimming_valid["Height_Inches"] <= shortest_men_swimming_heights[-1]
        ]
        print(
            f"Total of {len(tied_players)} athletes with height less than or equal to {shortest_men_swimming_heights[-1]} inches"
        )
        print("These athletes are:")
        for i, (_, player) in enumerate(tied_players.iterrows(), 1):
            print(
                f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
            )

    # Men's Volleyball Team
    if (
        len(
            mens_volleyball_valid[
                mens_volleyball_valid["Height_Inches"]
                >= tallest_men_volleyball_heights[-1]
            ]
        )
        > 5
    ):
        print("\nMen's Volleyball Team has height ties (tallest):")
        tied_players = mens_volleyball_valid[
            mens_volleyball_valid["Height_Inches"] >= tallest_men_volleyball_heights[-1]
        ]
        print(
            f"Total of {len(tied_players)} athletes with height greater than or equal to {tallest_men_volleyball_heights[-1]} inches"
        )
        print("These athletes are:")
        for i, (_, player) in enumerate(tied_players.iterrows(), 1):
            print(
                f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
            )

    if (
        len(
            mens_volleyball_valid[
                mens_volleyball_valid["Height_Inches"]
                <= shortest_men_volleyball_heights[-1]
            ]
        )
        > 5
    ):
        print("\nMen's Volleyball Team has height ties (shortest):")
        tied_players = mens_volleyball_valid[
            mens_volleyball_valid["Height_Inches"]
            <= shortest_men_volleyball_heights[-1]
        ]
        print(
            f"Total of {len(tied_players)} athletes with height less than or equal to {shortest_men_volleyball_heights[-1]} inches"
        )
        print("These athletes are:")
        for i, (_, player) in enumerate(tied_players.iterrows(), 1):
            print(
                f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
            )

    # Women's Swimming Team
    if (
        len(
            womens_swimming_valid[
                womens_swimming_valid["Height_Inches"]
                >= tallest_women_swimming_heights[-1]
            ]
        )
        > 5
    ):
        print("\nWomen's Swimming Team has height ties (tallest):")
        tied_players = womens_swimming_valid[
            womens_swimming_valid["Height_Inches"] >= tallest_women_swimming_heights[-1]
        ]
        print(
            f"Total of {len(tied_players)} athletes with height greater than or equal to {tallest_women_swimming_heights[-1]} inches"
        )
        print("These athletes are:")
        for i, (_, player) in enumerate(tied_players.iterrows(), 1):
            print(
                f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
            )

    if (
        len(
            womens_swimming_valid[
                womens_swimming_valid["Height_Inches"]
                <= shortest_women_swimming_heights[-1]
            ]
        )
        > 5
    ):
        print("\nWomen's Swimming Team has height ties (shortest):")
        tied_players = womens_swimming_valid[
            womens_swimming_valid["Height_Inches"]
            <= shortest_women_swimming_heights[-1]
        ]
        print(
            f"Total of {len(tied_players)} athletes with height less than or equal to {shortest_women_swimming_heights[-1]} inches"
        )
        print("These athletes are:")
        for i, (_, player) in enumerate(tied_players.iterrows(), 1):
            print(
                f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
            )

    # Women's Volleyball Team
    if (
        len(
            womens_volleyball_valid[
                womens_volleyball_valid["Height_Inches"]
                >= tallest_women_volleyball_heights[-1]
            ]
        )
        > 5
    ):
        print("\nWomen's Volleyball Team has height ties (tallest):")
        tied_players = womens_volleyball_valid[
            womens_volleyball_valid["Height_Inches"]
            >= tallest_women_volleyball_heights[-1]
        ]
        print(
            f"Total of {len(tied_players)} athletes with height greater than or equal to {tallest_women_volleyball_heights[-1]} inches"
        )
        print("These athletes are:")
        for i, (_, player) in enumerate(tied_players.iterrows(), 1):
            print(
                f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
            )

    if (
        len(
            womens_volleyball_valid[
                womens_volleyball_valid["Height_Inches"]
                <= shortest_women_volleyball_heights[-1]
            ]
        )
        > 5
    ):
        print("\nWomen's Volleyball Team has height ties (shortest):")
        tied_players = womens_volleyball_valid[
            womens_volleyball_valid["Height_Inches"]
            <= shortest_women_volleyball_heights[-1]
        ]
        print(
            f"Total of {len(tied_players)} athletes with height less than or equal to {shortest_women_volleyball_heights[-1]} inches"
        )
        print("These athletes are:")
        for i, (_, player) in enumerate(tied_players.iterrows(), 1):
            print(
                f"{i}. {player['Name']} ({player['School']}): {player['Height']} ({player['Height_Inches']} inches)"
            )

# Main function
def main():
    try:
        # Load data
        mens_swimming, womens_swimming, mens_volleyball, womens_volleyball = load_data()

        # Display basic dataset information
        print("\nDataset Information:")
        print(f"Men's Swimming Team: {len(mens_swimming)} athletes")
        print(f"Women's Swimming Team: {len(womens_swimming)} athletes")
        print(f"Men's Volleyball Team: {len(mens_volleyball)} athletes")
        print(f"Women's Volleyball Team: {len(womens_volleyball)} athletes")

        # Calculate average heights
        calculate_average_heights(
            mens_swimming, womens_swimming, mens_volleyball, womens_volleyball
        )

        # Find tallest and shortest athletes
        find_extreme_heights(
            mens_swimming, womens_swimming, mens_volleyball, womens_volleyball
        )

        # Check for tie situations
        check_ties(mens_swimming, womens_swimming, mens_volleyball, womens_volleyball)

        print("\nAnalysis complete!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

def load_data():
    """Load CSV files and return dataframes"""
    print("Loading data files...")
    mens_swimming = pd.read_csv("mens_swimming.csv")
    womens_swimming = pd.read_csv("womens_swimming.csv")
    mens_volleyball = pd.read_csv("mens_volleyball.csv")
    womens_volleyball = pd.read_csv("womens_volleyball.csv")

    return mens_swimming, womens_swimming, mens_volleyball, womens_volleyball


def calculate_average_heights(
    mens_swimming, womens_swimming, mens_volleyball, womens_volleyball
):
    """Calculate average heights for each team"""
    # Calculate average using Height_Inches column, ignoring NaN values
    mens_swimming_avg = mens_swimming["Height_Inches"].mean()
    womens_swimming_avg = womens_swimming["Height_Inches"].mean()
    mens_volleyball_avg = mens_volleyball["Height_Inches"].mean()
    womens_volleyball_avg = womens_volleyball["Height_Inches"].mean()

    return (
        mens_swimming_avg,
        womens_swimming_avg,
        mens_volleyball_avg,
        womens_volleyball_avg,
    )


def create_height_bar_chart(
    mens_swimming_avg, womens_swimming_avg, mens_volleyball_avg, womens_volleyball_avg
):
    """Create a bar chart comparing average heights and save it to a file"""
    # Data preparation
    team_categories = [
        "Men's Swimming",
        "Women's Swimming",
        "Men's Volleyball",
        "Women's Volleyball",
    ]
    heights_in_inches = [
        mens_swimming_avg,
        womens_swimming_avg,
        mens_volleyball_avg,
        womens_volleyball_avg,
    ]
    heights_in_cm = [h * 2.54 for h in heights_in_inches]  # Convert inches to cm

    # Set up the figure with a specific size
    plt.figure(figsize=(10, 6))

    # Set up bar positions
    x = np.arange(len(team_categories))
    width = 0.35

    # Create bars
    plt.bar(
        x - width / 2,
        heights_in_inches,
        width,
        label="Height (inches)",
        color="royalblue",
    )
    plt.bar(
        x + width / 2, heights_in_cm, width, label="Height (cm)", color="lightcoral"
    )

    # Add labels, title and legend
    plt.xlabel("Team Categories")
    plt.ylabel("Average Height")
    plt.title("Average Height Comparison: Swimming vs. Volleyball Athletes")
    plt.xticks(x, team_categories, rotation=45)
    plt.legend()

    # Add value labels on top of each bar
    for i, v in enumerate(heights_in_inches):
        plt.text(i - width / 2, v + 0.5, f'{v:.2f}"', ha="center", fontsize=9)

    for i, v in enumerate(heights_in_cm):
        plt.text(i + width / 2, v + 0.5, f"{v:.2f} cm", ha="center", fontsize=9)

    # Adjust layout to make room for labels
    plt.tight_layout()

    # Save the figure
    plt.savefig("height_comparison_chart.png", dpi=300)
    plt.savefig("height_comparison_chart.jpg", dpi=300)

    print(
        "Chart saved as 'height_comparison_chart.png' and 'height_comparison_chart.jpg'"
    )

    # Show the plot (optional - comment out if running in a non-interactive environment)
    plt.show()


def main():
    try:
        # Load data
        mens_swimming, womens_swimming, mens_volleyball, womens_volleyball = load_data()

        # Calculate average heights
        (
            mens_swimming_avg,
            womens_swimming_avg,
            mens_volleyball_avg,
            womens_volleyball_avg,
        ) = calculate_average_heights(
            mens_swimming, womens_swimming, mens_volleyball, womens_volleyball
        )

        # Display average heights
        print("\nAverage Heights:")
        print(
            f"Men's Swimming Team: {mens_swimming_avg:.2f} inches ({mens_swimming_avg * 2.54:.2f} cm)"
        )
        print(
            f"Women's Swimming Team: {womens_swimming_avg:.2f} inches ({womens_swimming_avg * 2.54:.2f} cm)"
        )
        print(
            f"Men's Volleyball Team: {mens_volleyball_avg:.2f} inches ({mens_volleyball_avg * 2.54:.2f} cm)"
        )
        print(
            f"Women's Volleyball Team: {womens_volleyball_avg:.2f} inches ({womens_volleyball_avg * 2.54:.2f} cm)"
        )

        # Create and save the chart
        create_height_bar_chart(
            mens_swimming_avg,
            womens_swimming_avg,
            mens_volleyball_avg,
            womens_volleyball_avg,
        )

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
