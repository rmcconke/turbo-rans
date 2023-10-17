#!/bin/bash

# Test goals:
#   - Verify same results returned from regular mode and json mode for the same conditioning (i.e., first iteration after random sampling)
#       - Note: in the general case, these modes might not return the same results, but they are still individually repeatable with a fixed random state.
#       - It appears that there may be small numerical differences when the optimizer is re-initialized, that over time change the suggestion.
#       - Nevertheless, the results are similar if you compare the target plots.
#   - Verify that regular mode and json mode run without errors
#   - Verify that the modes are switched correctly
#   - Verify that the runs are repeatable with fixed random_state in both regular mode and json mode

# Script assumes appropriate environment has been sourced.

echo "Running turbo-RANS tests...."
./reset_tests.sh
cd basic_optimization 
echo -e "\n\n\n ============= Running normal mode Test 1 =============\n \n \n">> ../tests.log
python3 optimize_x2.py >> ../tests.log
echo -e "\n\n\n ============= Running normal mode Test 2 =============\n \n \n">> ../tests.log
python3 optimize_x2.py >> ../tests.log

cd ../basic_optimization_json_mode
echo -e "\n\n\n ============= Running json mode Test 1 =============\n \n \n">> ../tests.log
python3 optimize_x2_json_mode.py >> ../tests.log
echo -e "\n\n\n ============= Running json mode Test 2 =============\n \n \n">> ../tests.log
python3 optimize_x2_json_mode.py >> ../tests.log

echo "Done."


