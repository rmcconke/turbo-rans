from blackbox_simulation import blackbox_simulation
import turborans

# Uncomment to see python logging info
#import logging
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)

# To reset the optimization, delete history.json and suggestion.json

iterations=30

for i in range(iterations):
    print(f'===== Iteration: {i} =====')
    turborans.suggest()
    search_point = turborans.utilities.json_io.load_suggestion()
    score = blackbox_simulation(search_point)
    turborans.register_score(score = score)
