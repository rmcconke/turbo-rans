The Fluent example here is less automated than the basic and OpenFOAM examples. 
We've included the code here we used to automate a Fluent journal file.
This code edits the line where turbulence model coefficients are set in the journal file, and then runs this journal file in Windows PowerShell.
The journal file completes all postprocessing necessary, and then the files are read for objective function calculations.
Feel free to reach out if you have any questions about the Fluent example case.