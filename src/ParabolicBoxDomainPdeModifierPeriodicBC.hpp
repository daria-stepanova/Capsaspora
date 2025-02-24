#ifndef PARABOLICBOXDOMAINPDEMODIFIERPERIODICBC_HPP_
#define PARABOLICBOXDOMAINPDEMODIFIERPERIODICBC_HPP_

//#include "AbstractBoxDomainPdeModifier.hpp"
#include "ParabolicBoxDomainPdeModifier.hpp"
#include "BoundaryConditionsContainer.hpp"

/**
 * A modifier class in which a linear parabolic PDE coupled to a cell-based simulation
 * is solved on a coarse domain with periodic boundary conditions in x and y.
 *
 * The finite element mesh used to solve the PDE numerically is a fixed tessellation of
 * a cuboid (box), which must be supplied to the constructor. The value of the dependent
 * variable is interpolated between coarse mesh nodes to obtain a value at each cell,
 * which is stored and updated in a CellData item.
 *
 * At each time step the boundary condition supplied to the constructor may be imposed
 * either on the boundary of the box domain, or on the boundary of the cell population
 * (which is assumed to lie within the box domain). This choice can be made using the
 * AbstractBoxDomainPdeModifier method SetBcsOnBoxBoundary(), which is inherited by this
 * class.
 *
 * Examples of PDEs in the source folder that can be solved using this class are
 * AveragedSourceParabolicPde and UniformSourceParabolicPde.
 */
template<unsigned DIM>
class ParabolicBoxDomainPdeModifierPeriodicBC : public ParabolicBoxDomainPdeModifier<DIM>
{

private:

public:

    /**
     * Constructor.
     *
     * @param pPde A shared pointer to a linear PDE object (defaults to NULL)
     * @param pBoundaryCondition A shared pointer to an abstract boundary condition
     *     (defaults to NULL, corresponding to a constant boundary condition with value zero)
     * @param isNeumannBoundaryCondition Whether the boundary condition is Neumann (defaults to true)
     * @param pMeshCuboid A shared pointer to a ChasteCuboid specifying the outer boundary for the FE mesh (defaults to NULL)
     * @param stepSize step size to be used in the FE mesh (defaults to 1.0, i.e. the default cell size)
     * @param solution solution vector (defaults to NULL)
     */
    ParabolicBoxDomainPdeModifierPeriodicBC(boost::shared_ptr<AbstractLinearPde<DIM,DIM> > pPde=boost::shared_ptr<AbstractLinearPde<DIM,DIM> >(),
                                  boost::shared_ptr<AbstractBoundaryCondition<DIM> > pBoundaryCondition=boost::shared_ptr<AbstractBoundaryCondition<DIM> >(),
                                  bool isNeumannBoundaryCondition=true,
                                  boost::shared_ptr<ChasteCuboid<DIM> > pMeshCuboid=boost::shared_ptr<ChasteCuboid<DIM> >(),
                                  double stepSize=1.0,
                                  Vec solution=nullptr);

    /**
     * Destructor.
     */
    virtual ~ParabolicBoxDomainPdeModifierPeriodicBC();

    /**
     * Overridden UpdateAtEndOfTimeStep() method.
     *
     * Specifies what to do in the simulation at the end of each time step.
     *
     * @param rCellPopulation reference to the cell population
     */
    virtual void UpdateAtEndOfTimeStep(AbstractCellPopulation<DIM,DIM>& rCellPopulation);

    /**
     * Overridden SetupSolve() method.
     *
     * Specifies what to do in the simulation before the start of the time loop.
     *
     * @param rCellPopulation reference to the cell population
     * @param outputDirectory the output directory, relative to where Chaste output is stored
     */
    virtual void SetupSolve(AbstractCellPopulation<DIM,DIM>& rCellPopulation, std::string outputDirectory);

    /**
     * Helper method to construct the boundary conditions container for the PDE.
     *
     * @param rCellPopulation reference to the cell population
     *
     * @return the full boundary conditions container
     */
    virtual std::shared_ptr<BoundaryConditionsContainer<DIM,DIM,1> > ConstructBoundaryConditionsContainer(AbstractCellPopulation<DIM,DIM>& rCellPopulation);

    /**
     * Helper method to initialise the PDE solution using the CellData.
     *
     * Here we assume a homogeneous initial consition.
     *
     * @param rCellPopulation reference to the cell population
     */
    void SetupInitialSolutionVector(AbstractCellPopulation<DIM,DIM>& rCellPopulation);

    /**
     * Overridden OutputSimulationModifierParameters() method.
     * Output any simulation modifier parameters to file.
     *
     * @param rParamsFile the file stream to which the parameters are output
     */
    void OutputSimulationModifierParameters(out_stream& rParamsFile);
};

#endif /*PARABOLICBOXDOMAINPDEMODIFIERPERIODICBC_HPP_*/