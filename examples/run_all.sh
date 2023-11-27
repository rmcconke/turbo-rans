#!/bin/bash
./reset_all.sh

echo Running all examples....
cd basic_optimization_json_mode && ./basic_json_mode.sh
cd ../basic_optimization_python_mode && ./basic_python_mode.sh
cd ../openfoam_airfoil_pythonscript && ./airfoil_example.sh
cd ../openfoam_airfoil_shellscript && ./airfoil_example.sh
cd ../openfoam_periodichills && ./periodichills_example.sh

echo Running templates....
cd ../../templates/generic_python && ./main.sh
cd ../generic_shell && ./main.sh










