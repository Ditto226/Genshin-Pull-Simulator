import random
import json
import os
# from zipfile import Path

standard_pools = os.path.join("Data", "standard_pools.json")
banner = os.path.join("Data", "banner.json")

# standard_pools = 'Data\\standard_pools.json'
# banner = 'Data\\banner.json'

with open(standard_pools, 'r') as f:
    standard_pools_data = json.load(f)
with open(banner, 'r') as f:
    banner_data = json.load(f)

# featured_5_star = banner_data["6.1.1.1"]['4star']
# print(featured_5_star)

def simulate_wish(num_wishes, user_state):
    pity_5, pity_4 = user_state.get('pity_5', 0) , user_state.get('pity_4', 0)
    guaranteed_5, guaranteed_4 = user_state.get('guaranteed_5', False), user_state.get('guaranteed_4', False)
    cr_count = user_state.get('cr_count', 1)
    banner = user_state.get('banner_version', list(banner_data.keys())[-1])  
    CR_TRIGGER_RATES = [0.0, 0.0, 0.09091, 1.0]
    results = []

    standard_5_stars = standard_pools_data['5star']
    standard_4_stars = standard_pools_data['4star']
    standard_3_stars = standard_pools_data['3star']
    featured_5_star = banner_data[banner]['5star']
    featured_4_star = banner_data[banner]['4star']
    non_featured_5_stars = [char for char in standard_5_stars if char not in featured_5_star]
    non_featured_4_stars = [char for char in standard_4_stars if char not in featured_4_star]

    for _ in range(num_wishes):
        pity_5 += 1
        pity_4 += 1
        rate_5 = 0.006 + max(0, (pity_5 - 73)) * 0.06
        rate_4 = 0.051 + max(0, (pity_4 - 8)) * 0.51
        
        r = random.random()
        # 5-STAR LOGIC
        if r < rate_5:
            if guaranteed_5:
                # character = random.choice(featured_5_star)
                pull_entry = {
                    "name": featured_5_star,
                    "rarity": 5,
                    "status": "G" ,
                    "pity": pity_5,
                }
                results.append(pull_entry)
                # pull_counts["5star"]["total_featured"] += 1 
                guaranteed_5 = False
            elif random.random() < CR_TRIGGER_RATES[min(cr_count, 3)]:   
                    # character = random.choice(featured_5_star)
                    pull_entry = {
                        "name": featured_5_star,
                        "rarity": 5,
                        "status": "CR",
                        "pity": pity_5,
                    }
                    results.append(pull_entry)
                    # pull_counts["5star"]["total_featured"] += 1 
                    cr_count = 1
            elif random.random() < 0.5 :
                # character = random.choice(featured_5_star)
                pull_entry = {
                    "name": featured_5_star,
                    "rarity": 5,
                    "status": "W", 
                    "pity": pity_5,
                }
                results.append(pull_entry)
                # pull_counts["5star"]["total_featured"] += 1
                cr_count = max(0, cr_count - 1)
            else:
                # Standard Loss
                character = random.choice(non_featured_5_stars)
                pull_entry = {
                    "name": character,
                    "rarity": 5,
                    "status": "L",
                    "pity": pity_5
                }
                results.append(pull_entry)
                # pull_counts["5star"]["total_nonfeatured"] += 1
                guaranteed_5 = True
                cr_count = min(3, cr_count + 1)
            pity_5 = 0

        # 4-STAR LOGIC
        elif r < (rate_5 + rate_4):
            if guaranteed_4:
                character = random.choice(featured_4_star)
                pull_entry = {
                    "name": character,
                    "rarity": 4,
                    "status": "G",
                    "pity": pity_4
                }
                results.append(pull_entry)
                # pull_counts["4star"]["total_featured"] += 1
                guaranteed_4 = False 
            elif random.random() < 0.5:
                character = random.choice(featured_4_star)
                pull_entry = {
                    "name": character,
                    "rarity": 4,
                    "status": "W",
                    "pity": pity_4
                }
                results.append(pull_entry)
                # pull_counts["4star"]["total_featured"] += 1
            else:    
                character = random.choice(non_featured_4_stars)
                pull_entry = {
                    "name": character,
                    "rarity": 4,
                    "status": "L",
                    "pity": pity_4
                }
                results.append(pull_entry)
                #  pull_counts["4star"]["total_nonfeatured"] += 1
                guaranteed_4 = True 
            pity_4 = 0  

        else:
            character = random.choice(standard_3_stars)
            pull_entry = {
                "name": character,
                "rarity": 3,
                "status": None,
                "pity": None
            }
            results.append(pull_entry)
            # pull_counts["3star"]["total"] += 1

    # user_state.setdefault('items', []).extend(results)
    user_state['items'] = results
    user_state['pulls'] += num_wishes
    user_state['pity_5'] = pity_5
    user_state['pity_4'] = pity_4
    user_state['guaranteed_5'] = guaranteed_5
    user_state['guaranteed_4'] = guaranteed_4
    user_state['cr_count'] = cr_count
    # return results, pity_5, pity_4, guaranteed_5, guaranteed_4, cr_count
    return user_state

# results, pity_5, pity_4, guaranteed_5, guaranteed_4, cr_count = simulate_wish("6.1.1.1", 10, 75, 0, False, False, 1)
# print(f"Results: {results}")