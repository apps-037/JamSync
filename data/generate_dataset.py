# generate_dataset.py
# creates synthetic musician data for testing

import random
import json
import numpy as np

NUM_MUSICIANS = 100
RANDOM_SEED = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# based on typical instrument distributions in community music programs
INSTRUMENTS = {
    "Guitar": 30,
    "Vocals": 20,
    "Keys": 15,
    "Drums": 10,
    "Bass": 10,
    "Saxophone": 5,
    "Trumpet": 4,
    "Violin": 3,
    "Other": 3
}

GENRES = ["Rock", "Jazz", "Blues", "Pop", "Metal", "Folk", "R&B", "Classical", "Electronic", "Indie"]

LOCATIONS = ["Boston", "Cambridge", "Somerville", "Brookline", "Allston"]

FIRST_NAMES = [
    "Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery",
    "Quinn", "Sage", "Skylar", "River", "Rowan", "Dakota", "Finley", "Reese",
    "Charlie", "Blake", "Emerson", "Drew", "Cameron", "Kai", "Elliot", "Jules",
    "Parker", "Hayden", "Lennon", "Phoenix", "Ashton", "Marlowe"
]

LAST_NAMES = [
    "Chen", "Rivera", "Lee", "Park", "Blake", "Singh", "Johnson", "Garcia",
    "Williams", "Martinez", "Brown", "Davis", "Rodriguez", "Wilson", "Moore",
    "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
    "Thompson", "Young", "King", "Wright", "Lopez", "Hill", "Green", "Adams"
]

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
TIME_SLOTS = ["06-09", "09-12", "12-15", "15-18", "18-21", "21-00"]

def generate_musician(id_num):
    
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    
    # pick instrument based on weights
    instrument = random.choices(
        list(INSTRUMENTS.keys()),
        weights=list(INSTRUMENTS.values())
    )[0]
    
    # skill: normal distribution, mean 6, std 2
    skill = int(np.clip(np.random.normal(6, 2), 1, 10))
    
    # pick 2-4 genres randomly
    num_genres = random.choices([2, 3, 4], weights=[0.4, 0.4, 0.2])[0]
    genres = random.sample(GENRES, num_genres)
    
    # availability: 2-6 time slots
    num_slots = random.randint(2, 6)
    availability = []
    for _ in range(num_slots):
        day = random.choice(DAYS)
        time = random.choice(TIME_SLOTS)
        slot = f"{day}_{time}"
        if slot not in availability:
            availability.append(slot)
    
    location = random.choice(LOCATIONS)
    
    # personality: 0 to 1 scale
    personality_leader = round(random.random(), 2)
    personality_improviser = round(random.random(), 2)
    
    return {
        "id": id_num,
        "name": name,
        "instrument": instrument,
        "skill_level": skill,
        "genres": genres,
        "availability": availability,
        "location": location,
        "personality_leader": personality_leader,
        "personality_improviser": personality_improviser
    }

def main():
    
    print(f"Generating {NUM_MUSICIANS} musicians...")
    print(f"Using seed: {RANDOM_SEED}\n")
    
    musicians = []
    for i in range(1, NUM_MUSICIANS + 1):
        musician = generate_musician(i)
        musicians.append(musician)
        
        if i % 10 == 0:
            print(f"Generated {i}/{NUM_MUSICIANS}...")
    
    output_file = "data/musicians_dataset.json"
    with open(output_file, 'w') as f:
        json.dump(musicians, f, indent=2)
    
    print(f"\nGenerated {NUM_MUSICIANS} musicians")
    print(f"Saved to: {output_file}")
    
    # print some stats
    print("\nDataset Statistics:")
    print(f"Total musicians: {len(musicians)}")
    
    from collections import Counter
    instrument_counts = Counter()
    for m in musicians:
        instrument_counts[m['instrument']] += 1
    
    print("\nInstruments:")
    for inst, count in sorted(instrument_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {inst}: {count}")
    
    skills = []
    for m in musicians:
        skills.append(m['skill_level'])
    
    print(f"\nSkill Levels:")
    print(f"  Average: {sum(skills)/len(skills):.1f}")
    print(f"  Range: {min(skills)} - {max(skills)}")
    print(f"  Distribution:")
    
    skill_dist = Counter(skills)
    for skill in range(1, 11):
        count = skill_dist.get(skill, 0)
        print(f"    {skill:2d}: {count}")
    
    # genre stats
    all_genres = []
    for m in musicians:
        for g in m['genres']:
            all_genres.append(g)
    
    genre_counts = Counter(all_genres)
    print(f"\nTop 5 Genres:")
    for genre, count in genre_counts.most_common(5):
        print(f"  {genre}: {count}")
    
    # location stats
    location_counts = Counter()
    for m in musicians:
        location_counts[m['location']] += 1
    
    print(f"\nLocations:")
    for loc in sorted(location_counts.keys()):
        count = location_counts[loc]
        print(f"  {loc}: {count}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()