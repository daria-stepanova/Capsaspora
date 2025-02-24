
#include "ParabolicBoxDomainPdeModifierPeriodicBC.hpp"
#include "SimpleLinearParabolicSolver.hpp"
//#include "NodeLocationWriter.hpp"

template<unsigned DIM>
ParabolicBoxDomainPdeModifierPeriodicBC<DIM>::ParabolicBoxDomainPdeModifierPeriodicBC(boost::shared_ptr<AbstractLinearPde<DIM,DIM> > pPde,
                                                                  boost::shared_ptr<AbstractBoundaryCondition<DIM> > pBoundaryCondition,
                                                                  bool isNeumannBoundaryCondition,
                                                                  boost::shared_ptr<ChasteCuboid<DIM> > pMeshCuboid,
                                                                  double stepSize,
                                                                  Vec solution)
    : ParabolicBoxDomainPdeModifier<DIM>(pPde,
                                        pBoundaryCondition,
                                        isNeumannBoundaryCondition,
                                        pMeshCuboid,
                                        stepSize,
                                        solution)
{
}

template<unsigned DIM>
ParabolicBoxDomainPdeModifierPeriodicBC<DIM>::~ParabolicBoxDomainPdeModifierPeriodicBC()
{
}

template<unsigned DIM>
void ParabolicBoxDomainPdeModifierPeriodicBC<DIM>::UpdateAtEndOfTimeStep(AbstractCellPopulation<DIM,DIM>& rCellPopulation)
{
    // Set up boundary conditions
    std::shared_ptr<BoundaryConditionsContainer<DIM,DIM,1> > p_bcc = ConstructBoundaryConditionsContainer(rCellPopulation);

    this->UpdateCellPdeElementMap(rCellPopulation);

    // When using a PDE mesh which doesn't coincide with the cells, we must set up the source terms before solving the PDE.
    // Pass in already updated CellPdeElementMap to speed up finding cells.
    this->SetUpSourceTermsForAveragedSourcePde(this->mpFeMesh, &this->mCellPdeElementMap);

    // Use SimpleLinearParabolicSolver as averaged Source PDE
    SimpleLinearParabolicSolver<DIM,DIM> solver(this->mpFeMesh,
                                                boost::static_pointer_cast<AbstractLinearParabolicPde<DIM,DIM> >(this->GetPde()).get(),
                                                p_bcc.get());

    ///\todo Investigate more than one PDE time step per spatial step
    SimulationTime* p_simulation_time = SimulationTime::Instance();
    double current_time = p_simulation_time->GetTime();
    double dt = p_simulation_time->GetTimeStep();
    solver.SetTimes(current_time,current_time + dt);
    solver.SetTimeStep(dt);

    // Use previous solution as the initial condition
    Vec previous_solution = this->mSolution;
    solver.SetInitialCondition(previous_solution);

    // Note that the linear solver creates a vector, so we have to keep a handle on the old one
    // in order to destroy it
    this->mSolution = solver.Solve();
    PetscTools::Destroy(previous_solution);
    this->UpdateCellData(rCellPopulation);
}

template<unsigned DIM>
void ParabolicBoxDomainPdeModifierPeriodicBC<DIM>::SetupSolve(AbstractCellPopulation<DIM,DIM>& rCellPopulation, std::string outputDirectory)
{
    AbstractBoxDomainPdeModifier<DIM>::SetupSolve(rCellPopulation,outputDirectory);

    // Copy the cell data to mSolution (this is the initial condition)
    SetupInitialSolutionVector(rCellPopulation);

    // Output the initial conditions on FeMesh
    this->UpdateAtEndOfOutputTimeStep(rCellPopulation);
}

