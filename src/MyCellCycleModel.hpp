#ifndef MYCELLCYCLEMODEL_HPP_
#define MYCELLCYCLEMODEL_HPP_

#include "AbstractSimpleCellCycleModel.hpp"
#include "RandomNumberGenerator.hpp"

/**
 * A stochastic cell-cycle model where cells divide with a stochastic cell cycle duration
 * with the length of the cell cycle drawn from an Inverse Gaussian (Wald) distribution
 *
 * If the cell is differentiated, then the cell cycle duration is set to be infinite,
 * so that the cell will never divide.
 */
class MyCellCycleModel : public AbstractSimpleCellCycleModel
{
// I use here Inverse Gaussian or Wald distribution. It has two parameters, mu and lambda.
private:

    /** The mu parameter of the Wald distribution. */
    double mMu;

    /** The lambda parameter of the Wald distribution. */
    double mLambda;

protected:

    /**
     * Protected copy-constructor for use by CreateCellCycleModel().
     *
     * The only way for external code to create a copy of a cell cycle model
     * is by calling that method, to ensure that a model of the correct subclass is created.
     * This copy-constructor helps subclasses to ensure that all member variables are correctly copied when this happens.
     *
     * This method is called by child classes to set member variables for a daughter cell upon cell division.
     * Note that the parent cell cycle model will have had ResetForDivision() called just before CreateCellCycleModel() is called,
     * so performing an exact copy of the parent is suitable behaviour. Any daughter-cell-specific initialisation
     * can be done in InitialiseDaughterCell().
     *
     * @param rModel the cell cycle model to copy.
     */
    MyCellCycleModel(const MyCellCycleModel& rModel);

public:

    /**
     * Constructor - just a default, mBirthTime is set in the AbstractCellCycleModel class.
     */
    MyCellCycleModel();

    /**
     * Overridden SetCellCycleDuration() method to add stochastic cell cycle times
     */
    void SetCellCycleDuration();

    /**
     * Overridden builder method to create new copies of
     * this cell-cycle model.
     *
     * @return new cell-cycle model
     */
    AbstractCellCycleModel* CreateCellCycleModel();

     /**
     * Set mMu.
     *
     * @param mu the value of the mu parameter
     */
    void SetMu(double mu);

    /**
     * @return mLambda.
     *
     * @param lambda the value of the lambda parameter
     */
    void SetLambda(double lambda);

    /**
     * @return mMu.
     */
    double GetMu() const;

    /**
     * @return mLambda.
     */
    double GetLambda() const;

    /**
     * Overridden GetAverageTransitCellCycleTime() method.
     *
     * @return the average of cell cycle duration given the params
     */
    double GetAverageTransitCellCycleTime();

    /**
     * Overridden GetAverageStemCellCycleTime() method.
     *
     * @return the same
     */
    double GetAverageStemCellCycleTime();

    /**
     * Overridden OutputCellCycleModelParameters() method.
     *
     * @param rParamsFile the file stream to which the parameters are output
     */
    virtual void OutputCellCycleModelParameters(out_stream& rParamsFile);
};


#endif /*MYCELLCYCLEMODEL_HPP_*/

