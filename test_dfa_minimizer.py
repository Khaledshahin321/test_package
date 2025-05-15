"""
Test cases for the DFA Minimizer.
"""

import unittest
from dfa_minimizer import DFA

class TestDFAMinimizer(unittest.TestCase):
    def test_simple_dfa_minimization(self):
        """Test minimization of a simple DFA."""
        # DFA for binary strings ending with '01'
        states = {'q0', 'q1', 'q2', 'q3'}
        alphabet = {'0', '1'}
        transitions = {
            ('q0', '0'): 'q1',
            ('q0', '1'): 'q3',
            ('q1', '0'): 'q1',
            ('q1', '1'): 'q2',
            ('q2', '0'): 'q1',
            ('q2', '1'): 'q3',
            ('q3', '0'): 'q1',
            ('q3', '1'): 'q3'
        }
        start_state = 'q0'
        final_states = {'q2'}
        
        dfa = DFA(states, alphabet, transitions, start_state, final_states)
        minimized_dfa = dfa.minimize()
        
        # The minimal DFA should have 3 states
        self.assertEqual(len(minimized_dfa.states), 3)
        
        # Check if the minimized DFA accepts the correct strings
        self.assertTrue(self.accepts(minimized_dfa, "01"))
        self.assertTrue(self.accepts(minimized_dfa, "001"))
        self.assertTrue(self.accepts(minimized_dfa, "101"))
        self.assertTrue(self.accepts(minimized_dfa, "0001"))
        
        self.assertFalse(self.accepts(minimized_dfa, ""))
        self.assertFalse(self.accepts(minimized_dfa, "0"))
        self.assertFalse(self.accepts(minimized_dfa, "1"))
        self.assertFalse(self.accepts(minimized_dfa, "00"))
        self.assertFalse(self.accepts(minimized_dfa, "10"))
        self.assertFalse(self.accepts(minimized_dfa, "11"))
        self.assertFalse(self.accepts(minimized_dfa, "010"))
        self.assertFalse(self.accepts(minimized_dfa, "011"))
    
    def test_inaccessible_states_removal(self):
        """Test removal of inaccessible states during minimization."""
        # DFA with inaccessible states
        states = {'q0', 'q1', 'q2', 'q3', 'q4'}
        alphabet = {'0', '1'}
        transitions = {
            ('q0', '0'): 'q1',
            ('q0', '1'): 'q2',
            ('q1', '0'): 'q1',
            ('q1', '1'): 'q2',
            ('q2', '0'): 'q0',
            ('q2', '1'): 'q2',
            # q3 and q4 are inaccessible
            ('q3', '0'): 'q4',
            ('q3', '1'): 'q3',
            ('q4', '0'): 'q3',
            ('q4', '1'): 'q4'
        }
        start_state = 'q0'
        final_states = {'q2', 'q4'}  # q4 is accepting but inaccessible
        
        dfa = DFA(states, alphabet, transitions, start_state, final_states)
        minimized_dfa = dfa.minimize()
        
        # The minimal DFA should have only the accessible states (2 states after minimization)
        self.assertEqual(len(minimized_dfa.states), 2)
        self.assertNotIn('q4', str(minimized_dfa))  # Ensure q4 is removed
    
    def test_equivalent_states_merging(self):
        """Test merging of equivalent states during minimization."""
        # DFA with equivalent states
        states = {'q0', 'q1', 'q2', 'q3', 'q4'}
        alphabet = {'a', 'b'}
        transitions = {
            ('q0', 'a'): 'q1',
            ('q0', 'b'): 'q2',
            ('q1', 'a'): 'q3',
            ('q1', 'b'): 'q4',
            ('q2', 'a'): 'q3',
            ('q2', 'b'): 'q4',
            ('q3', 'a'): 'q3',
            ('q3', 'b'): 'q4',
            ('q4', 'a'): 'q3',
            ('q4', 'b'): 'q4'
        }
        start_state = 'q0'
        final_states = {'q3', 'q4'}
        
        dfa = DFA(states, alphabet, transitions, start_state, final_states)
        minimized_dfa = dfa.minimize()
        
        # q1 and q2 should be merged, and q3 and q4 should remain separate
        # So the minimal DFA should have 3 states
        self.assertEqual(len(minimized_dfa.states), 3)
    
    def accepts(self, dfa, input_string):
        """
        Check if the DFA accepts the given input string.
        
        Args:
            dfa (DFA): The DFA to check
            input_string (str): The input string
        
        Returns:
            bool: True if the DFA accepts the string, False otherwise
        """
        current_state = dfa.start_state
        
        for symbol in input_string:
            if (current_state, symbol) not in dfa.transitions:
                return False
            current_state = dfa.transitions[(current_state, symbol)]
        
        return current_state in dfa.final_states


if __name__ == '__main__':
    unittest.main()
