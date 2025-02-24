#include "MyDiffusionForce.hpp"
#include "NodeBasedCellPopulation.hpp"

template<unsigned DIM>
MyDiffusionForce<DIM>::MyDiffusionForce()
    : AbstractForce<DIM>(),
      mDiff(16.866) // default cell motility in 0% FBS
{
}

template<unsigned DIM>
MyDiffusionForce<DIM>::~MyDiffusionForce()
{
}

template<unsigned DIM>
void MyDiffusionForce<DIM>::SetDiffusionConstant(double diffusionConstant)
{
    assert(diffusionConstant >= 0.0);
    mDiff = diffusionConstant;
}


template<unsigned DIM>
double MyDiffusionForce<DIM>::GetDiffusionConstant()
{

    return mDiff;
}

template<unsigned DIM>
double MyDiffusionForce<DIM>::GetDiffusionConstant(unsigned nodeIndex,  AbstractCellPopulation<DIM>& rCellPopulation)
{
    double fbs_conv = 5.0;      // conversion factor from normalised FBS used in simulations to real value (%)
    CellPtr p_cell = rCellPopulation.GetCellUsingLocationIndex(nodeIndex);
    double local_fbs =  p_cell->GetCellData()->GetItem("fbs");

    double local_motility_const = 0.0;

    // in the values below, space dimensions have been scaled with cell size (3 um)
    if(local_fbs*fbs_conv>= 5.0)
        local_motility_const = 1.7761*60;   // the value in 1/min from the manuscript is converted to 1/hour
    else
        local_motility_const = 60.0*(0.299*local_fbs*fbs_conv + 0.2811);

    SetDiffusionConstant(local_motility_const);

    return local_motility_const;
}

template<unsigned DIM>
void MyDiffusionForce<DIM>::AddForceContribution(AbstractCellPopulation<DIM>& rCellPopulation)
{
    double dt = SimulationTime::Instance()->GetTimeStep();

    // Iterate over the nodes
    for (typename AbstractMesh<DIM, DIM>::NodeIterator node_iter = rCellPopulation.rGetMesh().GetNodeIteratorBegin();
         node_iter != rCellPopulation.rGetMesh().GetNodeIteratorEnd();
         ++node_iter)
    {
        // Get the index, radius and damping constant of this node
        unsigned node_index = node_iter->GetIndex();
        double node_radius = node_iter->GetRadius();

        // If the node radius is zero, then it has not been set...
        if (node_radius == 0.0)
        {
            // ...so throw an exception to avoid dividing by zero when we compute diffusion_constant below
            EXCEPTION("SetRadius() must be called on each Node before calling DiffusionForce::AddForceContribution() to avoid a division by zero error");
        }

        double nu = dynamic_cast<AbstractOffLatticeCellPopulation<DIM>*>(&rCellPopulation)->GetDampingConstant(node_index);

        double diffusion_constant = GetDiffusionConstant(node_index,rCellPopulation);

        c_vector<double, DIM> force_contribution;
        for (unsigned i=0; i<DIM; i++)
        {
            /*
             * The force on this cell is scaled with the timestep such that when it is
             * used in the discretised equation of motion for the cell, we obtain the
             * correct formula
             *
             * x_new = x_old + sqrt(2*D*dt)*W
             *
             * where W is a standard normal random variable.
             */
            double xi = RandomNumberGenerator::Instance()->StandardNormalRandomDeviate();

            force_contribution[i] = (nu*sqrt(2.0*diffusion_constant*dt)/dt)*xi;
        }
        node_iter->AddAppliedForceContribution(force_contribution);
    }
}

template<unsigned DIM>
void MyDiffusionForce<DIM>::OutputForceParameters(out_stream& rParamsFile)
{
    *rParamsFile << "\t\t\t<DiffusionConstant>" << mDiff << "</DiffusionConstant> \n";

    // Call direct parent class
    AbstractForce<DIM>::OutputForceParameters(rParamsFile);
}

// Explicit instantiation
template class MyDiffusionForce<1>;
template class MyDiffusionForce<2>;
template class MyDiffusionForce<3>;
