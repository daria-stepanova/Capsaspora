
#include "MyForce.hpp"
#include "OutputFileHandler.hpp"

template<unsigned ELEMENT_DIM, unsigned SPACE_DIM>
MyForce<ELEMENT_DIM,SPACE_DIM>::MyForce()
   : AbstractTwoBodyInteractionForce<ELEMENT_DIM,SPACE_DIM>(),
     mStiffness(10.0),  
     mDelta(5.0),      
     mDivisionRestingLength(0.5),
     mGrowthDuration(2.0),
     m_n0(0.0),
     m_f0(0.0),
     m_mu0(mStiffness),
     m_response_type(1)
{
    if (SPACE_DIM == 1)
    {
        mStiffness = 30.0;
    }
}

template<unsigned ELEMENT_DIM, unsigned SPACE_DIM>
double MyForce<ELEMENT_DIM,SPACE_DIM>::VariableSpringConstantMultiplicationFactor(unsigned nodeAGlobalIndex,
                                                                                     unsigned nodeBGlobalIndex,
                                                                                     AbstractCellPopulation<ELEMENT_DIM,SPACE_DIM>& rCellPopulation,
                                                                                     bool isCloserThanRestLength)
{
    return 1.0;
}

template<unsigned ELEMENT_DIM, unsigned SPACE_DIM>
MyForce<ELEMENT_DIM,SPACE_DIM>::~MyForce()
{
}

