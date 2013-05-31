'''
Abstract classes for solver specific implementations.

@author: Daniel Machado

   Copyright 2013 Novo Nordisk Foundation Center for Biosustainability,
   Technical University of Denmark.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
   
'''

#CONSTANTS
class Status:
    """ Enumeration of possible solution status. """
    OPTIMAL = 1
    UNKNOWN = 0
    UNBOUNDED = -1
    UNFEASIBLE = -2


class Solution:
    """ Stores the results of an optimization.
    Invoke without arguments to create an empty Solution representing a failed optimization.
    """ 
    
    def __init__(self, status=Status.UNKNOWN, fobj=None, values=None, shadow_prices=None, reduced_costs=None):
        self.status = status
        self.fobj = fobj
        self.values = values
        self.shadow_prices = shadow_prices
        self.reduced_costs = reduced_costs


class Solver:
    """ Abstract class representing a generic solver.
    All solver interfaces should implement the basic methods.
    """
    
    def __init__(self):
        self.problem = None

    def build_problem(self, model):
        """ Create and store solver-specific internal structure for the given model.
        
        Arguments:
            model : ConstraintBasedModel
        """
        pass
        
    def solve_lp(self, objective, model=None, constraints=None, get_shadow_prices=False, get_reduced_costs=False):
        """ Solve an LP optimization problem.
        
        Arguments:
            objective : dict (of str to float) -- reaction ids in the objective function and respective
                        coefficients, the sense is maximization by default
            model : ConstraintBasedModel -- model (optional, leave blank to reuse previous model structure)
            constraints : dict (of str to (float, float)) -- environmental or additional constraints (optional)
            get_shadow_prices : bool -- return shadow price information if available (optional, default: False)
            get_reduced_costs : bool -- return reduced costs information if available (optional, default: False)
            
        Returns:
            Solution
        """
        
        # An exception is raised if the subclass does not implement this method.
        raise Exception('Not implemented for this solver.')
    
    def solve_qp(self, quad_obj, lin_obj, model=None, constraints=None, get_shadow_prices=False, get_reduced_costs=False):
        """ Solve an LP optimization problem.
        
        Arguments:
            quad_obj : dict (of (str, str) to float) -- map reaction pairs to respective coefficients
            lin_obj : dict (of str to float) -- map single reaction ids to respective linear coefficients
            model : ConstraintBasedModel -- model (optional, leave blank to reuse previous model structure)
            constraints : dict (of str to (float, float)) -- overriding constraints (optional)
            get_shadow_prices : bool -- return shadow price information if available (default: False)
            get_reduced_costs : bool -- return reduced costs information if available (default: False)
        
        Returns:
            Solution
        """

        # An exception is raised if the subclass does not implement this method.
        raise Exception('Not implemented for this solver.')    