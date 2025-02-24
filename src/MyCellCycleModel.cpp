
#include "MyCellCycleModel.hpp"
#include "StemCellProliferativeType.hpp"
#include "TransitCellProliferativeType.hpp"
#include "DifferentiatedCellProliferativeType.hpp"


MyCellCycleModel::MyCellCycleModel()
    : AbstractSimpleCellCycleModel(),
      mMu(DOUBLE_UNSET), // Hours
      mLambda(DOUBLE_UNSET)  // Hours
{
}

MyCellCycleModel::MyCellCycleModel(const MyCellCycleModel& rModel)
   :  AbstractSimpleCellCycleModel(rModel),
      mMu(rModel.mMu),
      mLambda(rModel.mLambda)
{
    /*
     * Initialize only those member variables defined in this class.
     *
     * The member variables mCurrentCellCyclePhase, mG1Duration,
     * mMinimumGapDuration, mStemCellG1Duration, mTransitCellG1Duration,
     * mSDuration, mG2Duration and mMDuration are initialized in the
     * AbstractPhaseBasedCellCycleModel constructor.
     *
     * The member variables mBirthTime, mReadyToDivide and mDimension
     * are initialized in the AbstractCellCycleModel constructor.
     *
     * Note that mG1Duration is (re)set as soon as InitialiseDaughterCell()
     * is called on the new cell-cycle model.
     */
}

AbstractCellCycleModel* MyCellCycleModel::CreateCellCycleModel()
{
    return new MyCellCycleModel(*this);
}

void MyCellCycleModel::SetCellCycleDuration()
{
    RandomNumberGenerator* p_gen = RandomNumberGenerator::Instance();

    if (mpCell->GetCellProliferativeType()->IsType<StemCellProliferativeType>()
        || mpCell->GetCellProliferativeType()->IsType<TransitCellProliferativeType>() )
    {
        // Generate a random number from the Inverse Gaussian (Wald) distribution for quantity (12 h - [cell cycle duration])

        double nu = p_gen->StandardNormalRandomDeviate(), z = p_gen->ranf();
        double x = mMu+mMu*0.5/mLambda*nu*(mMu*nu - sqrt(4*mMu*mLambda+ mMu*mMu*nu*nu));
        (z<=mMu/(mMu+x))?(mCellCycleDuration=x):(mCellCycleDuration = mMu*mMu/x);

        // Now, we transform mCellCycleDuration back to the original value (before the shift by 12 h)
        mCellCycleDuration = 12.0 - mCellCycleDuration;
    }
    else if (mpCell->GetCellProliferativeType()->IsType<DifferentiatedCellProliferativeType>())
    {
        mCellCycleDuration = DBL_MAX;
    }
    else
    {
        NEVER_REACHED;
    }
}

void MyCellCycleModel::SetMu(double mu)
{
    mMu = mu;
}

void MyCellCycleModel::SetLambda(double lambda)
{
    mLambda = lambda;
}

double MyCellCycleModel::GetMu() const
{
    return mMu;
}

double MyCellCycleModel::GetLambda() const
{
    return mLambda;
}

double MyCellCycleModel::GetAverageTransitCellCycleTime()
{
    return mMu;
}

double MyCellCycleModel::GetAverageStemCellCycleTime()
{
    return mMu;
}


void MyCellCycleModel::OutputCellCycleModelParameters(out_stream& rParamsFile)
{
    *rParamsFile << "\t\t\t<Mu>" << mMu << "</Mu>\n";
    *rParamsFile << "\t\t\t<Lambda>" << mLambda << "</Lambda>\n";

    AbstractSimpleCellCycleModel::OutputCellCycleModelParameters(rParamsFile);
}


