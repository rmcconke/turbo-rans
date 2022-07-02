from blackbox_simulation import blackbox_simulation
from turborans.suggest_coeffs import suggest
from turborans.update_history import register_score
from turborans.utilities.json_io import load_suggestion

# To reset the optimization, delete history.json and suggestion.json

iterations=15

for i in range(iterations):
    print(f'===== Iteration: {i} =====')
    suggest()
    search_point = load_suggestion()
    score = blackbox_simulation(search_point)
    register_score(score = score)
