#include <iostream>
#include <string>

#include "ExecutableSupport.hpp"
#include "Exception.hpp"
#include "PetscTools.hpp"
#include "PetscException.hpp"


#include <cxxtest/TestSuite.h>

#include "AbstractCellBasedTestSuite.hpp"
#include "Debug.hpp"
#include "LogFile.hpp"
#include "ExecutableSupport.hpp" 
#include "CapsasporaSimulation.hpp"


/*
 * Prototype functions
 */
int main(int argc, char *argv[])
{
    ExecutableSupport::StandardStartup(&argc, &argv);

    int exit_code = ExecutableSupport::EXIT_OK;

    // You should put all the main code within a try-catch, to ensure that
    // you clean up PETSc before quitting.
    try
    {
        CapsasporaSimulation sim = CapsasporaSimulation();
        sim.TestCapsasporaSimulation();

        return ExecutableSupport::EXIT_OK;
    }
    catch (const Exception &e)
    {
        ExecutableSupport::PrintError(e.GetMessage());
        exit_code = ExecutableSupport::EXIT_ERROR;
    }

    // Optional - write the machine info to file.
    ExecutableSupport::WriteMachineInfoFile("machine_info");

    // End by finalizing PETSc, and returning a suitable exit code.
    // 0 means 'no error'
    ExecutableSupport::FinalizePetsc();
    return exit_code;
}
