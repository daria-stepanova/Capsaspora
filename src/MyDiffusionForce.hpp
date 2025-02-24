
#ifndef MYDIFFUSIONFORCE_HPP_
#define MyDIFFUSIONFORCE_HPP_

#include "AbstractForce.hpp"
#include "AbstractOffLatticeCellPopulation.hpp"
#include "RandomNumberGenerator.hpp"

/**
 * A 'diffusion force' class to model the random movement of nodes.
 *
 * This class works with all off-lattice cell populations.
 */
template<unsigned DIM>
class MyDiffusionForce : public AbstractForce<DIM>
{
private :

    /**
     * Diffusion constant
     */
    double mDiff;

public :

    /**
     * Constructor.
     */
    MyDiffusionForce();

    /**
     * Destructor.
     */
    ~MyDiffusionForce();

    /**
     * Set the diffusion constant.
     *
     * @param diffusionConstant [space unit]^2/[time unit]
     */
    void SetDiffusionConstant(double diffusionConstant);

    
    /**
     * Calculate the diffusion constant
     *
     * @return the scaled diffusion constant.
     */
    double GetDiffusionConstant();

    double GetDiffusionConstant(unsigned nodeIndex,  AbstractCellPopulation<DIM>& rCellPopulation);

    /**
     * Overridden AddForceContribution() method.
     * Note that this method requires cell/node radii to be set.
     *
     * @param rCellPopulation reference to the tissue
     */
    void AddForceContribution(AbstractCellPopulation<DIM>& rCellPopulation);

    /**
     * Overridden OutputForceParameters() method.
     *
     * @param rParamsFile the file stream to which the parameters are output
     */
    void OutputForceParameters(out_stream& rParamsFile);
};


#endif /*MYDIFFUSIONFORCE_HPP_*/