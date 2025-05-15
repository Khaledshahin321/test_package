"""
CFG to CNF Converter

This module provides functionality to convert a Context-Free Grammar (CFG)
to Chomsky Normal Form (CNF).
"""

class CFG:
    """
    Class representing a Context-Free Grammar.
    """
    def __init__(self, variables, terminals, productions, start_symbol):
        """
        Initialize a CFG.
        
        Args:
            variables (set): Set of non-terminal symbols (variables)
            terminals (set): Set of terminal symbols
            productions (dict): Dictionary mapping variables to lists of productions
            start_symbol: The start symbol of the grammar
        """
        self.variables = variables
        self.terminals = terminals
        self.productions = productions
        self.start_symbol = start_symbol
    
    def __str__(self):
        """String representation of the CFG."""
        result = []
        for variable, productions in self.productions.items():
            for production in productions:
                result.append(f"{variable} -> {production}")
        return "\n".join(result)


class CNFConverter:
    """
    Class to convert a CFG to Chomsky Normal Form.
    """
    def __init__(self, cfg):
        """
        Initialize with a CFG.
        
        Args:
            cfg (CFG): The CFG to convert
        """
        self.cfg = cfg
        self.new_var_counter = 0
        self.terminal_to_var = {}  # Maps terminals to their variable representatives
    
    def generate_new_variable(self):
        """
        Generate a new variable name that doesn't conflict with existing ones.
        
        Returns:
            str: A new variable name
        """
        while True:
            new_var = f"X{self.new_var_counter}"
            self.new_var_counter += 1
            if new_var not in self.cfg.variables:
                return new_var
    
    def eliminate_epsilon_productions(self):
        """
        Eliminate epsilon productions from the grammar.
        
        Returns:
            CFG: New CFG without epsilon productions
        """
        nullable = set()
        
        # Identify nullable variables
        while True:
            nullable_added = False
            
            for var, productions in self.cfg.productions.items():
                if var in nullable:
                    continue
                
                # Check if this variable has an epsilon production or 
                # if it has a production with all nullable variables
                if "" in productions:
                    nullable.add(var)
                    nullable_added = True
                else:
                    for prod in productions:
                        if all(symbol in nullable for symbol in prod):
                            nullable.add(var)
                            nullable_added = True
                            break
            
            if not nullable_added:
                break
        
        # Generate new productions
        new_productions = {var: [] for var in self.cfg.variables}
        
        for var, productions in self.cfg.productions.items():
            for prod in productions:
                if prod == "":  # Skip epsilon productions
                    continue
                
                # Generate all possible combinations by omitting nullable variables
                nullable_indices = [i for i, symbol in enumerate(prod) if symbol in nullable]
                num_combinations = 2 ** len(nullable_indices)
                
                for i in range(num_combinations):
                    # Determine which nullable variables to omit
                    omit = []
                    for j, idx in enumerate(nullable_indices):
                        if (i >> j) & 1:
                            omit.append(idx)
                    
                    # Create the new production by omitting specified nullable variables
                    new_prod = "".join(prod[j] for j in range(len(prod)) if j not in omit)
                    
                    # Only add non-empty productions
                    if new_prod and new_prod not in new_productions[var]:
                        new_productions[var].append(new_prod)
        
        # Handle the case where the start symbol is nullable
        if self.cfg.start_symbol in nullable:
            # Create a new start symbol that can derive epsilon
            new_start = self.generate_new_variable()
            new_productions[new_start] = ["", self.cfg.start_symbol]
            self.cfg.variables.add(new_start)
            new_start_symbol = new_start
        else:
            new_start_symbol = self.cfg.start_symbol
        
        return CFG(self.cfg.variables, self.cfg.terminals, new_productions, new_start_symbol)
    
    def eliminate_unit_productions(self):
        """
        Eliminate unit productions from the grammar.
        
        Returns:
            CFG: New CFG without unit productions
        """
        # Build unit pairs
        unit_pairs = {var: {var} for var in self.cfg.variables}
        
        # Compute the closure of unit pairs
        changed = True
        while changed:
            changed = False
            for A in self.cfg.variables:
                for B in list(unit_pairs[A]):
                    for prod in self.cfg.productions.get(B, []):
                        if prod in self.cfg.variables and prod not in unit_pairs[A]:
                            unit_pairs[A].add(prod)
                            changed = True
        
        # Create new productions
        new_productions = {var: [] for var in self.cfg.variables}
        
        for A in self.cfg.variables:
            for B in unit_pairs[A]:
                for prod in self.cfg.productions.get(B, []):
                    # Skip unit productions
                    if prod in self.cfg.variables:
                        continue
                    
                    if prod not in new_productions[A]:
                        new_productions[A].append(prod)
        
        return CFG(self.cfg.variables, self.cfg.terminals, new_productions, self.cfg.start_symbol)
    
    def convert_to_cnf(self):
        """
        Convert the CFG to Chomsky Normal Form.
        
        Returns:
            CFG: The grammar in CNF
        """
        # Step 1: Eliminate epsilon productions
        cfg = self.eliminate_epsilon_productions()
        
        # Step 2: Eliminate unit productions
        cfg = self.eliminate_unit_productions()
        
        # Step 3: Replace terminals in productions with length > 2
        variables = cfg.variables.copy()
        terminals = cfg.terminals.copy()
        productions = {var: [] for var in variables}
        
        # Copy existing productions first
        for var, prods in cfg.productions.items():
            productions[var] = prods.copy()
        
        # Replace terminals in mixed productions
        for var, prods in cfg.productions.items():
            new_prods = []
            for prod in prods:
                # Skip if this is already in CNF
                if len(prod) <= 1 or (len(prod) == 2 and prod[0] in variables and prod[1] in variables):
                    continue
                
                # Replace terminals with new variables
                new_prod = ""
                for symbol in prod:
                    if symbol in terminals:
                        if symbol not in self.terminal_to_var:
                            new_var = self.generate_new_variable()
                            self.terminal_to_var[symbol] = new_var
                            variables.add(new_var)
                            productions[new_var] = [symbol]
                        new_prod += self.terminal_to_var[symbol]
                    else:
                        new_prod += symbol
                
                new_prods.append(new_prod)
            
            # Add the new productions
            for prod in new_prods:
                if prod not in productions[var]:
                    productions[var].append(prod)
        
        # Step 4: Break down productions with length > 2
        final_productions = {var: [] for var in variables}
        
        for var, prods in productions.items():
            for prod in prods:
                if len(prod) <= 2:
                    # Keep productions already in CNF
                    if prod not in final_productions[var]:
                        final_productions[var].append(prod)
                else:
                    # Break down long productions
                    current_var = var
                    for i in range(len(prod) - 2):
                        next_var = self.generate_new_variable()
                        variables.add(next_var)
                        final_productions[next_var] = []
                        
                        if i == 0:
                            final_productions[current_var].append(prod[0] + next_var)
                        else:
                            final_productions[current_var].append(prev_var + next_var)
                        
                        if i == len(prod) - 3:
                            final_productions[next_var].append(prod[-2] + prod[-1])
                        
                        prev_var = next_var
                        current_var = next_var
        
        # Return the final CFG in CNF
        return CFG(variables, terminals, final_productions, cfg.start_symbol)


# Example usage
if __name__ == "__main__":
    # Example grammar
    variables = {"S", "A", "B"}
    terminals = {"a", "b"}
    productions = {
        "S": ["aA", "B"],
        "A": ["SB", "aAa"],
        "B": ["b", "ε"]  # epsilon represented as ε
    }
    
    # Replace "ε" with empty string for processing
    for var, prods in productions.items():
        productions[var] = [prod if prod != "ε" else "" for prod in prods]
    
    cfg = CFG(variables, terminals, productions, "S")
    print("Original CFG:")
    print(cfg)
    
    converter = CNFConverter(cfg)
    cnf = converter.convert_to_cnf()
    
    print("\nCNF:")
    print(cnf)
