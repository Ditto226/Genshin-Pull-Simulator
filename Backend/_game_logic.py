import random
import json
import os
import copy
from typing import Any

standard_pools = os.path.join("Assets", "standard_pools.json")
banner = os.path.join("Assets", "banner.json")

with open(standard_pools, 'r') as f:
    standard_pools_data = json.load(f)
with open(banner, 'r') as f:
    banner_data = json.load(f)

def simulate_wish(num_wishes, user_state, lightweight = False):

    pity_5, pity_4 = user_state.get('pity_5', 0) , user_state.get('pity_4', 0)
    guaranteed_5, guaranteed_4 = user_state.get('guaranteed_5', False), user_state.get('guaranteed_4', False)
    cr_count = user_state.get('cr_count', 1)
    banner = user_state.get('banner_version', list(banner_data.keys())[-1])  
    CR_TRIGGER_RATES = [0.0, 0.0, 0.09091, 1.0]
    
    results = []
    featured_5_count = 0
    featured_4_count = 0
    featured_5_star = []
    featured_4_star = []
    non_featured_5_stars = []
    non_featured_4_stars = []
    standard_3_stars = []

    if not lightweight:
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
            # guaranteed
            if guaranteed_5:
                if lightweight:
                    featured_5_count += 1
                else:
                    results.append({"name": featured_5_star, "rarity": 5, "status": "G", "pity": pity_5})               
                guaranteed_5 = False
            # trigger CR
            elif random.random() < CR_TRIGGER_RATES[min(cr_count, 3)]:   
                if lightweight:
                    featured_5_count += 1
                else:
                    results.append({"name": featured_5_star, "rarity": 5, "status": "CR", "pity": pity_5}) 
                guaranteed_5 = False
                cr_count = 1
            # win 5050
            elif random.random() < 0.5 :
                if lightweight:
                    featured_5_count += 1
                else:
                    results.append({"name": featured_5_star, "rarity": 5, "status": "W", "pity": pity_5}) 
                cr_count = max(0, cr_count - 1)
            # loss 5050
            else:
                if not lightweight:
                    character = random.choice(non_featured_5_stars)
                    results.append({"name": character, "rarity": 5, "status": "L", "pity": pity_5}) 
                guaranteed_5 = True
                cr_count = min(3, cr_count + 1)
            pity_5 = 0

        # 4-STAR LOGIC
        elif r < (rate_5 + rate_4):
            # guaranteed
            if guaranteed_4:
                if lightweight:
                    # Roll 1/3 chance for the specific target 4-star
                    if random.randint(1, 3) == 1:
                        featured_4_count += 1
                else:
                    character = random.choice(featured_4_star)
                    results.append({"name": character, "rarity": 4, "status": "G", "pity": pity_4})
                guaranteed_4 = False 
            # win 5050
            elif random.random() < 0.5:
                if lightweight:
                    if random.randint(1, 3) == 1:
                        featured_4_count += 1
                else:
                    character = random.choice(featured_4_star)
                    results.append({"name": character, "rarity": 4, "status": "W", "pity": pity_4})
            # loss 5050
            else:    
                if not lightweight:
                    character = random.choice(non_featured_4_stars)
                    results.append({"name": character, "rarity": 4, "status": "L", "pity": pity_4})
                guaranteed_4 = True 
            pity_4 = 0  

        else:
            if not lightweight:
                character = random.choice(standard_3_stars)
                results.append({"name": character, "rarity": 3, "status": None, "pity": None})

    user_state['items'] = results
    user_state['pulls'] += num_wishes
    user_state['pity_5'] = pity_5
    user_state['pity_4'] = pity_4
    user_state['guaranteed_5'] = guaranteed_5
    user_state['guaranteed_4'] = guaranteed_4
    user_state['cr_count'] = cr_count

    if lightweight:
        return user_state, featured_5_count, featured_4_count
    else:
        user_state['items'] = results
        return user_state

def simulate_distribution(num_wishes, initial_user_state):
    num_trials = 10000
    
    # Keys will be 'n' (number of times won), values will be the frequency
    dist_featured_5 = {}
    dist_featured_4 = {}

    for _ in range(num_trials):
        # 1. CRITICAL: Deep copy the initial state so every trial starts identical
        current_state = copy.deepcopy(initial_user_state)
        
        # 2. Run the simulation for exactly y pulls
        current_state, trial_5_star_count, trial_4_star_count = simulate_wish(
            num_wishes, current_state, lightweight=True
        )        
                
        # 4. Record the total 'n' for this trial into our frequency distribution
        # Ex: dist_featured_5[1] = dist_featured_5.get(1, 0) + 1  for when the trial had exactly 1 featured 5-star drop
        dist_featured_5[trial_5_star_count] = dist_featured_5.get(trial_5_star_count, 0) + 1
        dist_featured_4[trial_4_star_count] = dist_featured_4.get(trial_4_star_count, 0) + 1

    # Optional: Convert frequencies to probabilities (percentages)
    prob_dist_5 = {n: (freq / num_trials) for n, freq in dist_featured_5.items()}
    prob_dist_4 = {n: (freq / num_trials) for n, freq in dist_featured_4.items()}
    expected_value5 = sum(n * prob for n, prob in prob_dist_5.items())
    expected_value4 = sum(n * prob for n, prob in prob_dist_4.items())

    return prob_dist_5, prob_dist_4, expected_value5, expected_value4


def calc_stats(user_items):
    stats = {
        "5star": {"total": 0, "W": 0, "L": 0, "G": 0, "CR": 0, "average_pity": 0, "win_rate": 0, "total_pity": 0, "distribution": {}},
        "4star": {"total": 0, "W": 0, "L": 0, "G": 0, "CR": 0, "average_pity": 0, "win_rate": 0, "total_pity": 0, "distribution": {}},
        "3star": {"total": 0}
    }
    
    for pull in user_items:
        name = pull['name']
        rarity = pull['rarity']
        status = pull['status']
        pity = pull['pity']

        if rarity == 5:
            stats["5star"]["distribution"][name] = stats["5star"]["distribution"].get(name, 0) + 1
            stats["5star"][status] += 1 
            stats["5star"]["total"] += 1
            # stats["5star"]["distribution_pity"][pity] += 1
            stats["5star"]["total_pity"] += pity
        elif rarity == 4:
            stats["4star"]["distribution"][name] = stats["4star"]["distribution"].get(name, 0) + 1
            stats["4star"][status] += 1
            stats["4star"]["total"] += 1
            # stats["4star"]["distribution_pity"][pity] += 1
            stats["4star"]["total_pity"] += pity
        else:
            stats["3star"]["total"] += 1

    # --- Calculation with Safety Checks ---
    for rank in ["5star", "4star"]:        
        if stats[rank]['W'] > 0:
            # Win Rate
            stats[rank]['win_rate'] = (stats[rank]['W'] / (stats[rank]['W']+stats[rank]['L'])) * 100
        if stats[rank]['total'] > 0:
            # Average Pity
            stats[rank]['average_pity'] = stats[rank]['total_pity'] / stats[rank]['total']

    return stats
