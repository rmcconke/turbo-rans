#!/bin/bash

# This is a placeholder for a script which runs a CFD simulation using a given set of coefficients, and computes a loss function.
echo -e "\nblackbox function got coefficients: `cat suggestion.json | jq`">&2

# Insert code to run simulation here
echo "blackbox function running simulation">&2

# This scoring function should be computed with the simulation results.
# For now, it just returns -x^2 (where x is the coefficient)
echo "blackbox function computing score">&2

#score=`cat suggestion.json | jq '.[]' | paste -sd+ | bc`
x=`cat suggestion.json | jq '.[]'`
score=`echo "-1*$x^2" | bc`

echo "score: $score">&2
echo "$score"