template<unsigned ELEMENT_DIM, unsigned SPACE_DIM>
c_vector<double, SPACE_DIM> MyForce<ELEMENT_DIM,SPACE_DIM>::CalculateForceBetweenNodes(unsigned nodeAGlobalIndex,
                                                                                    unsigned nodeBGlobalIndex,
                                                                                    AbstractCellPopulation<ELEMENT_DIM,SPACE_DIM>& rCellPopulation)
{
    // We should only ever calculate the force between two distinct nodes
    assert(nodeAGlobalIndex != nodeBGlobalIndex);

    Node<SPACE_DIM>* p_node_a = rCellPopulation.GetNode(nodeAGlobalIndex);
    Node<SPACE_DIM>* p_node_b = rCellPopulation.GetNode(nodeBGlobalIndex);

    // Get the node locations
    const c_vector<double, SPACE_DIM>& r_node_a_location = p_node_a->rGetLocation();
    const c_vector<double, SPACE_DIM>& r_node_b_location = p_node_b->rGetLocation();

    // Get the node radii for a NodeBasedCellPopulation
    double node_a_radius = 0.0;
    double node_b_radius = 0.0;

    double radius_correction = 1.0;

    if (bool(dynamic_cast<NodeBasedCellPopulation<SPACE_DIM>*>(&rCellPopulation)))
    {
        node_a_radius = radius_correction*(p_node_a->GetRadius());
        node_b_radius = radius_correction*(p_node_b->GetRadius());
    }

    // Get the unit vector parallel to the line joining the two nodes
    c_vector<double, SPACE_DIM> unit_difference;
    /*
     * We use the mesh method GetVectorFromAtoB() to compute the direction of the
     * unit vector along the line joining the two nodes, rather than simply subtract
     * their positions, because this method can be overloaded (e.g. to enforce a
     * periodic boundary in Cylindrical2dMesh).
     */
    unit_difference = rCellPopulation.rGetMesh().GetVectorFromAtoB(r_node_a_location, r_node_b_location);


    // Calculate the distance between the two nodes
    double distance_between_nodes = norm_2(unit_difference);
    
    if(distance_between_nodes==0.0)
        distance_between_nodes = -1;
    assert(distance_between_nodes > 0);

    assert(!std::isnan(distance_between_nodes));

    unit_difference /= distance_between_nodes;

    /*
     * If mUseCutOffLength has been set, then there is zero force between
     * two nodes located a distance apart greater than mMechanicsCutOffLength in AbstractTwoBodyInteractionForce.
     */
    if (this->mUseCutOffLength)
    {
        if (distance_between_nodes >= this->GetCutOffLength())
        {
            return zero_vector<double>(SPACE_DIM); // c_vector<double,SPACE_DIM>() is not guaranteed to be fresh memory
        }
    }

    /*
     * Calculate the rest length of the spring connecting the two nodes with a default
     * value of 1.0.
     */
    double rest_length_final = 1.0;

    if (bool(dynamic_cast<MeshBasedCellPopulation<ELEMENT_DIM,SPACE_DIM>*>(&rCellPopulation)))
    {
        rest_length_final = static_cast<MeshBasedCellPopulation<ELEMENT_DIM,SPACE_DIM>*>(&rCellPopulation)->GetRestLength(nodeAGlobalIndex, nodeBGlobalIndex);
    }
    else if (bool(dynamic_cast<NodeBasedCellPopulation<SPACE_DIM>*>(&rCellPopulation)))
    {
        assert(node_a_radius > 0 && node_b_radius > 0);
        rest_length_final = node_a_radius+node_b_radius;
    }

    double rest_length = rest_length_final;

    CellPtr p_cell_A = rCellPopulation.GetCellUsingLocationIndex(nodeAGlobalIndex);
    CellPtr p_cell_B = rCellPopulation.GetCellUsingLocationIndex(nodeBGlobalIndex);

    double ageA = p_cell_A->GetAge();
    double ageB = p_cell_B->GetAge();

    assert(!std::isnan(ageA));
    assert(!std::isnan(ageB));

    /*
     * If the cells are both newly divided, then the rest length of the spring
     * connecting them grows linearly with time, until 2 hours after division.
     */
    if (ageA < mGrowthDuration && ageB < mGrowthDuration)
    {
        AbstractCentreBasedCellPopulation<ELEMENT_DIM,SPACE_DIM>* p_static_cast_cell_population = static_cast<AbstractCentreBasedCellPopulation<ELEMENT_DIM,SPACE_DIM>*>(&rCellPopulation);

        std::pair<CellPtr,CellPtr> cell_pair = p_static_cast_cell_population->CreateCellPair(p_cell_A, p_cell_B);

        if (p_static_cast_cell_population->IsMarkedSpring(cell_pair))
        {
            // Spring rest length increases from a small value to the normal rest length over 1 hour
            double lambda = mDivisionRestingLength;
            rest_length = lambda + (rest_length_final - lambda) * ageA/mGrowthDuration;
        }
        if (ageA + SimulationTime::Instance()->GetTimeStep() >= mGrowthDuration)
        {
            // This spring is about to go out of scope
            p_static_cast_cell_population->UnmarkSpring(cell_pair);
        }
    }

    /*
     * For apoptosis, progressively reduce the radius of the cell
     */
    double a_rest_length = rest_length*0.5;
    double b_rest_length = a_rest_length;

    if (bool(dynamic_cast<NodeBasedCellPopulation<SPACE_DIM>*>(&rCellPopulation)))
    {
        assert(node_a_radius > 0 && node_b_radius > 0);
        a_rest_length = (node_a_radius/(node_a_radius+node_b_radius))*rest_length;
        b_rest_length = (node_b_radius/(node_a_radius+node_b_radius))*rest_length;
    }

    /*
     * If either of the cells has begun apoptosis, then the length of the spring
     * connecting them decreases linearly with time.
     */
    if (p_cell_A->HasApoptosisBegun())
    {
        double time_until_death_a = p_cell_A->GetTimeUntilDeath();
        a_rest_length = a_rest_length * time_until_death_a / p_cell_A->GetApoptosisTime();
    }
    if (p_cell_B->HasApoptosisBegun())
    {
        double time_until_death_b = p_cell_B->GetTimeUntilDeath();
        b_rest_length = b_rest_length * time_until_death_b / p_cell_B->GetApoptosisTime();
    }

    rest_length = a_rest_length + b_rest_length;

    // Although in this class the 'spring constant' is a constant parameter, in
    // subclasses it can depend on properties of each of the cells
    double overlap = distance_between_nodes - rest_length;
    bool is_closer_than_rest_length = (overlap <= 0);
    double multiplication_factor = VariableSpringConstantMultiplicationFactor(nodeAGlobalIndex, nodeBGlobalIndex, rCellPopulation, is_closer_than_rest_length);
    double spring_stiffness = mStiffness;

    double fbs_local = 0.5*(p_cell_A->GetCellData()->GetItem("fbs")+p_cell_B->GetCellData()->GetItem("fbs"));

    double fbs_conv = 5.0;
    if(m_response_type==1)    //Hill fitting
    {
        if(fbs_local*fbs_conv<0.001) //5 is the conversion factor from nondim to dim values
        {
            spring_stiffness=0.0;
        }
        else
        {
            spring_stiffness = m_mu0/(1+pow(m_f0/(fbs_local*fbs_conv),m_n0));
        }
    }
    else                          // linear (shallow or steep)
    {
        spring_stiffness = fbs_local*m_mu0*fbs_conv;
    }

    if (bool(dynamic_cast<MeshBasedCellPopulation<ELEMENT_DIM,SPACE_DIM>*>(&rCellPopulation)))
    {
        return multiplication_factor * spring_stiffness * unit_difference * overlap;
    }
    else
    {
        double my_delta = mDelta;
        // If cells are too close to each other (i.e. the overlap value<0), then we have short-range repulsion.
        if(overlap<0.0)
        {    
            my_delta = 2.0;     // high value of delta to impose repulsion when aggregated
            spring_stiffness = mStiffness; 
        }
        // otherwise, we enter into the regime of longer-range cell adhesion (has been defined above).

        // Now, we put it into the expression for the Morse force.
        c_vector<double, SPACE_DIM> temp = multiplication_factor * spring_stiffness * unit_difference * ( exp(- my_delta* overlap) - exp(- 2.0*my_delta* overlap) );

        return temp;
    }
}

