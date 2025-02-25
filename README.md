# *Capsaspora*

This repository contains the implementation of the *Capsaspora* model in Chaste. The model follows a centre-based approach, where cells are represented as circles, and their positions evolve based on random movement and interactions with neighboring cells. Cell behaviour is influenced by the surrounding chemical field of Fetal Bovine Serum (FBS), which is governed by a partial differential equation (PDE). FBS plays a key role in regulating cell motility and cell-cell adhesion while being gradually consumed by *Capsaspora* cells through their metabolic activity.

For more details, please refer to our manuscript [Link to our manuscript](https://doi.org/10.1101/).

## 1. Installing Chaste

All installation instructions and getting started guides for Chaste can be found on the official [Chaste webpage](https://chaste.github.io/docs/). Chaste can be installed directly on Ubuntu Linux, while Windows and macOS users can set it up via Docker as an alternative.

## 2. Change the source code to allow for periodic boundary conditions

This repository has been implemented on a domain with periodic boundary conditions in x and y directions. Cell simulations in periodic doamin have been already included in the original Chaste distribution. However, at the moment of setting this repository, Chaste does not allow for the solution of PDEs on periodic domains. Simple instructions outlined below, can allow to change this and enable the PDE solver for periodic domain. Please follow the steps below before downloading the *Capsaspora* repository. 

### Steps to apply periodic boundary conditions

**Step 1.** Modify `AbstractAssemblerSolverHybrid.hpp`

Uncomment the following line in `AbstractAssemblerSolverHybrid.hpp`. The file is located at `/path/to/Chaste/src/pde/src/solver/`, closer to the end of the file (around line 148):
```
mpBoundaryConditions->ApplyPeriodicBcsToLinearProblem(*pLinearSystem, true, true);
```
**Step 2.** Modify `BoundaryConditionsContainerImplementation.hpp`

Navigate to `BoundaryConditionsContainerImplementation.hpp` in `/path/to/Chaste/src/pde/src/common/` and locate the method `ApplyPeriodicBcsToLinearProblem(...)`.

Inside this method, find the following line:
```
PetscMatTools::SetElement(rLinearSystem.rGetLhsMatrix(), mat_index1, mat_index2, -1.0);
```
Comment out or delete this line and replace it with:
```
MatSetOption(rLinearSystem.GetLhsMatrix(), MAT_NEW_NONZERO_ALLOCATION_ERR, PETSC_FALSE);
rLinearSystem.SetMatrixElement(mat_index1, mat_index2, -1.0);
```
Additionally, comment out the following line to ensure other tests without periodic boundary conditions still function correctly:
```
// EXCEPT_IF_NOT(has_periodic_bcs);
```
Finally, wrap everything below the commented line in an outer if condition:
```
if (has_periodic_bcs) {
    // Existing code for applying periodic BCs
}
```
**Step 3.** Test periodic boundary conditions

If you want to verify that periodic boundary conditions work before applying them to the *Capsaspora* project, locate the test file `TestSimpleLinearEllipticSolver.hpp`.

Find the test function `Test2dHeatEquationWithPeriodicBcs()`. If its name is `dontTest2dHeatEquationWithPeriodicBcs()`, rename it to ensure it runs.

After the following line in the test:
```
mesh.ConstructRegularSlabMesh(0.1, width, width);
```
Insert this line:
```
PetscTools::SetOption("-ksp_type", "gmres");
```
Run the test from the build folder using (see [Chaste webpage](https://chaste.github.io/docs/) for more instructions on how to run tests):
```
make TestSimpleLinearEllipticSolver
ctest -V -R TestSimpleLinearEllipticSolver
```
The test output will be stored in the `PeriodicBcs` folder under `result.txt`. In this test, periodicity is imposed only on the left-right boundaries. To verify correctness, check that function values at these boundaries are identical in `result.txt`.

*Note:* This test may fail in Docker, although the project with periodic BCs (PdeModifier) used in *Capsaspora* works fine. If an exception occurs, proceed to **Step 4** before troubleshooting further.

4. Apply periodic BCs in your project

If the test works correctly, you can now use periodic boundary conditions in your Chaste projects. Boundary conditions are specified in PdeModifiers (e.g., `ParabolicBoxDomainPdeModifier`).

Regardless of the PdeModifier type, you need to modify the `ConstructBoundaryConditionsContainer(..)` method to impose periodicity. The best approach is to create a custom PdeModifier that inherits from the original class and overrides the boundary condition method.

This can be implemented similarly to `Test2dHeatEquationWithPeriodicBcs()`, but it's better to iterate only over boundary nodes rather than the entire mesh.

For instance, in the *Capsaspora* project, a `ParabolicBoxDomainPdeModifierPeriodicBC` class is used to implement a fully periodic boundary condition (also known as a ‘torus’ condition).

## 3. Download *Capsaspora* repository as your local Chaste project

If you are using Git, you can clone this repository directly. First, navigate to your local Chaste directory:
```
cd /path/to/Chaste/
```
Next, inside the projects directory (`/path/to/Chaste/projects/`), create a new folder named `Capsaspora` and move into it:
```
mkdir -p /path/to/Chaste/projects/Capsaspora  
cd /path/to/Chaste/projects/Capsaspora
```
Then, clone the Capsaspora repository using the following command:
```
git init  
git pull https://github.com/daria-stepanova/Capsaspora.git main
```
Alternatively, you can download the source code manually from the GitHub repository and copy it into the projects directory (`/path/to/Chaste/projects/`).

After adding the new project, reconfigure Chaste by running the following command in the terminal:
```
ccmake /path/to/Chaste/
```

## 4. Project scripts

If you are working with Chaste through Docker, you should see a `scripts` folder in the main Chaste directory. This folder contains useful scripts, including `new_project.sh` for creating new user projects and `build_project.sh` for compiling them. These scripts are particularly convenient for managing custom projects.

If the scripts folder is missing, it is helpful to add it manually. This repository includes `scripts` folder containing all the necessary files. From the project directory, simply copy this folder to your Chaste main directory:
```
cp -r scripts /path/to/Chaste/
``` 
After copying the scripts, you need to update the Chaste directory path in all of them. For example, if your Chaste directory is located at `/home/your_username/Chaste`, replace all occurrences of:
```
export CHASTE_DIR="/path/to/Chaste"
```
with:
```
export CHASTE_DIR="/home/your_username/Chaste"
```
This ensures the scripts function correctly in your environment.

## 5. How to run the model

The source code files located in `/path/to/Chaste/projects/Capsaspora/src/` include detailed comments explaining all model parameters and the steps taken to implement the model. The main source file, `CapsasporaSimulation.hpp`, allows you to modify most parameters and adjust the simulation setup. This file also contains detailed instructions on how to configure the simulation.

To run the model, navigate to the Chaste directory and execute the `build_project.sh` script. If you are building the project for the first time or have added new source files, run the script with the `c` argument:
```
cd /path/to/Chaste/  
scripts/build_project.sh Exe_Capsaspora c
```
This command compiles the project and creates an executable file, which can be found at:
```/path/to/Chaste/build/projects/Capsaspora/apps/Exe_Capsaspora```
To run the executable in the background (so the terminal can be closed while the process continues), use the `nohup` command:
```
nohup /path/to/Chaste/build/projects/Capsaspora/apps/Exe_Capsaspora >> /path/to/directory/to/redirect/shell/output/simulation.txt &  
disown
```
The output files of the simulation will be saved in Chaste’s output directory, typically:
```
/path/to/Chaste/testoutput
```  
The folder name for all output files will be displayed when building the project with `scripts/build_project.sh Exe_Capsaspora`. 
The output directory for each simulation (subfolder in the main output directory) is defined in `CapsasporaSimulation.hpp` and can be modified before building the project.

## 6. Visualisation of the results in Paraview
## 7. Simulation data from the paper
