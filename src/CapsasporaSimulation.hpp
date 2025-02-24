
#ifndef CAPSASPORASIMULATION_HPP_
#define CAPSASPORASIMULATION_HPP_

#include <string>
#include <ctime>
#include "CheckpointArchiveTypes.hpp"
#include "LogFile.hpp"
#include "SmartPointers.hpp"

#include "DifferentiatedCellProliferativeType.hpp"
#include "StemCellProliferativeType.hpp"
#include "WildTypeCellMutationState.hpp"

#include "OffLatticeSimulation.hpp"
#include "PeriodicNodesOnlyMesh.hpp"
#include "NodeBasedCellPopulation.hpp"


#include "AveragedSourceParabolicPde.hpp"
#include "ParabolicBoxDomainPdeModifierPeriodicBC.hpp"

#include "MyCellCycleModel.hpp"
#include "MyForce.hpp"
#include "MyDiffusionForce.hpp"


class CapsasporaSimulation
{

public:
  void TestCapsasporaSimulation()
    {
        SetupSingletons(std::time(0));
        LogFile::Instance()->Set(2, "TestCapsasporaSimulation_Log");
        
        // For Capsaspora simulations, the parameters to choose are:
        // initial FBS (from 0 to 10%)
        // cell adhesion response to FBS (Hill, shallow linear or steep linear)
        // domain (small, 360 um, or large, 1080 um)

        // Initial FBS
        // FBS concentration in simulations is normalised such that 5% corresponds to fbs = 1.0 in simulations
        // fbs = 0.1  corresponds to 0.5%  FBS
        // fbs = 0.2  corresponds to 1.0%  FBS
        // fbs = 1.0  corresponds to 5.0%  FBS
        // fbs = 2.0  corresponds to 10.0% FBS
        double FBS_init_concentration = 1.0;

        // FBS response type (how cell adhesion strength inreases with FBS, mu_l(FBS)):
        // 0  - steep linear response:    mu_l(FBS) = k_mu^2 * FBS
        // 1  - Hill sigmoidal response:  mu_l(FBS) = mu0/(1 + (f0/FBS)^n0)
        // 2  - shallow linear response:  mu_l(FBS) = k_mu^1 * FBS
        int fbs_response_type = 1;  //0, 1 or 2

        // Domain size (periodic boundary condition in x and y directions).
        // Spatial coordinates are normalised with cell radius (R = 3 um). Real domain dimensions = (domain_size_x*R, domain_size_y*R)
        // small domain, a square with side of 360 um   (120 in dimensionless units)
        // large domain, a square with side of 1080 um  (360 in dimensionless units)
        // When domain size is changed, the initial number of cells should be adjusted to maintain the same initial cell density.
        // small domain:
        double domain_size_x = 120.0, domain_size_y = 120.0;
        int num_nodes = 24;
        // large domain:
        //double domain_size_x = 360.0, domain_size_y = 360.0;
        //int num_nodes = 216;

        // Name of the directory in which the output will be saved
        std::stringstream ss;
        ss<<"Capsaspora"<<"_FBSinit"<<FBS_init_concentration<<"_FbsResp-"<<fbs_response_type;
        std::string folder_to_save = ss.str();

        // Final simulation time (in hours)
        double sim_end_time = 70.0;
        
        // How many timepoints will be saved in the output. 
        // System configuration will be saved every sim_end_time/number_of_frames hours
        double number_of_frames = 1050.0;

        // %%%%%%%%%%%%%%%% From here on, the parameters should not be changed. %%%%%%%%%%%%%%%%%%%%%%
        
        // Simulation timestep
        double sim_dt = 0.00001;
        if ((fbs_response_type==1 || fbs_response_type==0) && (FBS_init_concentration>1.0)) // timestep should be reduced when adhesion forces are stronger (in high FBS)
          sim_dt = 0.000004;

        // Parameter controlling the strength of short-range repulsion (mu_s in the manuscript)
        double force_mu = 300.0;
        // Parameter controlling the range of the adhesion force (a_l in the manuscript) 
        double force_delta = 0.5;
        
        // Default value of cell motility at 0% FBS (D(0.0) in the manuscript).
        // In the manuscript the values are provided in um^2/min or 1/min in nondimensional space units.
        // Simulations are set up in hours. Thus, the parameter values shown in the manuscript must be converted to 1/h (by multiplying by 60)
        double cell_diffusion = 16.866; // = 0.2811*60

        // Parameters for different FBS-dependent cell adhesion response
        double n0 = 0.0, f0 = 0.0, mu0 = 0.0;

        if(fbs_response_type==1)        // Hill
        {
          n0 = 1.8153; mu0 = 470.7025; f0 = 3.8494;
        }
        else if(fbs_response_type==0)   // linear (step)
        {
          mu0 = 40.0;    // in manuscript this parameter is called k_mu^2
        }
        else                            // linear (shallow)
        {
          mu0 = 22.0;   // in manuscript this parameter is called k_mu^1
        }

        // Parameters defining the temporal evolution of FBS.
        // FBS_C is a coefficient in front of the partial derivative with respect to time
        // FBS_D is the FBS diffusion (D_fbs in the manuscript)
        // FBS__Uptake sets the rate of FBS consumption by cells
        // FBS_mesh is an auxilary parameter setting the size of finite elements for the Finite Element Method which is used to solve the FBS PDE
        double FBS_C = 1.0, FBS_D = 75.0, FBS_Uptake = -2.3, FBS_mesh = 4.8;
        // 0 - linear; 1 - hill; 2 - double hill; 3 - constant force; 4 - linear (shallow slope)
        
        // Interaction radius of particles is the cell radius. Space dimensions have been normalised with cell radius (R = 3 um), thus, the interaction radius in simulations is 1.0
        double interaction_radius = 1.0;
        
        // This parameter is used for speeding up numerical simulations.
        // Beyond this distance, cells are no longer considered neighbours and their pairwise interaction force is set to 0.
        double max_interaction_distance = 15.0;
        
        // Mean value of Capsaspora cell cycle obtained from data in (Perez-Posada, 2020). This value is used only to initialise cell cycle (set their birth times in the past).
        double average_cell_cycle_duration = 9.87;

        // %%%%%%%%%%%%%%%%%%%%% Here, we begin setting up the simulation %%%%%%%%%%%%%%%%%%%%%%
        // Cells are a collection of 'nodes' (because this type of models is sometimes called node-based simulations)
        std::vector< Node<2>*> mynodes;   
        double x0 =0.0, y0=0.0;

        // We generate random initial locations within the domain for each cell
        for(int i=0;i< num_nodes;i++)
        {
          ChastePoint<2> p_node(x0 + (domain_size_x - x0)*RandomNumberGenerator::Instance()->ranf(), y0 + (domain_size_y - y0)*RandomNumberGenerator::Instance()->ranf() );
          mynodes.push_back(new Node<2>(i,p_node,false));
        }
        
        // Set domain periodicity, i.e. make it a torus
        c_vector<double,2> periodic_width = zero_vector<double>(2);
        periodic_width[0] = std::ceil(domain_size_x/interaction_radius)*interaction_radius;
        periodic_width[1] = std::ceil(domain_size_y/interaction_radius)*interaction_radius;
        PeriodicNodesOnlyMesh<2> mesh(periodic_width);
        mesh.ConstructNodesWithoutMesh(mynodes, max_interaction_distance);
        
        // Create a class to define cells (cells are defined by their type and cell cycle model)
        std::vector<CellPtr> cells;
        
        // Capsaspora cells can divide. In Chaste, cells that are allowed to divide are set to the 'stem cell type'
        MAKE_PTR(StemCellProliferativeType,p_diff_type);
        // If needed, cell division can be turned off by making all cells of 'differentiated' type (do not proliferate)
        // MAKE_PTR(DifferentiatedCellProliferativeType,p_diff_type); 
        
        // All cells are set to be wild type. If needed, Chaste has capability to add and track mutant cell populations.
        MAKE_PTR(WildTypeCellMutationState, p_state);

        // Now, we initialise the cells with their individual cell cycle models.
        for (int i=0; i<num_nodes; i++)
        {
          // Cell cycle was fitted to the experimental data and the Inverse Gaussian (Wald) distribution fits the best.
          // Parameter values of this distribution are mu and lambda were obtained from the fitting.
          MyCellCycleModel* p_model = new MyCellCycleModel();
          p_model->SetMu(2.153);
          p_model->SetLambda(12.2344);

          p_model->SetDimension(2);
          CellPtr p_cell(new Cell(p_state, p_model));
          p_cell->SetCellProliferativeType(p_diff_type);
          p_cell->InitialiseCellCycleModel();
          p_cell->GetCellData()->SetItem("fbs",FBS_init_concentration);
          // Birth time is set in the past (negative time) by sampling from U[0,1]*(mean cell cycle). U[0,1] is a random uniform distribution on [0,1] interval.
          double birth_time = - RandomNumberGenerator::Instance()->ranf()* average_cell_cycle_duration;
          p_cell->SetBirthTime(birth_time);
          cells.push_back(p_cell);
        }

        // We generate cell population by connecting cells with their initial positions.
        NodeBasedCellPopulation<2> cell_population(mesh,cells);

        // Interaction radius for all the cells is set to 1.0 (this value is normalised).
        for(unsigned i =0; i<cell_population.GetNumNodes();i++)
        {
          cell_population.GetNode(i)->SetRadius(interaction_radius);
        }

        // This parameter is set to a high value to ensure that no exception is triggered when instabilities occur. 
        // No instabilities should appear but if they do, it is easier to pinpoint the problem if simulations continue.
        // Thus, we choose some large number (the exact number does not really matter).
        cell_population.SetAbsoluteMovementThreshold(500.0);

        // We set up the simulator for the given cell population.
        OffLatticeSimulation<2> simulator(cell_population);
        // Setting final simulation time.
        simulator.SetEndTime(sim_end_time);
        // Timestep of the simulations.
        simulator.SetDt(sim_dt);
        // How often to save the output configuration.
        simulator.SetSamplingTimestepMultiple(std::ceil(sim_end_time/sim_dt/number_of_frames));
        // The name of the output directory.
        simulator.SetOutputDirectory(folder_to_save);
        
        // This sets up the interaction force between cells.
        MAKE_PTR(MyForce<2>, p_force);
        // Range of long-range cell adhesion.
        p_force->SetDelta(force_delta);
        // Strength of short-range repulsion.
        p_force->SetStiffness(force_mu);
        // FBS-dependent cell adhesion response.
        p_force->SetNonLinearResponse(n0,f0,mu0,fbs_response_type);
        // Distance beyond which cells are not considered neighbours (and their interaction force = 0.0).
        p_force->SetCutOffLength(max_interaction_distance);
        simulator.AddForce(p_force);

        // The second force that affects cell movement is random motility which is modelled as Brownian motion.
        MAKE_PTR(MyDiffusionForce<2>, p_force_diff);
        // Here, we simply set it to to the default cell motility at 0% FBS. FBS-dependent cell diffusion is set inside the 'MyDiffusionForce' calss
        p_force_diff->SetDiffusionConstant(cell_diffusion);
        simulator.AddForce(p_force_diff);

        // Finally, we add a PDE solver for the FBS evolution.
        MAKE_PTR_ARGS(AveragedSourceParabolicPde<2>, p_pde, (cell_population, FBS_C,FBS_D,FBS_Uptake));
        MAKE_PTR_ARGS(ConstBoundaryCondition<2>, p_bc, (0.0));
        
        // Create a ChasteCuboid on which to base the finite element mesh used to solve the PDE.
        ChastePoint<2> lower(0.0, 0.0);
        ChastePoint<2> upper((periodic_width[0]), (periodic_width[1]));
        MAKE_PTR_ARGS(ChasteCuboid<2>, p_cuboid, (lower, upper));

        // Create a PDE modifier and set the name of the dependent variable in the PDE.
        // We use periodic boundary conditions.
        MAKE_PTR_ARGS(ParabolicBoxDomainPdeModifierPeriodicBC<2>, p_pde_modifier, (p_pde, p_bc, true, p_cuboid,FBS_mesh));  // add step size if box domain is not integer (must be multiple of the stepsize which is 1.0 by default)
        p_pde_modifier->SetDependentVariableName("fbs");
        simulator.AddSimulationModifier(p_pde_modifier);

        // Perform the simulation.
        simulator.Solve();

        // Clean up.
        DestroySingletons();

  }

private:
  void SetupSingletons(unsigned seed)
  {
      // Set up what the test suite would do
      SimulationTime::Instance()->SetStartTime(0.0);
      //RandomNumberGenerator::Instance()->Reseed(time(NULL));
      //std::stringstream message;
      //message << "Reseeding with seed " << std::to_string(seed) << std::endl;
      //std::cout << message.str() << std::flush;
      RandomNumberGenerator::Instance()->Reseed(seed);
      CellPropertyRegistry::Instance()->Clear();
      CellId::ResetMaxCellId();
  }

  void DestroySingletons()
  {
      // This is from the tearDown method of the test suite
      SimulationTime::Destroy();
      RandomNumberGenerator::Destroy();
      CellPropertyRegistry::Instance()->Clear();
  }
};

#endif /*CAPSASPORASIMULATION_HPP_*/
