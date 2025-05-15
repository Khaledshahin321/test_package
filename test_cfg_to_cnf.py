"""
Test cases for the CFG to CNF Converter.
"""

import unittest
from cfg_to_cnf import CFG, CNFConverter

class TestCFGtoCNF(unittest.TestCase):
    def test_simple_cfg_conversion(self):
        """Test conversion of a simple CFG to CNF."""
        # Example grammar
        variables = {"S", "A", "B"}
        terminals = {"a", "b"}
        productions = {
            "S": ["aA", "B"],
            "A": ["SB", "aAa"],
            "B": ["b", ""]  # epsilon represented as empty string
        }
        
        cfg = CFG(variables, terminals, productions, "S")
        converter = CNFConverter(cfg)
        cnf = converter.convert_to_cnf()
        
        # Verify that productions are in CNF form
        for var, prods in cnf.productions.items():
            for prod in prods:
                if len(prod) == 1:
                    # A -> a form (terminal)
                    self.assertTrue(prod in cnf.terminals)
                elif len(prod) == 2:
                    # A -> BC form (two variables)
                    self.assertTrue(prod[0] in cnf.variables and prod[1] in cnf.variables)
                else:
                    # Invalid CNF production
                    self.fail(f"Invalid CNF production: {var} -> {prod}")
    
    def test_epsilon_elimination(self):
        """Test elimination of epsilon productions."""
        variables = {"S", "A", "B"}
        terminals = {"a", "b"}
        productions = {
            "S": ["AB"],
            "A": ["a", ""],  # A can derive epsilon
            "B": ["b"]
        }
        
        cfg = CFG(variables, terminals, productions, "S")
        converter = CNFConverter(cfg)
        
        # Eliminate epsilon productions
        new_cfg = converter.eliminate_epsilon_productions()
        
        # Check that epsilon is eliminated
        for var, prods in new_cfg.productions.items():
            self.assertNotIn("", prods)
        
        # Check that S -> B is added (since A can be epsilon)
        self.assertIn("B", new_cfg.productions["S"])
    
    def test_unit_production_elimination(self):
        """Test elimination of unit productions."""
        variables = {"S", "A", "B"}
        terminals = {"a", "b"}
        productions = {
            "S": ["A"],  # unit production
            "A": ["B", "a"],  # unit production
            "B": ["b"]
        }
        
        cfg = CFG(variables, terminals, productions, "S")
        converter = CNFConverter(cfg)
        
        # Eliminate unit productions
        new_cfg = converter.eliminate_unit_productions()
        
        # Check that unit productions are eliminated
        for var, prods in new_cfg.productions.items():
            for prod in prods:
                self.assertFalse(prod in variables)
        
        # Check that transitive unit productions are handled
        # S -> A -> B -> b should become S -> b
        self.assertIn("b", new_cfg.productions["S"])
        self.assertIn("a", new_cfg.productions["S"])
    
    def test_long_production_breakdown(self):
        """Test breakdown of long productions."""
        variables = {"S"}
        terminals = {"a", "b", "c", "d"}
        productions = {
            "S": ["abcd"]  # long production
        }
        
        cfg = CFG(variables, terminals, productions, "S")
        converter = CNFConverter(cfg)
        cnf = converter.convert_to_cnf()
        
        # Check that all productions are in CNF form
        for var, prods in cnf.productions.items():
            for prod in prods:
                self.assertTrue(len(prod) <= 2)
                if len(prod) == 2:
                    self.assertTrue(prod[0] in cnf.variables and prod[1] in cnf.variables)
    
    def test_terminal_replacement(self):
        """Test replacement of terminals in mixed productions."""
        variables = {"S"}
        terminals = {"a", "b"}
        productions = {
            "S": ["aSb"]  # mixed production with terminals and variables
        }
        
        cfg = CFG(variables, terminals, productions, "S")
        converter = CNFConverter(cfg)
        cnf = converter.convert_to_cnf()
        
        # Check that terminals are replaced in mixed productions
        for var, prods in cnf.productions.items():
            for prod in prods:
                if len(prod) == 2:
                    self.assertTrue(prod[0] in cnf.variables and prod[1] in cnf.variables)


if __name__ == '__main__':
    unittest.main()
