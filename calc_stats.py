import json

def calc_stats(username, user_items):
    stats = {
        "5star": {"total": 0, "W": 0, "L": 0, "G": 0, "CR": 0, "average_pity": 0, "win_rate": 0, "total_pity": 0, "distribution": {}},
        "4star": {"total": 0, "W": 0, "L": 0, "G": 0, "CR": 0, "average_pity": 0, "win_rate": 0, "total_pity": 0, "distribution": {}},
        "3star": {"total": 0}
    }
    
    for pull in user_items:
    # for pull in user_items[username]['items']:
        name = pull['name']
        rarity = pull['rarity']
        status = pull['status']
        pity = pull['pity']
        # pity = pull.get('pity', 0)

        if rarity == 5:
            stats["5star"]["distribution"][name] = stats["5star"]["distribution"].get(name, 0) + 1
            stats["5star"][status] += 1
            stats["5star"]["total"] += 1
            stats["5star"]["total_pity"] += pity
        elif rarity == 4:
            stats["4star"]["distribution"][name] = stats["4star"]["distribution"].get(name, 0) + 1
            stats["4star"][status] += 1
            stats["4star"]["total"] += 1
            stats["4star"]["total_pity"] += pity
        else:
            stats["3star"]["total"] += 1

    # --- Calculation with Safety Checks ---
    for rank in ["5star", "4star"]:        
        if stats[rank]['W']+stats[rank]['L'] > 0:
            # Win Rate
            stats[rank]['win_rate'] = (stats[rank]['W'] / (stats[rank]['W']+stats[rank]['L'])) * 100
        if stats[rank]['total'] > 0:
            # Average Pity
            stats[rank]['average_pity'] = stats[rank]['total_pity'] / stats[rank]['total']

    return stats
    
# with open('data.json', 'r') as f:
#     pull_results_data = json.load(f)    
# stats = calc_stats("Aqil", pull_results_data)
# print(stats["5star"])    
# print(stats["4star"])    
