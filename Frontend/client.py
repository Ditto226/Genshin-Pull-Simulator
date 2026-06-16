import requests

SERVER_URL = "http://127.0.0.1:8000"

def send_request(method, endpoint, client_username=None, data=None, params = None):
    url = f"{SERVER_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    # if client_username:
    #     headers["X-User"] = client_username

    try:
        if method.upper() == "GET": response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST": response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT": response = requests.put(url, headers=headers, json=data)
        elif method.upper() == "PATCH": response = requests.patch(url, headers=headers, json=data)
        else: raise ValueError(f"Unsupported HTTP method: {method}")

        if response.status_code == 404:
            return None  
        
        if response.status_code == 400:
            print(f"\n[-] Error: {response.json().get('detail', 'Bad Request')}")
            return None
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as req_err:
        print(f"Network error occurred: {req_err}")
        return None

def custom_setting():
    print(f"Do you want to customise your setting? (y/n)")
    if input().lower() != 'y':
        return {}
    else:
        print(f"Press Enter to set to default value")
        while True:
            pity_5 = input("Pity 5 (0-89): ").strip()
            if pity_5 == "":
                pity_5 = 0
                break
            elif 0 <= int(pity_5) <= 89:
                break  
            print("[-] Input out of bounds. Try again.")
                
        while True:
            pity_4 = input("Pity 4 (0-9): ").strip()
            if pity_4 == "":
                pity_4 = 0
                break
            elif 0 <= int(pity_4) <= 9:
                break
            print("[-] Input out of bounds. Try again.")
                
        while True:
            g5_input = input("Guaranteed 5? (y/n): ").strip().lower()
            if g5_input in ['y', 'n', ""]:
                guaranteed_5 = (g5_input == 'y')  # Converts to True or False
                break
            print("[-] Invalid input. Please enter 'y' or 'n'.")
            
        while True:
            g4_input = input("Guaranteed 4? (y/n): ").strip().lower()
            if g4_input in ['y', 'n', '']:
                guaranteed_4 = (g4_input == 'y')
                break
            print("[-] Invalid input. Please enter 'y' or 'n'.")
            
        while True:
            cr_count = input("CR Count (0-3): ").strip()
            if cr_count == "":
                cr_count = 1
                break
            elif 0 <= int(cr_count) <= 3:
                break
            print("[-] Input out of bounds. Try again.")

        return {
            "pity_5": pity_5, "pity_4": pity_4, 
            "guaranteed_5": guaranteed_5, "guaranteed_4": guaranteed_4, 
            "cr_count": cr_count
        }


def handle_change_banner(username):
    result = send_request("GET", "/banner")
    if result is None: return None
    
    banner_names = list(result['banner'].keys())
    print("\n--- Available Banners ---")
    for idx, name in enumerate(banner_names, 1):
        banner_info = result['banner'][name]
        print(f"{idx}. {name} ({banner_info['5star']}) ({', '.join(banner_info['4star'])})")

    choice = input("\nSelect a banner number (or 'q' to quit): ").strip()
    if choice.lower() == 'q' or not choice.isdigit():
        return None

    idx = int(choice) - 1
    if 0 <= idx < len(banner_names):
        selected_banner = banner_names[idx]
        result2 = send_request("PATCH", f"/user/{username}/data", data={"banner_version": selected_banner})
        if result2 is not None:
            print(f"[*] Success! Active banner is now: {selected_banner}")
            return selected_banner, result2.get('featured', '')
    else:
        print("Selection out of range.")
    return None

def handle_pulls(username, choice):
    if choice == '1': num_pulls = 1
    elif choice == '2': num_pulls = 10
    else:
        try:
            num_pulls = int(input("How many times would you like to pull?\n > ").strip())
            if num_pulls <= 0: return None
        except ValueError:
            print("Please enter a valid integer.")
            return None

    result = send_request("POST", f"/user/{username}/pull", data={"frequency": num_pulls})
    if result is not None:
        new_items = result.get('newly_pulled', [])
        for item in new_items:
            print(f"Pulled {item['rarity']}* {item['name']}")

        return result.get('data', {}), new_items
    return None

def view_items(username):
    print("Press Enter to view all items, or type 'y' to filter results:")
    params = {}
    if input().strip().lower() == "y":
        while True:
            rarity = input("Rarity (3,4,5) : (Enter to skip) ").strip()
            if rarity == '':
                break
            elif int(rarity) in [3, 4, 5]:
                params["rarity"] = rarity
                break  
            print("[-] Input out of bounds. Try again.")

        while True:
            status = input("Status (G/W/L/CR): (Enter to skip) ").strip().upper()
            if status == '':
                break
            elif status in ['G', 'W', 'L', 'CR']:
                params["status"] = status
                break  
            print("[-] Input out of bounds. Try again.")
        
        while True:
            pity = input("Pity: (Enter to skip) ").strip()
            if pity == '':
                break
            elif pity.isdigit() and 1 <= int(pity) <= 89:
                params["pity"] = int(pity)
                break
            print("[-] Input out of bounds. Try again.")
                
        print("")
        
    result = send_request("GET", f"/user/{username}/items", params = params)
    if result is not None:
        items = result.get('items', [])
        if not items:
            print("No items found, try pulling more!")

        for idx, item in enumerate(items, 1):
            status_str = f"{item['status']}" if item.get('status') else ""
            pity_str = f"{item['pity']}" if item.get('pity') else ""
            print(f"{idx}. {item['rarity']}* {item['name']} {status_str}{pity_str}")