// Here, we implement periodic boundary conditions.
template<unsigned DIM>
std::shared_ptr<BoundaryConditionsContainer<DIM,DIM,1> > ParabolicBoxDomainPdeModifierPeriodicBC<DIM>::ConstructBoundaryConditionsContainer(AbstractCellPopulation<DIM,DIM>& rCellPopulation)
{
    std::shared_ptr<BoundaryConditionsContainer<DIM,DIM,1> > p_bcc(new BoundaryConditionsContainer<DIM,DIM,1>(false));

    if (!this->mSetBcsOnBoxBoundary)
    {
        EXCEPTION("Boundary conditions cannot yet be set on the cell population boundary for a ParabolicBoxDomainPdeModifierPeriodicBC");
    }
    else // Apply BC at boundary nodes of box domain FE mesh
    {
        ChastePoint<DIM> upper = this->mpMeshCuboid->rGetUpperCorner();
        ChastePoint<DIM> lower = this->mpMeshCuboid->rGetLowerCorner();
        double x0 = lower[0], y0 = lower[1], xL = upper[0], yL = upper[1]; 
        double width = xL-x0, height = yL-y0;

        // impose periodicity  
        for (typename TetrahedralMesh<DIM,DIM>::BoundaryNodeIterator node_iter = this->mpFeMesh->GetBoundaryNodeIteratorBegin();
                 node_iter != this->mpFeMesh->GetBoundaryNodeIteratorEnd();
                 ++node_iter)
        {
            Node<DIM>* p_node = *node_iter; //Get pointer to the current node from the iterator
            double x = p_node->rGetLocation()[0];
            double y = p_node->rGetLocation()[1];
            // left and right boundaries
            if (fabs(x) < 1e-6)
            {
                for (typename TetrahedralMesh<DIM,DIM>::BoundaryNodeIterator node_iter2 = this->mpFeMesh->GetBoundaryNodeIteratorBegin();
                 node_iter2 != this->mpFeMesh->GetBoundaryNodeIteratorEnd();
                 ++node_iter2)
                {
                    Node<DIM>* p_node2 = *node_iter2; //Get pointer to the current node from the iterator
                    double x2 = p_node2->rGetLocation()[0];
                    double y2= p_node2->rGetLocation()[1];
                    if ((fabs(x2-width)<1e-6) && (fabs(y-y2)<1e-6))
                    {
                        p_bcc->AddPeriodicBoundaryCondition(p_node, p_node2);
                    }   
                }
            }
            // top and bottom boundaries
            if (fabs(y) < 1e-6)
            {
                for (typename TetrahedralMesh<DIM,DIM>::BoundaryNodeIterator node_iter2 = this->mpFeMesh->GetBoundaryNodeIteratorBegin();
                 node_iter2 != this->mpFeMesh->GetBoundaryNodeIteratorEnd();
                 ++node_iter2)
                {
                    Node<DIM>* p_node2 = *node_iter2; //Get pointer to the current node from the iterator
                    double x2 = p_node2->rGetLocation()[0];
                    double y2= p_node2->rGetLocation()[1];
                    if ((fabs(x-x2)<1e-6) && (fabs(y2-height)<1e-6))
                    {
                        p_bcc->AddPeriodicBoundaryCondition(p_node, p_node2);
                    }   
                }
            }
        }
    }
    return p_bcc;
}

template<unsigned DIM>
void ParabolicBoxDomainPdeModifierPeriodicBC<DIM>::SetupInitialSolutionVector(AbstractCellPopulation<DIM,DIM>& rCellPopulation)
{
    // Specify homogeneous initial conditions based upon the values stored in CellData.
    // Note need all the CellDataValues to be the same.

    double initial_condition = rCellPopulation.Begin()->GetCellData()->GetItem(this->mDependentVariableName);

    for (typename AbstractCellPopulation<DIM>::Iterator cell_iter = rCellPopulation.Begin();
         cell_iter != rCellPopulation.End();
         ++cell_iter)
    {
        double initial_condition_at_cell = cell_iter->GetCellData()->GetItem(this->mDependentVariableName);
        UNUSED_OPT(initial_condition_at_cell);
        assert(fabs(initial_condition_at_cell - initial_condition)<1e-12);
    }

    // Initialise mSolution
    this->mSolution = PetscTools::CreateAndSetVec(this->mpFeMesh->GetNumNodes(), initial_condition);
}

template<unsigned DIM>
void ParabolicBoxDomainPdeModifierPeriodicBC<DIM>::OutputSimulationModifierParameters(out_stream& rParamsFile)
{
    // No parameters to output, so just call method on direct parent class
    AbstractBoxDomainPdeModifier<DIM>::OutputSimulationModifierParameters(rParamsFile);
}

// Explicit instantiation
template class ParabolicBoxDomainPdeModifierPeriodicBC<1>;
template class ParabolicBoxDomainPdeModifierPeriodicBC<2>;
template class ParabolicBoxDomainPdeModifierPeriodicBC<3>;

