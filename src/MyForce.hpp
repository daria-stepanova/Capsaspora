
#ifndef MYFORCE_HPP_
#define MYFORCE_HPP_

#include "AbstractTwoBodyInteractionForce.hpp"


/**
 * Force corresponding to Morse's potential
 */
template<unsigned  ELEMENT_DIM, unsigned SPACE_DIM=ELEMENT_DIM>
class MyForce : public AbstractTwoBodyInteractionForce<ELEMENT_DIM, SPACE_DIM>
{

protected:

    /**
     *  stiffness parameter; controls the depth of the well
     */
    double mStiffness;

    /**
     * controls the 'width' of the potential (the smaller is, the larger the well)
     */

    double mDelta;

    /**
     * Initial resting spring length after cell division.
     * Has units of cell size at equilibrium rest length
     *
     * The value of this parameter should be larger than mDivisionSeparation,
     * because of pressure from neighbouring springs.
     */
    double mDivisionRestingLength;

    /**
     * The time it takes for the springs rest length to increase from
     * mDivisionRestingLength to its natural length.
     *
     * The value of this parameter is usually the same as the M Phase of the cell cycle and defaults to 1.
     */
    double mGrowthDuration;

    // params for the non-linear Hill response to FBS
    double m_n0;
    double m_f0; 
    double m_mu0;
    int m_response_type;

public:

    /**
     * Constructor.
     */
    MyForce();

    /**
     * Destructor.
     */
    virtual ~MyForce();

    /**
     * Return a multiplication factor for the spring constant, which
     * returns a default value of 1.
     *
     * This method may be overridden in subclasses.
     *
     * @param nodeAGlobalIndex index of one neighbouring node
     * @param nodeBGlobalIndex index of the other neighbouring node
     * @param rCellPopulation the cell population
     * @param isCloserThanRestLength whether the neighbouring nodes lie closer than the rest length of their connecting spring
     *
     * @return the multiplication factor.
     */
    virtual double VariableSpringConstantMultiplicationFactor(unsigned nodeAGlobalIndex,
                                                              unsigned nodeBGlobalIndex,
                                                              AbstractCellPopulation<ELEMENT_DIM,SPACE_DIM>& rCellPopulation,
                                                              bool isCloserThanRestLength);

    /**
     * Overridden CalculateForceBetweenNodes() method.
     *
     * Calculates the force between two nodes.
     *
     * Note that this assumes they are connected and is called by AddForceContribution()
     *
     * @param nodeAGlobalIndex index of one neighbouring node
     * @param nodeBGlobalIndex index of the other neighbouring node
     * @param rCellPopulation the cell population
     * @return The force exerted on Node A by Node B.
     */
    c_vector<double, SPACE_DIM> CalculateForceBetweenNodes(unsigned nodeAGlobalIndex,
                                                     unsigned nodeBGlobalIndex,
                                                     AbstractCellPopulation<ELEMENT_DIM,SPACE_DIM>& rCellPopulation);
    /**
     * @return mStiffness
     */
    double GetStiffness();

    /**
     * @return mDivisionRestingLength
     */
    double GetDivisionRestingLength();

    /**
     * @return mGrowthDuration
     */
    double GetGrowthDuration();

    /**
     * Set mMeinekeSpringStiffness.
     *
     * @param myStiffness the new value of mStiffness
     */
    void SetStiffness(double myStiffness);

    /**
     * Set mDivisionRestingLength.
     *
     * @param divisionRestingLength the new value of mDivisionRestingLength
     */
    void SetDivisionRestingLength(double divisionRestingLength);

    /**
     * Set mGrowthDuration.
     *
     * @param growthDuration the new value of mGrowthDuration
     */
    void SetGrowthDuration(double growthDuration);

    /**
     * Set mDelta.
     *
     * @param myDelta the new value of mDelta
     */
    void SetDelta(double myDelta);

    void SetNonLinearResponse(double n0, double f0, double mu0, int response_type);

    /**
     * Overridden OutputForceParameters() method.
     *
     * @param rParamsFile the file stream to which the parameters are output
     */
    virtual void OutputForceParameters(out_stream& rParamsFile);
};

#endif /*MYFORCE_HPP_*/