def handle_simulate_distribution(username):
    try:
        num_pulls = int(input("How many pulls you like to test?  > ").strip())
        if num_pulls <= 0: return None
    except ValueError:
        print("Please enter a valid integer.")
        return None
    
    print("Simulating pull distribution, this may take a while (10k simulations)...")
    result = send_request("GET", f"/user/{username}/distribution", params={"frequency": num_pulls})
    if result is not None:
        prob5 = result.get('5star_distribution', {})
        expected_value5 = result.get('5star_expected_value', 0)
        print("\n--- Featured 5★ Distribution ---\n")
        print(f"Expected Copies: {expected_value5:.2f}\n")
        print(f"{'Copies':<8} | {'Probability':<12}")
        print("-" * 25)

        sorted_prob5 = sorted(prob5.items(), key=lambda x: int(x[0]))
        for count, prob in sorted_prob5:
            if prob > 0.001:
                # bar_length = int(prob * 50)
                # bar = "█" * bar_length                
                print(f"{count:<8} | {prob:<12.2%}")
        
        prob4 = result.get('4star_distribution', {})
        expected_value4 = result.get('4star_expected_value', 0)
        print("\n\n--- Individual Featured 4★ Distribution ---\n")
        print(f"Expected Copies : {expected_value4:.2f}\n")
        print(f"{'Copies':<8} | {'Probability':<12}")
        print("-" * 25)

        sorted_prob4 = sorted(prob4.items(), key=lambda x: int(x[0]))
        for count, prob in sorted_prob4:
            if prob > 0.001:
                # bar_length = int(prob * 50)
                # bar = "█" * bar_length                
                print(f"{count:<8} | {prob:<12.2%}")

def view_stats(username):
    result = send_request("GET", f"/user/{username}/stats")
    if result is not None:
        total_pulls = result['5star']['total'] + result['4star']['total'] + result['3star']['total']
        print(f"\nTotal Pulls: {total_pulls}")
        print(f"\n5* | Total: {result['5star']['total']}  W: {result['5star']['W']}  L: {result['5star']['L']}  G: {result['5star']['G']}  CR: {result['5star']['CR']} | Average Pity: {result['5star']['average_pity']:.2f} | Win Rate: {result['5star']['win_rate']:.2f}%")
        for name, count in result['5star']['distribution'].items(): print(f"     {name}: {count}")
        print(f"\n4* | Total: {result['4star']['total']}  W: {result['4star']['W']}  L: {result['4star']['L']}  G: {result['4star']['G']} | Average Pity: {result['4star']['average_pity']:.2f} | Win Rate: {result['4star']['win_rate']:.2f}%")
        for name, count in result['4star']['distribution'].items(): print(f"     {name}: {count}")
        print(f"\n3* | Total: {result['3star']['total']}")

def handle_reset(username):
    print("Are you sure you want to reset your account? This cannot be undone! (y/n)")
    if input().lower() != 'y':
        return None
    payload = custom_setting()
    result = send_request("PUT", f"/user/{username}/data", data=payload)
    if result is not None:
        print("Account reset successfully!")
        # return {"data": result.get('user_data', {})}
        return result.get('user_data', {}), result.get('featured', {})
    return None

# --- CORE GAME LOOP CONTROL ---
def game_loop(username):
    """Manages the logged-in gameplay state. Returns True to exit game entirely, False to Logout."""

    while True:

        user_state = send_request("GET", f"/user/{username}/data")
        if user_state is None:
            print("Could not load user data from the server.")
            return False # Boot back to login screen
        user_data = user_state.get('data', {}) 
        featured_info = user_state.get('featured', '') 

        print(f"\n")
        print("-"*104)
        print(f"Username: {username} | Banner Selected: {user_data.get('banner_version', '')} {featured_info}")
        print(f"Pity 5: {user_data.get('pity_5', 0)} | Pity 4: {user_data.get('pity_4', 0)} | "
              f"Guaranteed 5: {user_data.get('guaranteed_5', False)} | Guaranteed 4: {user_data.get('guaranteed_4', False)} | "
              f"CR Count: {user_data.get('cr_count', 1)}")
        print("-"*104)
        
        choice = input("\nPlease enter one of the following:\n"
                       "0 : change banner\n"
                       "1 : pull 1 time\n"
                       "2 : pull 10 times\n"
                       "3 : pull a custom number of times\n"
                       "4 : view pulled items\n"
                       "5 : view stats\n"
                       "6 : simulate pull distribution\n"
                       "7 : reset account\n"
                       "8 : logout account\n"
                       "Any other key to exit\n\n > ").strip()
        
        if choice == '0':
            handle_change_banner(username)
        elif choice in ('1', '2', '3'):
            handle_pulls(username, choice)
        elif choice == '4':
            view_items(username)
        elif choice == '5':
            view_stats(username)
        elif choice == '6':
            handle_simulate_distribution(username)
        elif choice == '7':
            handle_reset(username)
        elif choice == '8':
            print(f"Logging out of '{username}'...")
            return False  # Tells the outer wrapper: "Go back to login loop"
        else:
            print("Exiting application...")
            return True  # Tells the outer wrapper: "Kill the program entirely"

def login():
    print("--- Welcome to Simulator Impact ---")
    while True:
        username = input("Enter username (or 0 to exit): ").strip()
        if not username: continue
        elif username == '0': break

        data = send_request("GET", f"/user/{username}")

        if data is None:
            print(f"User '{username}' not found. Create account? (y/n)")
            if input().lower() == 'y':
                payload = custom_setting()
                result = send_request("POST", f"/user/{username}/data", data=payload)
                if result is None:  
                    print("Creation failed.")
                else:
                    print("Account created successfully!")
            else:
                continue

        # print(f"Welcome back, {username}!")

        should_exit_program = game_loop(username)
        if should_exit_program:
            break 

if __name__ == "__main__":
    login()