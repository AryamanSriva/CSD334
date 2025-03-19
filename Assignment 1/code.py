from collections import defaultdict
from graphviz import Digraph

def epsilon_closure(state, nfa, visited=None):
    if visited is None:
        visited = set()
    if state in visited:
        return set()
    visited.add(state)
    closure = {state}
    for next_state in nfa['transition'].get(state, {}).get('ε', set()):
        closure.update(epsilon_closure(next_state, nfa, visited))
    return closure

def nfa_to_dfa(nfa):
    dfa = {
        'states': set(),
        'alphabet': nfa['alphabet'] - {'ε'},  
        'transition': defaultdict(dict),
        'start_state': frozenset(epsilon_closure(nfa['start_state'], nfa)),
        'accept_states': set()
    }

    unprocessed_states = [dfa['start_state']]
    dfa['states'].add(dfa['start_state'])

    while unprocessed_states:
        current_state = unprocessed_states.pop()

        for symbol in dfa['alphabet']:
            next_state = set()
            for nfa_state in current_state:
                next_state.update(nfa['transition'].get(nfa_state, {}).get(symbol, set()))
            
            next_state_closure = set()
            for state in next_state:
                next_state_closure.update(epsilon_closure(state, nfa))
            
            next_state_closure = frozenset(next_state_closure)

            if next_state_closure not in dfa['states']:
                dfa['states'].add(next_state_closure)
                unprocessed_states.append(next_state_closure)

            dfa['transition'][current_state][symbol] = next_state_closure

    for state in dfa['states']:
        if state.intersection(nfa['accept_states']):
            dfa['accept_states'].add(state)

    return dfa

def generate_dfa_graphviz(dfa):
    dot = Digraph(format='png')
    dot.attr(rankdir='LR', size='8,5')

    for state in dfa['states']:
        state_str = str(state)
        if state == dfa['start_state']:
            dot.node(state_str, state_str, shape='circle', style='bold')
        elif state in dfa['accept_states']:
            dot.node(state_str, state_str, shape='doublecircle')
        else:
            dot.node(state_str, state_str, shape='circle')

    for src_state, transitions in dfa['transition'].items():
        src_state_str = str(src_state)
        for symbol, dest_state in transitions.items():
            dest_state_str = str(dest_state)
            dot.edge(src_state_str, dest_state_str, label=symbol)

    dot.render('dfa_graph', cleanup=True)
    print("DFA graph saved")

def main():
    nfa = {
        'states': {'q0', 'q1', 'q2'},
        'alphabet': {'0', '1'},
        'transition': {
            'q0': {'0': {'q0'}, '1': {'q1', 'q2'}},
            'q1': {'0': {'q1', 'q2'}, '1': {'q2'}},
            'q2': {'0': {'q0', 'q1'}, '1': {'q1'}}
        },
        'start_state': 'q0',
        'accept_states': {'q1'}
    }

    dfa = nfa_to_dfa(nfa)

    generate_dfa_graphviz(dfa)

if _name_ == "_main_":
    main()