import os
import random
from service_api.models import Service

def load_words(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

current_dir = os.path.dirname(__file__)
adjectives_path = os.path.join(current_dir, 'adjectives.txt')
nouns_path = os.path.join(current_dir, 'nouns.txt')

adjectives = load_words(adjectives_path)
nouns = load_words(nouns_path)

def generate_unique_domain_prefix():
    while True:
        adjective = random.choice(adjectives)
        noun = random.choice(nouns)
        combination = f"{adjective}-{noun}"
        if not Service.objects.filter(hostname=combination).exists():
            return combination

