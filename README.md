# *Capsaspora*

This repository contains the implementation of the *Capsaspora* model in Chaste. The model follows a centre-based approach, where cells are represented as circles, and their positions evolve based on random movement and interactions with neighboring cells. Cell behaviour is influenced by the surrounding chemical field of Fetal Bovine Serum (FBS), which is governed by a partial differential equation (PDE). FBS plays a key role in regulating cell motility and cell-cell adhesion while being gradually consumed by *Capsaspora* cells through their metabolic activity.

For more details, please refer to our manuscript [Link to our manuscript](https://doi.org/10.1101/).

## 1. Installing Chaste

All installation instructions and getting started guides for Chaste can be found on the official [Chaste webpage](https://chaste.github.io/docs/). Chaste can be installed directly on Ubuntu Linux, while Windows and macOS users can set it up via Docker as an alternative.

## 2. Change the source code to allow for periodic boundary conditions

This repository has been implemented on a domain with periodic boundary conditions in x and y directions. Cell simulations in periodic domain have been already included in the original Chaste distribution. However, at the moment of setting this repository, Chaste does not allow for the solution of PDEs on periodic domains. Simple instructions outlined below, can allow to change this and enable the PDE solver for periodic domain. Please follow the steps below before downloading the *Capsaspora* repository. 

### Steps to apply periodic boundary conditions

**Step 1.** Modify `AbstractAssemblerSolverHybrid.hpp`

Uncomment the following line in `AbstractAssemblerSolverHybrid.hpp`. The file is located at `/path/to/Chaste/src/pde/src/solver/`, closer to the end of the file (around line 148):
```
mpBoundaryConditions->ApplyPeriodicBcsToLinearProblem(*pLinearSystem, true);
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
Finally, wrap everything below (until the end of the function) the commented line in an outer if condition:
```
if (has_periodic_bcs) {
    // Existing code for applying periodic BCs
}
```
**Step 3.** Test periodic boundary conditions

If you want to verify that periodic boundary conditions work before applying them to the *Capsaspora* project, locate the test file `TestSimpleLinearEllipticSolver.hpp`.

Find the test function `Test2dHeatEquationWithPeriodicBcs()`. If its name is `dont_Test2dHeatEquationWithPeriodicBcs()` or `dontTest2dHeatEquationWithPeriodicBcs()`, rename it to ensure it runs.

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

Simulation results generated with Chaste can be visualized using [ParaView](https://www.paraview.org/), an open-source software for post-processing and visualisation. ParaView allows users to automate visualisation steps using Python scripts, which can be executed within ParaView’s Python Shell.

This repository includes a `visualisation` folder containing the Python script `CapsasporaAnimation.py`, which was used to generate figures and supplementary movies for the manuscript. The script provides four visualisation methods:

* `Capsaspora360(sim_folder, folder_save_video, save_anim)` visualises simulations on small square domains ($360 ~\mu m \times 360 ~\mu m$). Cells are coloured based on local FBS concentration.
* `Capsaspora1080(sim_folder, folder_save_video, save_anim)` visualises simulations on large square domains ($1080 ~\mu m \times 1080 ~\mu m$). Cells are coloured based on local FBS concentration.
* `Capsaspora360_CellDensity(sim_folder, folder_save_video, save_anim)` visualises simulations on small square domains ($360 ~\mu m \times 360 ~\mu m$). Cells are coloured according to local cell density (number of cells within a circular neighborhood of $10 ~\mu m$ radius, normalised by the circle area).
* `Capsaspora1080_CellDensity(sim_folder, folder_save_video, save_anim)` visualises simulations on large square domains ($1080 ~\mu m \times 1080 ~\mu m$). Cells are coloured according to local cell density.

Each method requires the following three arguments:

* `sim_folder` – Absolute path to the folder containing simulation output files.
* `folder_save_video` – Absolute path to the directory where the animation video will be saved.
* `save_anim` – Boolean (`True` or `False`), specifying whether to save the animation as a `.avi` movie. If `save_anim = False`, the simulation will be visualised in ParaView but not saved.

To run the script in ParaView:

1. Open ParaView.
2. Open the Python Shell (`View -> Python Shell`).
3. Copy and paste the following commands, modifying paths as needed:

```
import sys  
import importlib  

# Provide the absolute path to the directory where CapsasporaAnimation.py is saved  
sys.path.append("/absolute/path/to/CapsasporaAnimation/")  

# Import the visualization script  
import CapsasporaAnimation as cplot  

# Set save_anim to False if you do not want to save the animation  
save_anim = True  

# Set the absolute path to the simulation output directory  
sim_folder = "/absolute/path/to/simulation/output"  

# Set the absolute path to the directory where the animation will be saved (e.g., Downloads folder)  
folder_save_video = "/Users/your_username/Downloads"  

# Reload the module in case of any changes  
importlib.reload(cplot)  

# Choose a visualisation method  
cplot.Capsaspora360(sim_folder, folder_save_video, save_anim)  
# cplot.Capsaspora1080(sim_folder, folder_save_video, save_anim)  
# cplot.Capsaspora360_CellDensity(sim_folder, folder_save_video, save_anim)  
# cplot.Capsaspora1080_CellDensity(sim_folder, folder_save_video, save_anim)  
```
You can modify any of the methods to adjust the appearance of the animation (e.g. changing font size, color schemes, etc.).

## 7. Simulation data from the paper

The simulation data used to generate figures and supplementary movies for the manuscript have been uploaded to Figshare (approximately n GB) and can be downloaded from: [https://doi.org/figshare/number](https://doi.org/figshare/number).

To reproduce the simulation animations, you can use the visualization scripts described in **Section 6**.

## 8. Aggregate quantification using [DBSCAN](https://file.biolab.si/papers/1996-DBSCAN-KDD.pdf)

The `aggregate_quantification` directory in this repository contains two Python scripts designed to analyse the distribution of *Capsaspora* aggregates over time. The `GetClusterSizes_Folder.py` script processes system snapshots sequentially at each time point. It internally calls `GetClusterSizes_Frame.py` to compute cluster sizes based on area and the number of cells. The results are then saved in a `.txt` file in the following format:

```
[frame number]   \t [aggregate 1, cell #] \t [aggregate 1, area] \t [aggregate 2, cell #] \t [aggregate 2, area]
[frame number+1] \t [aggregate 1, cell #] \t [aggregate 1, area] \t [aggregate 2, cell #] \t [aggregate 2, area] \t [aggregate 3, cell #] \t [aggregate 3, area]
```
The first value represents the frame number (typically, our simulations have 1050 frames). Each frame is followed by tab-separated values for the number of cells and area of each aggregate. The number of cell count-area pairs corresponds to the number of aggregates at that time point. This output can be used to derive statistics on aggregate area distributions, cell count per aggregate, and aggregate density, similar to the results presented in our manuscript.

`GetClusterSizes_Folder.py` requires two arguments:
* Absolute path of the folder containing simulation results.
* Final frame number (default: 1050).
  
To ensure correct execution, certain parameters may need to be adjusted within the script:
* `sim_end_time` – Final simulation time (e.g. 70 hours in our simulations).
* `sim_dt` – Timestep used in the simulation. Required for correctly accessing individual simulation files, as frame numbers are not consecutive (output is saved every `plot_counter` simulation steps).
* `L` – Domain size in $\mu m$.
* `print_fig` – Boolean (`True` or `False`), determines whether to save figures with aggregate metrics for each frame.
* `threshold` – Passed to DBSCAN ($\epsilon$), defines the distance threshold between cells for clustering. Cells within this threshold are considered part of the same aggregate.

To execute the script in the background, use:
```
nohup python /absolute/path/to/simulation/folder 1050 >> output_AggregateQuantification.txt &  
disown
```
Here, 1050 specifies the last frame number.
