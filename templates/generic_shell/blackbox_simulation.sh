# This is a placeholder for a script which runs a CFD simulation using a given set of coefficients, and computes a loss function.
echo "blackbox function got coefficients: `cat suggestion.json | jq`">&2

# Insert code to run simulation here
echo "blackbox function running simulation">&2

# This scoring function should be computed with the simulation results, but for now just returns the sum of the provided coefficients
echo "blackbox function computing score">&2

score=`cat suggestion.json | jq '.[]' | paste -sd+ | bc`
echo "score: $score">&2
echo "$score"