template<unsigned ELEMENT_DIM, unsigned SPACE_DIM>
double MyForce<ELEMENT_DIM,SPACE_DIM>::GetStiffness()
{
    return mStiffness;
}

template<unsigned ELEMENT_DIM, unsigned SPACE_DIM>
double MyForce<ELEMENT_DIM,SPACE_DIM>::GetDivisionRestingLength()
{
    return mDivisionRestingLength;
}

template<unsigned ELEMENT_DIM, unsigned SPACE_DIM>
double MyForce<ELEMENT_DIM,SPACE_DIM>::GetGrowthDuration()
{
    return mGrowthDuration;
}

template<unsigned ELEMENT_DIM, unsigned SPACE_DIM>
void MyForce<ELEMENT_DIM,SPACE_DIM>::SetStiffness(double myStiffness)
{
    assert(myStiffness > 0.0);
    mStiffness = myStiffness;
}

template<unsigned ELEMENT_DIM, unsigned SPACE_DIM>
void MyForce<ELEMENT_DIM,SPACE_DIM>::SetDivisionRestingLength(double divisionRestingLength)
{
    assert(divisionRestingLength <= 1.0);
    assert(divisionRestingLength >= 0.0);

    mDivisionRestingLength = divisionRestingLength;
}

template<unsigned ELEMENT_DIM, unsigned SPACE_DIM>
void MyForce<ELEMENT_DIM,SPACE_DIM>::SetGrowthDuration(double growthDuration)
{
    assert(growthDuration >= 0.0);

    mGrowthDuration = growthDuration;
}

template<unsigned ELEMENT_DIM, unsigned SPACE_DIM>
void MyForce<ELEMENT_DIM,SPACE_DIM>::SetDelta(double myDelta)
{
    assert(myDelta >= 0.0);

    mDelta = myDelta;
}

template<unsigned ELEMENT_DIM, unsigned SPACE_DIM>
void MyForce<ELEMENT_DIM,SPACE_DIM>::SetNonLinearResponse(double n0, double f0, double mu0, int response_type)
{
    if(response_type==1)            //  Hill
    {
        m_mu0 = mu0;
        m_n0 = n0;
        m_f0 = f0;
        m_response_type = 1;
    }
    else if(response_type==2)       //  linear (shallow)
    {
        m_mu0 = mu0;
        m_n0 = 0.0;
        m_f0 = 0.0;
        m_response_type = 2; 
    }
    else                            // linear (steep)
    {
        m_mu0 = mu0;
        m_n0 = 0.0;
        m_f0 = 0.0;
        m_response_type = 0; 
    }
}

template<unsigned ELEMENT_DIM, unsigned SPACE_DIM>
void MyForce<ELEMENT_DIM,SPACE_DIM>::OutputForceParameters(out_stream& rParamsFile)
{
    *rParamsFile << "\t\t\t<MyStiffness>" << mStiffness << "</MyStiffness>\n";
    *rParamsFile << "\t\t\t<MyDelta>" << mDelta << "</MyDelta>\n";
    *rParamsFile << "\t\t\t<MyDivisionRestingLength>" << mDivisionRestingLength << "</MyDivisionRestingLength>\n";
    *rParamsFile << "\t\t\t<MyGrowthDuration>" << mGrowthDuration << "</MyGrowthDuration>\n";

    // Call method on direct parent class
    AbstractTwoBodyInteractionForce<ELEMENT_DIM,SPACE_DIM>::OutputForceParameters(rParamsFile);
}

// Explicit instantiation
template class MyForce<1,1>;
template class MyForce<1,2>;
template class MyForce<2,2>;
template class MyForce<1,3>;
template class MyForce<2,3>;
template class MyForce<3,3>;


