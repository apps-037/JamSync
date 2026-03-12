# generate_dataset.py
import random
import json
import numpy as np

# Configuration
NUM_MUSICIANS = 100
RANDOM_SEED = 42  # For reproducibility

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Realistic distributions
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
    """Generate one realistic musician profile"""
    
    # Random name (ensure uniqueness by combining with number if needed)
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    
    # Weighted random instrument
    instrument = random.choices(
        list(INSTRUMENTS.keys()),
        weights=list(INSTRUMENTS.values())
    )[0]
    
    # Skill level: Normal distribution (mean=6, std=2)
    # Most people are average (5-7), fewer beginners (1-3) and experts (8-10)
    skill = int(np.clip(np.random.normal(6, 2), 1, 10))
    
    # Random 2-4 genres (more likely to have 2-3)
    num_genres = random.choices([2, 3, 4], weights=[0.4, 0.4, 0.2])[0]
    genres = random.sample(GENRES, num_genres)
    
    # Random availability (5-15 hours per week)
    # Most people have 2-5 time slots available
    num_slots = random.randint(2, 6)
    availability = []
    for _ in range(num_slots):
        day = random.choice(DAYS)
        time = random.choice(TIME_SLOTS)
        slot = f"{day}_{time}"
        if slot not in availability:  # Avoid duplicates
            availability.append(slot)
    
    # Random location
    location = random.choice(LOCATIONS)
    
    # Personality traits (0.0 to 1.0)
    # Leader: 0.0 = always support, 1.0 = always lead
    # Improviser: 0.0 = structured only, 1.0 = pure improv
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
    """Generate 100 musicians and save to JSON file"""
    
    print(f"🎵 Generating {NUM_MUSICIANS} synthetic musicians...")
    print(f"   Using random seed: {RANDOM_SEED} (for reproducibility)\n")
    
    musicians = []
    for i in range(1, NUM_MUSICIANS + 1):
        musician = generate_musician(i)
        musicians.append(musician)
        
        # Print progress
        if i % 10 == 0:
            print(f"   Generated {i}/{NUM_MUSICIANS}...")
    
    # Save to JSON file
    output_file = "data/musicians_dataset.json"
    with open(output_file, 'w') as f:
        json.dump(musicians, f, indent=2)
    
    print(f"\n✅ Successfully generated {NUM_MUSICIANS} musicians!")
    print(f"📁 Saved to: {output_file}")
    
    # Print statistics
    print("\n📊 Dataset Statistics:")
    print(f"   Total musicians: {len(musicians)}")
    
    # Count instruments
    from collections import Counter
    instrument_counts = Counter(m['instrument'] for m in musicians)
    
    print("\n   Instruments:")
    for inst, count in sorted(instrument_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"      {inst}: {count}")
    
    # Skill distribution
    skills = [m['skill_level'] for m in musicians]
    print(f"\n   Skill Levels:")
    print(f"      Average: {sum(skills)/len(skills):.1f}")
    print(f"      Range: {min(skills)} - {max(skills)}")
    print(f"      Distribution:")
    skill_dist = Counter(skills)
    for skill in range(1, 11):
        count = skill_dist.get(skill, 0)
        bar = '▓' * count
        print(f"         {skill:2d}: {bar} ({count})")
    
    # Genre distribution
    all_genres = [g for m in musicians for g in m['genres']]
    genre_counts = Counter(all_genres)
    print(f"\n   Top 5 Genres:")
    for genre, count in genre_counts.most_common(5):
        print(f"      {genre}: {count}")
    
    # Location distribution
    location_counts = Counter(m['location'] for m in musicians)
    print(f"\n   Locations:")
    for loc, count in sorted(location_counts.items()):
        print(f"      {loc}: {count}")
    
    print("\n🎉 Dataset ready to use!")
    print(f"💡 Next: Upload {output_file} to Google Colab to explore!")

if __name__ == "__main__":
    main()