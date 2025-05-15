

class DFA:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

    def __str__(self):
        """String representation of the DFA."""
        return (f"States: {self.states}\n"
                f"Alphabet: {self.alphabet}\n"
                f"Transitions: {self.transitions}\n"
                f"Start State: {self.start_state}\n"
                f"Final States: {self.final_states}")

    def get_accessible_states(self):
        accessible = {self.start_state}
        queue = [self.start_state]
        
        while queue:
            state = queue.pop(0)
            for symbol in self.alphabet:
                if (state, symbol) in self.transitions:
                    next_state = self.transitions[(state, symbol)]
                    if next_state not in accessible:
                        accessible.add(next_state)
                        queue.append(next_state)
        
        return accessible

    def remove_inaccessible_states(self):
        accessible = self.get_accessible_states()
        
        # Filter states
        new_states = accessible
        
        # Filter final states
        new_final_states = self.final_states.intersection(accessible)
        
        # Filter transitions
        new_transitions = {}
        for (state, symbol), next_state in self.transitions.items():
            if state in accessible and next_state in accessible:
                new_transitions[(state, symbol)] = next_state
        
        return DFA(new_states, self.alphabet, new_transitions, 
                   self.start_state, new_final_states)

    def minimize(self):
        dfa = self.remove_inaccessible_states()
        
        if len(dfa.states) <= 1:
            return dfa
        
        partition = []
        accepting = dfa.final_states
        non_accepting = dfa.states - accepting
        
        if accepting:
            partition.append(accepting)
        if non_accepting:
            partition.append(non_accepting)
        
        # Refine the partition until it stabilizes
        while True:
            new_partition = refine_partition(dfa, partition)
            if new_partition == partition:
                break
            partition = new_partition
        
        # Create new DFA based on the minimized partition
        return create_minimized_dfa(dfa, partition)


def refine_partition(dfa, partition):
    result = []
    
    for group in partition:
        # For each group in the partition
        subgroups = {}
        
        for state in group:
            # Compute the signature of this state
            signature = []
            for symbol in dfa.alphabet:
                if (state, symbol) in dfa.transitions:
                    next_state = dfa.transitions[(state, symbol)]
                    # Find which group in partition contains the next_state
                    for i, p in enumerate(partition):
                        if next_state in p:
                            signature.append((symbol, i))
                            break
                else:
                    # No transition on this symbol
                    signature.append((symbol, -1))
            
            # Convert list to tuple for hashing
            signature = tuple(signature)
            
            # Add state to the appropriate subgroup
            if signature not in subgroups:
                subgroups[signature] = set()
            subgroups[signature].add(state)
        
        # Add each subgroup to the result
        for subgroup in subgroups.values():
            result.append(subgroup)
    
    return result


def create_minimized_dfa(dfa, partition):
    # Map from original states to representative states
    state_map = {}
    for i, group in enumerate(partition):
        representative = f"q{i}"
        for state in group:
            state_map[state] = representative
    
    # Create new DFA components
    new_states = {state_map[state] for state in dfa.states}
    new_alphabet = dfa.alphabet.copy()
    new_transitions = {}
    
    for (state, symbol), next_state in dfa.transitions.items():
        new_transitions[(state_map[state], symbol)] = state_map[next_state]
    
    new_start_state = state_map[dfa.start_state]
    new_final_states = {state_map[state] for state in dfa.final_states}
    
    return DFA(new_states, new_alphabet, new_transitions, 
               new_start_state, new_final_states)


# Example usage
if __name__ == "__main__":
    # Example DFA: Binary strings ending with '01'
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
    print("Original DFA:")
    print(dfa)
    
    minimized_dfa = dfa.minimize()
    print("\nMinimized DFA:")
    print(minimized_dfa)
