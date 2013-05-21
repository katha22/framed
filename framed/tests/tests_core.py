'''
Unit testing module.
'''
import unittest

from framed.io_utils.sbml import load_sbml_model, save_sbml_model, CONSTRAINT_BASED, GPR_CONSTRAINED
from framed.core.fixes import fix_bigg_model
from framed.analysis.simulation import FBA
from framed.analysis.variability import FVA
from framed.io_utils.plaintext import read_model_from_file, write_model_to_file
from framed.analysis.deletion import gene_deletion
from framed.analysis.essentiality import essential_genes
from framed.solvers.solver import Status
from framed.core.transformation import make_irreversible
from framed.design.combinatorial import combinatorial_gene_deletion

SMALL_TEST_MODEL = '../../misc/ecoli_core_model.xml'
TEST_MODEL_COPY = '../../misc/model_copy.xml'
PLAIN_TEXT_COPY = '../../misc/model_copy.txt'

GROWTH_RATE = 0.8739

DOUBLE_GENE_KO = ['b3731', 's0001']
DOUBLE_KO_GROWTH_RATE = 0.108
DOUBLE_KO_SUCC_EX = 3.8188

MOMA_GENE_KO = ['b0721']
MOMA_GROWTH_RATE = 0.5745
MOMA_SUCC_EX = 4.467

ESSENTIAL_GENES = ['b0720', 'b1136', 'b1779', 'b2415', 'b2416', 'b2779', 'b2926']


class SBMLTest(unittest.TestCase):
    """ Test SBML import and export. """
        
    def testRun(self):
        model = load_sbml_model(SMALL_TEST_MODEL, kind=GPR_CONSTRAINED)
        save_sbml_model(model, TEST_MODEL_COPY)
        model_copy = load_sbml_model(TEST_MODEL_COPY, kind=GPR_CONSTRAINED)
        self.assertEqual(model.id, model_copy.id)
        self.assertListEqual(model.metabolites.keys(), model_copy.metabolites.keys())
        self.assertListEqual(model.reactions.keys(), model_copy.reactions.keys())
        self.assertDictEqual(model.stoichiometry, model_copy.stoichiometry)
        self.assertDictEqual(model.bounds, model_copy.bounds)
        self.assertListEqual(model.genes.keys(), model_copy.genes.keys())
        self.assertDictEqual(model.rules, model_copy.rules)

class PlainTextIOTest(unittest.TestCase):
    """ Test plain text import and export. """
        
    def testRun(self):
        model = load_sbml_model(SMALL_TEST_MODEL, kind=CONSTRAINT_BASED)
        fix_bigg_model(model)
        write_model_to_file(model, PLAIN_TEXT_COPY)
        model_copy = read_model_from_file(PLAIN_TEXT_COPY, kind=CONSTRAINT_BASED)
        self.assertListEqual(sorted(model.metabolites.keys()),
                             sorted(model_copy.metabolites.keys()))
        self.assertListEqual(model.reactions.keys(), model_copy.reactions.keys())
        self.assertDictEqual(dict(model.stoichiometry),
                             dict(model_copy.stoichiometry))
        self.assertDictEqual(model.bounds, model_copy.bounds)
        
class FBATest(unittest.TestCase):
    """ Test FBA simulation. """
    
    def testRun(self):
        model = load_sbml_model(SMALL_TEST_MODEL, kind=CONSTRAINT_BASED)
        fix_bigg_model(model)
        solution = FBA(model, get_shadow_prices=True, get_reduced_costs=True)
        self.assertEqual(solution.status, Status.OPTIMAL)
        self.assertAlmostEqual(solution.fobj, GROWTH_RATE, places=2)

class FBATest2(unittest.TestCase):
    """ Test FBA simulation from plain text model. """
    
    def testRun(self):
        model = read_model_from_file(PLAIN_TEXT_COPY, kind=CONSTRAINT_BASED)
        solution = FBA(model)
        self.assertEqual(solution.status, Status.OPTIMAL)
        self.assertAlmostEqual(solution.fobj, GROWTH_RATE, places=2)

        
class FBATest3(unittest.TestCase):
    """ Test FBA simulation after reversible decomposition. """
    
    def testRun(self):
        model = load_sbml_model(SMALL_TEST_MODEL, kind=CONSTRAINT_BASED)
        fix_bigg_model(model)
        make_irreversible(model)
        self.assertTrue(all([not reaction.reversible for reaction in model.reactions.values()]))
        solution = FBA(model)
        self.assertEqual(solution.status, Status.OPTIMAL)
        self.assertAlmostEqual(solution.fobj, GROWTH_RATE, places=2)
        
                
class FVATest(unittest.TestCase):
    """ Test flux variability analysis """
    
    def testRun(self):
        model = load_sbml_model(SMALL_TEST_MODEL, kind=CONSTRAINT_BASED)
        fix_bigg_model(model)
        variability = FVA(model)        
        self.assertTrue(all([lb <= ub if lb is not None and ub is not None else True
                             for lb, ub in variability.values()]))


class GeneDeletionFBATest(unittest.TestCase):
    """ Test gene deletion with FBA. """
    
    def testRun(self):
        model = load_sbml_model(SMALL_TEST_MODEL, kind=GPR_CONSTRAINED)
        fix_bigg_model(model)
        solution = gene_deletion(model, DOUBLE_GENE_KO)
        self.assertEqual(solution.status, Status.OPTIMAL)
        self.assertAlmostEqual(solution.values[model.detect_biomass_reaction()], DOUBLE_KO_GROWTH_RATE, 3)
        self.assertAlmostEqual(solution.values['R_EX_succ_e'], DOUBLE_KO_SUCC_EX, 3)

class GeneDeletionMOMATest(unittest.TestCase):
    """ Test gene deletion with MOMA. """
    
    def testRun(self):
        model = load_sbml_model(SMALL_TEST_MODEL, kind=GPR_CONSTRAINED)
        fix_bigg_model(model)
        solution = gene_deletion(model, MOMA_GENE_KO, 'MOMA')
        self.assertEqual(solution.status, Status.OPTIMAL)
        self.assertAlmostEqual(solution.values[model.detect_biomass_reaction()], MOMA_GROWTH_RATE, 3)
        self.assertAlmostEqual(solution.values['R_EX_succ_e'], MOMA_SUCC_EX, 3)
                
class GeneEssentialityTest(unittest.TestCase):
    """ Test gene deletion with MOMA. """
    
    def testRun(self):
        model = load_sbml_model(SMALL_TEST_MODEL, kind=GPR_CONSTRAINED)
        fix_bigg_model(model)
        essential = essential_genes(model)
        self.assertListEqual(essential, ESSENTIAL_GENES)
        
class CombinatorialGeneDeletion(unittest.TestCase):
    """ Test combinatorial gene deletion with FBA. """
    
    def testRun(self):
        model = load_sbml_model(SMALL_TEST_MODEL, kind=GPR_CONSTRAINED)
        fix_bigg_model(model)
        objective = {'R_EX_succ_e': 1}
        max_dels = 2
        result = combinatorial_gene_deletion(model, objective, max_dels)
        print len(result)
        #print result
        self.assertTrue(result is not None)

                
def suite():
    #tests = [SBMLTest, PlainTextIOTest, FBATest, FVATest, FBATest2, FBATest3, GeneDeletionFBATest, GeneDeletionMOMATest, GeneEssentialityTest]
    tests = [CombinatorialGeneDeletion]
    
    test_suite = unittest.TestSuite()
    for test in tests:
        test_suite.addTest(unittest.makeSuite(test))
    return test_suite
        

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())