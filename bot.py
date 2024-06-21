import requests
import time
from datetime import datetime
import json
import sys
import os
from colorama import *

init(autoreset=True)

red = Fore.LIGHTRED_EX
green = Fore.LIGHTGREEN_EX
yellow = Fore.LIGHTYELLOW_EX
blue = Fore.LIGHTBLUE_EX
black = Fore.LIGHTBLACK_EX
reset = Style.RESET_ALL
white = Fore.LIGHTWHITE_EX

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the full paths to the files
data_file = os.path.join(script_dir, "data.txt")
config_file = os.path.join(script_dir, "config.json")


# Clear the terminal
def clear_terminal():
    # For Windows
    if os.name == "nt":
        _ = os.system("cls")
    # For macOS and Linux
    else:
        _ = os.system("clear")


def get_user_info(headers):
    # Login and get user information
    user_response = requests.get(
        "https://api-clicker.pixelverse.xyz/api/users", headers=headers
    )
    if user_response.status_code == 200:
        user_data = user_response.json()
        telegram_user = user_data.get("telegramUserId")
        claim_count = user_data.get("clicksCount", 0)
        if telegram_user:
            print(f"{green}Get info successful!")
        else:
            print(f"{yellow}Telegram User ID not found.")
        return claim_count
    else:
        print(f"{red}Login failed. Status code:", user_response.status_code)
        return None


def claim(headers):
    claim_response = requests.post(
        "https://api-clicker.pixelverse.xyz/api/mining/claim",
        headers=headers,
    )
    if claim_response.status_code == 201:
        claim_data = claim_response.json()
        claimed_amount = claim_data.get("claimedAmount", 0)
        print(f"{green}Claimed Amount:", str(claimed_amount))
        return claimed_amount
    else:
        print(f"{red}Claim failed!")
        return None


def fetch_pet_info(headers):
    try:
        pet_response = requests.get(
            "https://api-clicker.pixelverse.xyz/api/pets", headers=headers
        )
        if pet_response.status_code == 200:
            pet_data = pet_response.json()
            pets = pet_data.get("data", [])
            for pet in pets:
                name = pet.get("name")
                user_pet = pet.get("userPet", {})
                level = user_pet.get("level")
                stats = user_pet.get("stats", [])

                # Initialize default values
                max_energy = power = recharge_speed = None

                # Extract specific stats
                for stat in stats:
                    stat_name = stat.get("petsStat", {}).get("name")
                    current_value = stat.get("currentValue")
                    if stat_name == "Max energy":
                        max_energy = current_value
                    elif stat_name == "Damage":
                        power = current_value
                    elif stat_name == "Energy restoration":
                        recharge_speed = current_value

                print(
                    f"{yellow}Pet information: {white}[Name: {name}, Level: {level}, Max energy: {max_energy}, Power: {power}, Recharge speed: {recharge_speed}]"
                )
            return pets  # Return the pet data for further processing
        else:
            print(
                f"{red}Failed to fetch pet information. Status code:",
                pet_response.status_code,
            )
    except Exception as e:
        print(f"{red}Error fetching pet information:", e)
    return []


def upgrade_pet(headers, pet):
    try:
        user_pet = pet.get("userPet", {})
        pet_id = user_pet.get("id")

        upgrade_response = requests.post(
            f"https://api-clicker.pixelverse.xyz/api/pets/user-pets/{pet_id}/level-up",
            headers=headers,
        )
        if upgrade_response.status_code == 201:
            print(f"{green}Pet with ID {pet_id} upgraded successfully.")
            # Fetch and display the updated pet information
            fetch_pet_info(headers)
        else:
            print(
                f"{red}Failed to upgrade pet with ID {pet_id}. Status code:",
                upgrade_response.status_code,
            )
    except Exception as e:
        print(f"{red}Error upgrading pet with ID {pet_id}:", e)


def main():
    clear_terminal()
    banner = f"""

    {blue}Smart Airdrop {white}PixelTap Auto Claimer
    t.me/smartairdrop2120

    """
    print(banner)
    initdatas = open(data_file, "r").read().splitlines()
    auto_upgrade = json.loads(open(config_file, "r").read())["auto_upgrade"]
    while True:
        for no, initdata in enumerate(initdatas):
            line = "~" * 50
            print(line)
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"[{now}]--- Account number:", no + 1, "---")

            # Headers
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Cache-Control": "no-cache",
                "Initdata": initdata,
                "Origin": "https://sexyzbot.pxlvrs.io",
                "Pragma": "no-cache",
                "Referer": "https://sexyzbot.pxlvrs.io/",
                "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                "Sec-Fetch-Site": "cross-site",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            }

            try:
                # Get user info
                claim_count = get_user_info(headers)
                print(f"{green}Balance:", claim_count)

                # Fetch and display pet information after login
                pets = fetch_pet_info(headers)

                # Start claim
                claimed_amount = claim(headers)

                if claimed_amount:
                    # Get user info
                    claim_count = get_user_info(headers)
                    print(f"{green}New balance:", claim_count)

                if auto_upgrade == "true":
                    print(f"{yellow}Auto-upgrading pets...")
                    try:
                        for pet in pets:
                            upgrade_pet(headers, pet)

                        # Re-fetch pet information after upgrades
                        pets = fetch_pet_info(headers)
                    except:
                        print(f"{red}Upgrade failed")

            except Exception as e:
                print("Error:", e)

        print()
        print(f"{yellow}Wait for 5 minutes")
        time.sleep(300)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
