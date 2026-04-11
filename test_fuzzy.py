import difflib

# Test fuzzy matching with Cyrillic
names = [
    'Иванов Иван Иванович',
    'Плюхин Владимир Александрович',
    'Федоров Федор Федорович',
    'Смирнов Смирнов Смирнов',
    'Петров Петр Петрович',
    'Козлов Козлович Козлович',
    'Николаев Николай Николаевич'
]

search_terms = [
    'Плюхин',
    'Плюхин Владимир',
    'Плюхин В.А.',
    'Иванов',
    'Федор'
]

print('Testing fuzzy matching with Cyrillic:')
print('=' * 80)

for term in search_terms:
    print(f'\nSearching for: "{term}"')
    matches = difflib.get_close_matches(term, names, n=3, cutoff=0.6)
    print(f'Matches (cutoff=0.6): {matches}')
    
    matches = difflib.get_close_matches(term, names, n=3, cutoff=0.4)
    print(f'Matches (cutoff=0.4): {matches}')
    
    matches = difflib.get_close_matches(term, names, n=3, cutoff=0.3)
    print(f'Matches (cutoff=0.3): {matches}')
    
    # Also try with normalized names (just surnames)
    surnames = [name.split()[0] for name in names]
    print(f'Surnames: {surnames}')
    matches = difflib.get_close_matches(term, surnames, n=3, cutoff=0.6)
    print(f'Surname matches (cutoff=0.6): {matches}')
