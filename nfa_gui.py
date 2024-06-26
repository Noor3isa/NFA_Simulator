import customtkinter as ctk
import pylab as plt
import pandas as pd
import graphviz
import pandastable
from pandastable import Table
from tkinter import filedialog,messagebox,ttk
import tkinter
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import tkinter as tk
from tkinter import Label
from tkinter import filedialog
from PIL import Image, ImageTk
import time


import re

from prompt_toolkit.key_binding.bindings.named_commands import self_insert

input = " "


class PandasAPP():
    def __init__(self, frame) ->   None :
        try :
            self.frame = frame
            self.frame.place(relx=0.35, rely=0)
            df = pd.read_csv("transition_table.csv")
            self.table = Table(self.frame, dataframe=df)
            self.table.show()
        except Exception as e:
            tkinter.messagebox.showerror("Information", f"{str(e)}")
            return None


import ast


class NFA:
    def __init__(self, Q, Sigma, delta, S, F):
        self.Q = Q  # a set of states
        self.Sigma = Sigma  # a set of symbols
        self.delta = delta  # a transition table
        self.S = S  # a set of start states
        self.F = F  # a set of final states
        self.stripped = False
        self.path = []

    def __repr__(self) -> str:
        f"NFA(Q={self.Q}, Sigma={self.Sigma}, delta={self.delta}, S={self.S}, F={self.F})"

    def do_delta(self, q, x):
        try:
            return self.delta[(q, x)]
        except KeyError:
            return set()

    def run(self, w):
        i = 0
        P = self.S
        while w != "":
            Pnew = set()
            for q in P:
                Pnew = Pnew | self.do_delta(q, w[0])
            if P:
                self.path.append([w[0], P.pop()])
            w = w[1:]
            P = Pnew
            i += 1
        return (P & self.F) != set()

    def get_e_closure(self, state):
        visited = {}
        visited[state] = 0
        closure_stack = [state]

        while len(closure_stack) > 0:
            current_state = closure_stack.pop(0)

            for next_state in self.delta[(current_state, "epsilon")]:

                if next_state not in visited.keys():
                    visited[next_state] = 0
                    closure_stack.append(next_state)

            visited[current_state] = 1

        return set(visited.keys())

    def is_final_state(self, state_set):
        for s in state_set:
            if s in self.F:
                return True
        return False

    def remove_epsilon(self):
        if self.stripped:
            print("Already modified")
            return
        # Calculating all epsilon closures
        eclosure = {}
        for s in self.Q:
            eclosure[s] = list(self.get_e_closure(s))

        # Initializations
        state_stack = []
        initial_closure = eclosure[0]
        state_stack.append(initial_closure)
        new_delta = {}
        new_q = []
        new_q.append(set(initial_closure))

        while state_stack:
            current = tuple(state_stack.pop(0))
            for a in self.Sigma:
                if a == "epsilon":
                    continue
                from_closure = set()
                for s in current:
                    from_closure = from_closure | self.delta[(s, a)]
                to_state = set()
                for state in from_closure:
                    to_state = to_state | set(eclosure[state])

                if to_state and to_state not in new_q:
                    new_q.append(to_state)
                    state_stack.append(to_state)
                if (current, a) not in new_delta:
                    new_delta[(current, a)] = to_state

        new_f = set()
        for s in new_q:
            if self.is_final_state(s):
                new_f.add(tuple(s))

        self.Q = new_q
        state_index_map = {tuple(state): idx for idx, state in enumerate(self.Q)}
        self.F = {state_index_map[final_state] for final_state in new_f}
        indexed_new_delta = dict()
        for state_input, transition in new_delta.items():
            state_tuple, symbol = state_input
            state_idx = state_index_map[state_tuple]
            indexed_new_delta[(state_idx, symbol)] = set()
            target_state_tuple = tuple(transition)
            if target_state_tuple:
                target_state_idx = state_index_map[target_state_tuple]
                indexed_new_delta[(state_idx, symbol)] = {target_state_idx}
            else:
                indexed_new_delta[(state_idx, symbol)] = set()

        self.delta = indexed_new_delta
        print(f"New states: {self.Q}")
        print(f"New transitions: {self.delta}")
        print(f"New finals: {self.F}")
        self.stripped = True
        return




def nfa_from_csv(csv):
    df = pd.read_csv(csv)
    list_of_states = df.loc[:, "state"].tolist()
    start = {0}
    final = {max(list_of_states)}
    headers = df.columns.values
    sigma = set(headers[1:])
    delta = {}
    for state in list_of_states:
        for symbol in sigma:
            next_state_string = df.loc[df["state"] == state, symbol].iloc[0]
            if next_state_string == '-':
                delta[(state, symbol)] = set()
            else:
                next_state = ast.literal_eval(next_state_string)
                if isinstance(next_state, int):
                    delta[(state, symbol)] = {next_state}
                elif isinstance(next_state, (list, tuple, set)):
                    delta[(state, symbol)] = set(next_state)
    nfa = NFA(list_of_states, sigma, delta, start, final)
    print(nfa.S)
    print(nfa.F)
    print(nfa.Q)
    print(nfa.Sigma)
    print(nfa.delta)
    return nfa






class Type:
    SYMBOL = 1
    CONCAT = 2
    UNION = 3
    KLEENE = 4


class ExpressionTree:

    def __init__(self, _type, value=None):
        self._type = _type
        self.value = value
        self.left = None
        self.right = None


def constructTree(regexp):
    try :
        stack = []
        for c in regexp:
            if c.isalpha():
                stack.append(ExpressionTree(Type.SYMBOL, c))
            else:
                if c == "|":
                    z = ExpressionTree(Type.UNION)
                    z.right = stack.pop()
                    z.left = stack.pop()
                elif c == ".":
                    z = ExpressionTree(Type.CONCAT)
                    z.right = stack.pop()
                    z.left = stack.pop()
                elif c == "*":
                    z = ExpressionTree(Type.KLEENE)
                    z.left = stack.pop()
                stack.append(z)

        return stack[0]
    except Exception as e:
        # Handle any type of exception that might occur
        print(f"An error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",
                                         bg_color="black")
        tkinter.messagebox.showerror("Information", "your RE is not VALID")
        # Wait for 2 seconds
        time.sleep(2)
        # Run exit(1) after the 2-second delay
        exit(1)



def inorder(et):
    try :
        if et._type == Type.SYMBOL:
            print(et.value)
        elif et._type == Type.CONCAT:
            inorder(et.left)
            print(".")
            inorder(et.right)
        elif et._type == Type.UNION:
            inorder(et.left)
            print("+")
            inorder(et.right)
        elif et._type == Type.KLEENE:
            inorder(et.left)
            print("*")
    except Exception as e:
        # Handle any type of exception that might occur
        print(f"An error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",bg_color="black")
        tkinter.messagebox.showerror("Information", "your RE is not VALID")
        # Wait for 2 seconds
        time.sleep(2)
        exit(1)


def higherPrecedence(a, b):
    p = ["|", ".", "*"]
    return p.index(a) > p.index(b)


def postfix(regexp):
    try :
        # adding dot "." between consecutive symbols
        temp = []
        for i in range(len(regexp)):
            if i != 0 \
                    and (regexp[i - 1].isalpha() or regexp[i - 1] == ")" or regexp[i - 1] == "*") \
                    and (regexp[i].isalpha() or regexp[i] == "("):
                temp.append(".")
            temp.append(regexp[i])
        regexp = temp

        stack = []
        output = ""

        for c in regexp:
            if c.isalpha():
                output = output + c
                continue

            if c == ")":
                while len(stack) != 0 and stack[-1] != "(":
                    output = output + stack.pop()
                stack.pop()
            elif c == "(":
                stack.append(c)
            elif c == "*":
                output = output + c
            elif len(stack) == 0 or stack[-1] == "(" or higherPrecedence(c, stack[-1]):
                stack.append(c)
            else:
                while len(stack) != 0 and stack[-1] != "(" and not higherPrecedence(c, stack[-1]):
                    output = output + stack.pop()
                stack.append(c)

        while len(stack) != 0:
            output = output + stack.pop()

        return output
    except Exception as e:
        # Handle any type of exception that might occur
        print(f"An error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        # check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",
        #                                  bg_color="black")
        tkinter.messagebox.showerror("Information", str(e))
        # Wait for 5 seconds
        time.sleep(2)
        # Run exit(1) after the 5-second delay
        exit(1)



class FiniteAutomataState:
    def __init__(self):
        self.next_state = {}


def evalRegex(et):
    # returns equivalent E-NFA for given expression tree (representing a Regular
    # Expression)
    try :
        if et._type == Type.SYMBOL:
            return evalRegexSymbol(et)
        elif et._type == Type.CONCAT:
            return evalRegexConcat(et)
        elif et._type == Type.UNION:
            return evalRegexUnion(et)
        elif et._type == Type.KLEENE:
            return evalRegexKleene(et)
    except Exception as e:
        # Handle any type of exception that might occur
        print(f"An error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        # check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",
        #                                  bg_color="black")
        tkinter.messagebox.showerror("Information", str(e))
        # Wait for 5 seconds
        time.sleep(2)
        # Run exit(1) after the 5-second delay
        exit(1)


def evalRegexSymbol(et):
    try :
        start_state = FiniteAutomataState()
        end_state = FiniteAutomataState()

        start_state.next_state[et.value] = [end_state]
        return start_state, end_state
    except Exception as e:
        # Handle any type of exception that might occur
        print(f"An error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        # check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",
        #                                  bg_color="black")
        tkinter.messagebox.showerror("Information", str(e))
        # Wait for 5 seconds
        time.sleep(2)
        # Run exit(1) after the 5-second delay
        exit(1)


def evalRegexConcat(et):
    try :
        left_nfa = evalRegex(et.left)
        right_nfa = evalRegex(et.right)

        left_nfa[1].next_state['epsilon'] = [right_nfa[0]]

        return left_nfa[0], right_nfa[1]
    except Exception as e:
        # Handle any type of exception that might occur
        print(f"An error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        # check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",
        #                                  bg_color="black")
        tkinter.messagebox.showerror("Information", str(e))
        # Wait for 5 seconds
        time.sleep(2)
        # Run exit(1) after the 5-second delay
        exit(1)


def evalRegexUnion(et):
    try :
        start_state = FiniteAutomataState()
        end_state = FiniteAutomataState()

        up_nfa = evalRegex(et.left)
        down_nfa = evalRegex(et.right)

        start_state.next_state['epsilon'] = [up_nfa[0], down_nfa[0]]
        up_nfa[1].next_state['epsilon'] = [end_state]
        down_nfa[1].next_state['epsilon'] = [end_state]

        return start_state, end_state
    except Exception as e:
        # Handle any type of exception that might occur
        print(f"An error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        # check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",
        #                                  bg_color="black")
        tkinter.messagebox.showerror("Information", str(e))
        # Wait for 5 seconds
        time.sleep(2)
        # Run exit(1) after the 5-second delay
        exit(1)


def evalRegexKleene(et):
    try :
        start_state = FiniteAutomataState()
        end_state = FiniteAutomataState()

        sub_nfa = evalRegex(et.left)

        start_state.next_state['epsilon'] = [sub_nfa[0], end_state]
        sub_nfa[1].next_state['epsilon'] = [sub_nfa[0], end_state]

        return start_state, end_state
    except Exception as e:
        # Handle any type of exception that might occur
        print(f"An error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        # check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",
        #                                  bg_color="black")
        tkinter.messagebox.showerror("Information", str(e))
        # Wait for 5 seconds
        time.sleep(2)
        # Run exit(1) after the 5-second delay
        exit(1)


t = [["state", 'symbol', 'next state']]


def printStateTransitions(state, states_done, symbol_table):
    try :
        if state in states_done:
            return

        states_done.append(state)

        for symbol in list(state.next_state):
            line_output = "s" + str(symbol_table[state]) + "\t\t" + symbol + "\t\t\t"

            for ns in state.next_state[symbol]:
                if ns not in symbol_table:
                    symbol_table[ns] = 1 + sorted(symbol_table.values())[-1]
                line_output = line_output + "s" + str(symbol_table[ns]) + " "
                t.append([str(symbol_table[state]), symbol, str(symbol_table[ns])])
            print(line_output)

            for ns in state.next_state[symbol]:
                printStateTransitions(ns, states_done, symbol_table)
    except Exception as e:
        # Handle any type of exception that might occur
        print(f"An error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        # check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",
        #                                  bg_color="black")
        tkinter.messagebox.showerror("Information", str(e))
        # Wait for 5 seconds
        time.sleep(2)
        # Run exit(1) after the 5-second delay
        exit(1)



def printTransitionTable(finite_automata):
    print("State\t\tSymbol\t\t\tNext state")
    printStateTransitions(finite_automata[0], [], {finite_automata[0]: 0})


# to positive closure
def check(st):
    try :
        v = 0
        for i in range(len(st)):
            if st[i] == '+':
                v = 1
                break
        if v == 1:
            print('have')
            cv = convert(input)
            r = positive(cv)
            return r
        else:
            return st
    except Exception as e:
        # Handle any type of exception that might occur
        print(f"An error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        # check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",
        #                                  bg_color="black")
        tkinter.messagebox.showerror("Information", str(e))
        # Wait for 5 seconds
        time.sleep(2)
        # Run exit(1) after the 5-second delay
        exit(1)

def convert(s):
    try :
        ms = []
        f = 0
        for i in range(len(s)):
            if s[i] == "(":
                x = i
                f = 1

            if s[i] == ")":
                y = i
                ms.append(s[x:y + 1])
                f = 0

            if f == 0:
                ms.append(s[i])
        ms = list(filter(lambda x: x != ')', ms))
        return ms
    except Exception as e:
        # Handle any type of exception that might occur
        print(f"An error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        # check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",
        #                                  bg_color="black")
        tkinter.messagebox.showerror("Information", str(e))
        # Wait for 5 seconds
        time.sleep(2)
        # Run exit(1) after the 5-second delay
        exit(1)


def positive(t):
   try :
       for i in range(len(t)):

           if t[i] == '+':

               ele = t.pop(i - 1)
               ele = ele + ele + '*'
               t.insert(i - 1, ele)

           else:
               pass

       out = ''
       t = list(filter(lambda x: x != '+', t))
       print('t', t)
       for i in range(len(t)):
           out = out + t[i]

       print('output', out)
       return out
   except Exception as e:
       # Handle any type of exception that might occur
       print(f"An error occurred: {type(e).__name__}")
       print(f"Error message: {str(e)}")
       # check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",
       #                                  bg_color="black")
       tkinter.messagebox.showerror("Information", str(e))
       # Wait for 5 seconds
       time.sleep(2)
       # Run exit(1) after the 5-second delay
       exit(1)


#
# def group_inner_list(item_list):
#         grouped_items = []
#         grouped_items = defaultdict(list)
#         items = []
#         items = item_list
#         for sublist in items:
#             state = sublist[0]
#             symbol = sublist[1]
#             next_state = int(sublist[2])
#             grouped_items[state] = []
#             grouped_items[state].append((symbol, next_state))
#         # print("grouped_items",grouped_items)
#
#
#         updated_list = []
#         for state, values in grouped_items.items():
#             symbols = list(set([symbol for symbol, _ in values]))
#             combined_values = [next_state for _, next_state in values]
#             # print(type(combined_values[0]))
#             updated_list.append([state, symbols] + [combined_values])
#
#         return updated_list


def group_inner_list(item_list):
    grouped_items = defaultdict(list)

    for sublist in item_list:
        state = sublist[0]
        symbol = sublist[1]
        next_state = int(sublist[2])
        # print(type(next_state))
        grouped_items[state].append((symbol, next_state))
        # print(grouped_items)

    updated_list = []
    for state, values in grouped_items.items():
        symbols = list(set([symbol for symbol, _ in values]))
        combined_values = [next_state for _, next_state in values]
        # print(type(combined_values[0]))
        updated_list.append([state, symbols] + [combined_values])

    return updated_list


def Intialize_dataframe_columns() :
    df = pd.DataFrame()
    # Initialize separate lists for each position
    state_list = []
    symbol_list = []
    next_state_list = []

    # Extract elements at the same position
    for item in t:
        print(item)
        state_list.append(item[0])
        symbol_list.append(item[1])
        next_state_list.append(item[2])

    # slice needed values
    state_list = state_list[1:]
    symbol_list = symbol_list[1:]
    next_state_list = next_state_list[1:]

    # Print the separate lists
    print("state_list", state_list)
    print("symbol_list", symbol_list)
    print("next_state_list", next_state_list)
    #
    # Find the unique values
    distinct_symbols = list(set(symbol_list))
    # Convert string numbers to integers and sort the list
    distinct_states = list(set(sorted(map(int, state_list))))

    # Print the sorted list
    print(distinct_states)

    # Remove 'epsilon' from the list
    distinct_symbols.remove('epsilon')

    # Sort the remaining letters alphabetically
    distinct_symbols.sort()

    # Create a new list with 'symbol' as the first element, the sorted letters in the middle, and 'epsilon' as the last element
    new_lst = ['state'] + distinct_symbols + ['epsilon']

    # Create a dataframe from the new list
    df = pd.DataFrame(columns=[new_lst])

    # Print the updated dataframe
    return df


def contrust_dataframe() :

    df = Intialize_dataframe_columns()
    print("dataframe columns" ,df.columns)
    items = []
    items = t[1:]
    print("items", items)
    updated_item_list = []
    updated_item_list = group_inner_list(items)
    # print("updated_item_list",updated_item_list)
    first_states = set()
    last_states = set()
    # Add nodes and edges
    for start, label, end in items:
        first_states.add(start)

    # Iterate over the items and update the DataFrame
    for item in updated_item_list:
        current_state, symbol, next_state = item
        current_state = int(current_state)
        symbol = (symbol[0],)
        last_states = {items[-1] for items in items if items[-1] not in first_states}
        #
        for col in df.columns:
            # print(symbol, col[0])
            if symbol == col:
                if col[0] == "epsilon":
                    # print(True)
                    new_lst = []
                    new_lst.append(current_state)
                    new_lst.extend(element for element in next_state)
                    df.loc[current_state, col] = sorted(new_lst)
                    break
                else:

                    df.loc[current_state, col] = next_state

                    df.loc[current_state, "epsilon"] = current_state

                    break  # Exit the loop after finding a match

    df['state'] = [item[0] for item in updated_item_list]
    df.fillna('-', inplace=True)  # Fill null values with '-'
    # print(df)

    df.reset_index(drop=True, inplace=True)
    print(df)

    last_states = {items[-1] for items in items if items[-1] not in first_states}
    if len(last_states) == 1:
        last_states =list(last_states)
        print(last_states)
        df.loc[-1,"state"] = last_states[0]
        df.loc[-1,"epsilon"] = last_states[0]

    df.fillna('-', inplace=True)  # Fill null values with '-'
    # print(df)

    df.reset_index(drop=True, inplace=True)
    print("from contrust_dataframe" , df)

    # Save the DataFrame as a CSV file
    df.to_csv('transition_table.csv', index=False)


def uniqe_list(input_list) :
    unique_set = set(map(tuple, input_list))

    # Convert the tuples back to lists
    unique_list = [list(item) for item in unique_set]

    # Print the unique list
    return (unique_list)



def Draw_nfa_graph() :
    # Create a new Graphviz graph
    items = []
    graph = graphviz.Digraph()
    # Initialize a set to keep track of states that appear as first elements in any transition
    first_states = set()
    last_states = set()
    items = t[1:]
    # items=uniqe_list(items)


    # Add nodes and edges
    for start, label, end in items:
        graph.edge(start, end, label=" " + label)
        first_states.add(start)

    # Identify the first state as the first element of the first transition
    first_state = items[0][0]

    # Identify the last state as the last element of any transition that doesn't appear as the first element in any other transition
    last_states = {items[-1] for items in items if items[-1] not in first_states}
    if len(last_states) == 1:
        # last_states.tolist()
        print("not common state")
    else:
        tkinter.messagebox.showerror("Information", "Ambiguous last state")
        return None
        # raise ValueError("Ambiguous last state")

    # Add styling for nodes
    for state in first_states:
        if state == first_state:
            graph.node(state, shape='circle')  # Make first state a  circle

    for state in last_states:
        graph.node(state, shape='doublecircle')  # Make last state(s) a double circle

    # Render the graph
    graph.render('output', format='png', cleanup=True)




def validate_regex(pattern):
    try:
        re.compile(pattern)
        print("Regular expression is valid.")
        return True
    except re.error:
        print("Invalid regular expression.")
        check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",bg_color="black")
        tkinter.messagebox.showerror("Information", "your RE is not VALID")
        return False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


app = ctk.CTk()
app.title("NFA Graph Design")
# app.iconphoto("NFAofaclosure.jpg")
app.geometry("500x450")



#Delete all component in frame befor write on it
def delete_child_components(child_frame):
    # Get a list of all the child components in the child frame
    child_components = child_frame.pack_slaves()

    # Destroy each child component
    for component in child_components:
        component.destroy()



def read_exp() :
    # take t as input
    global t
    t = [["state", 'symbol', 'next state']]
    df = pd.DataFrame()
    updated_list = []
    input = ""
    input = entry_box.get()
    check_validation_label.configure(text="")
    value_of_validation = validate_regex(input)
    if(value_of_validation) :
        check_validation_label.configure(text="your RE is VALID", font=('Times', 12),bg_color="black",fg_color="green")
        pass

    if(value_of_validation != True) :
        exit(1)

    r = check(input)
    print(r)
    pr = postfix(r)
    et = constructTree(pr)
    # inorder(et)
    fa = evalRegex(et)
    print('regular expression :', input)
    printTransitionTable(fa)
    print(t)


    read_file_label.configure(text='')
    read_exp_label.configure(text="read from your entry RE", font=('Times', 14))

    new_window = ctk.CTkToplevel(app)
    new_window.title("NFA Graph Design")
    new_window.geometry("600x500")
    new_window.grid()

    # def clear_frame_content(frame):
    #     for widget in frame.winfo_children():
    #         widget.destroy()

    # new_frame for choise
    new_frame1 = ctk.CTkFrame(new_window,width=200, height=500)
    new_frame1.place(relx=0,rely=0)

    nfa_label = ctk.CTkLabel(new_frame1, text="Choose From:", font=('Times', 24))
    nfa_label.place(relx=0.13, rely=0.2)



    def load_dataframe() :
        Matching_tree_button.configure(state="normal")
        try :
            # clear_frame_content(new_frame2)
            updated_list = group_inner_list(t[1:])
            # print("updated_list", updated_list)
            contrust_dataframe()
            df = pd.read_csv("transition_table.csv")
            root = PandasAPP(new_frame2)

        except ValueError :
            tkinter.messagebox.showerror("Information","dataframe is invalid")
            return None
        except FileNotFoundError :
            tkinter.messagebox.showerror("Information","No such file as transition_table.csv")
            return None

        except Exception as e:
            tkinter.messagebox.showerror("Information", f"{str(e)}")
            return None

    def show_graph() :
        try :
            # clear_frame_content(new_frame2)
            Draw_nfa_graph()
            img_name = "output.png"
            size = Image.open(img_name).size

            # Image.resize()
            image = ctk.CTkImage(light_image=Image.open(img_name), size=(400, 500))
            nfa_graph_image_label = ctk.CTkLabel(new_window, text="", image=image)
            nfa_graph_image_label.place(relx=0.35, rely=0)

        except Exception as e:
            tkinter.messagebox.showerror("Information", f"{str(e)}")
            return None

    def match_tree() :
        try :

            g = graphviz.Digraph(format='png')

            # entry_box
            input_entry_box = ctk.CTkEntry(new_frame1, placeholder_text="  Write your Sequence  ", font=("Times", 16), width=175,height=25)
            input_entry_box.place(relx=0.05, rely=0.78)


            def get_seq() :
                input_sequence = input_entry_box.get()
                try:
                    text_ = ""
                    nfa = nfa_from_csv("transition_table.csv")
                    print("i have opend ",)
                    nfa.remove_epsilon()
                    match = nfa.run(input_sequence)
                    print("match",match)
                    if(match==True) :
                        test_ = "accepted_path"
                        path = nfa.path
                        print("path",path)
                        matching_label = ctk.CTkLabel(new_frame1, text="accepted_path", font=('Times', 14))
                        matching_label.place(relx=0.05, rely=0.84)
                        symbols = []
                        current_states = []
                        next_states = []
                        for symbol,state in nfa.path :
                            symbols.append(symbol)
                            current_states.append(state)

                        next_states = current_states[1:]
                        print(symbols,current_states,next_states)

                        if (len(current_states) != len(next_states)) :
                            next_states.append(current_states[-1])
                        print(next_states)

                        # g.node_attr.update(shape='box')  # Square nodes
                        for state in current_states:
                            g.node(str(state), shape='box')


                        items = [current_states,symbols,next_states]
                        print(items)



                        result = [
                            [sublist[i] for sublist in items]
                            for i in range(len(items[0]))
                        ]

                        print("the accepted path is" ,result)

                        # Add nodes and edges
                        for row in result:
                            print(row[0],row[1],row[2])
                            g.edge(str(row[0]),str(row[2]), label=str(" " +row[1]))


                        g.render('state_diagram')

                        try:
                            # clear_frame_content(new_frame2)

                            img_name = "state_diagram.png"
                            size = Image.open(img_name).size

                            # Image.resize()
                            image = ctk.CTkImage(light_image=Image.open(img_name), size=(400, 500))
                            input_label = ctk.CTkLabel(new_window, text="", image=image)
                            input_label.place(relx=0.35, rely=0)

                        except Exception as e:
                            tkinter.messagebox.showerror("Information", f"{str(e)}")
                            return None




                    else :
                        test_ = "not accepted_path"
                        matching_label = ctk.CTkLabel(new_frame1, text="not accepted_path", font=('Times', 14))
                        matching_label.place(relx=0.05, rely=0.84)
                        delete_child_components(new_frame2)
                        input_label = ctk.CTkLabel(new_window, text="")
                        input_label.place(relx=0.35, rely=0)


                except Exception as e:
                    print("ERROR")
                    print(str(e))



                # Label_of_matching:

                # print("input_sequence",input_sequence)
                # if (input_sequence == "True"):
                #     matching_label.configure(text=text_, font=("Times", 16))
                # else:
                #     matching_label.configure(text="", font=("Times", 16))
                    # time.sleep(2)
                    # matching_label.configure(text=text_, font=("Times", 16))



            draw_seq_button = ctk.CTkButton(new_frame1, text="Get your Input", font=('Times', 12),
                                                 height=30, width=50, command=get_seq)
            draw_seq_button.place(relx=0.25, rely=0.9)

            # time.sleep(2)
            # if (input_sequence == None):
            #     input_seq_label.configure(text="not VALID Sequence")
            # else:
            #     input_seq_label.configure(text="not VALID Sequence")

        except Exception as e:
            tkinter.messagebox.showerror("Information", f"{str(e)}")
            return None





    transtion_table_button = ctk.CTkButton(new_frame1,text="display Transion Table",font=('Times', 16),height=30,width=150,command=load_dataframe)
    transtion_table_button.place(relx=0.13,rely=0.4)





    Nfa_graph_button = ctk.CTkButton(new_frame1, text="display NFA Graph", font=('Times', 16),height=30,width=150,command=show_graph)
    Nfa_graph_button.place(relx=0.13, rely=0.55)

    Matching_tree_button = ctk.CTkButton(new_frame1, text="display Matching Tree", font=('Times', 16),height=30,width=150,command=match_tree)
    Matching_tree_button.place(relx=0.13, rely=0.70)
    Matching_tree_button.configure(state="disabled")

    new_frame2 = ctk.CTkFrame(new_window,width=400,height=500)
    new_frame2.place(relx=0.35,rely=0)







    # updated_list=group_inner_list(t[1:])
    # print("updated_list",updated_list)
    # contrust_dataframe()
    # Draw_nfa_graph()




def read_file():
    read_exp_label.configure(text='')
    read_file_label.configure(text="read from your entry File", font=('Times', 14))
    filename = filedialog.askopenfilename(initialdir="/",title="Select A File",filetype=(("txt files","*.txt"),("All Files",("*.*"))))
    entry_box.configure(font=("Times", 16))
    entry_box.delete(0, tk.END)  # Clear existing text
    entry_box.insert(0, filename)
    words = load_data()

    def next_re() :
        try :
            entry_box.delete(0, tk.END)  # Clear existing text
            entry_box.insert(0, words.pop(0))
        except IndexError :
            tkinter.messagebox.showerror("Information", "You have drawn all RE in File")
        except Exception as e:
            # Handle any type of exception that might occur
            print(f"An error occurred: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",
                                             bg_color="black")
            tkinter.messagebox.showerror("Information", "your RE is not VALID")
            # # Wait for 2 seconds
            # time.sleep(2)
            # exit(1)


    if entry_box.get().strip() == "":
        tkinter.messagebox.showerror("Information", "you did not choose file")
    else :
        read_next_RE = ctk.CTkButton(master=app, text="NEXT RE", font=('Times', 16),
                                     command=next_re)  # TODO :, command=read_exp
        read_next_RE.place(relx=0.65, rely=0.9)


def load_data() :
    file_path = entry_box.get()
    try :
        stop_word = '#'
        txt_filename=r"{}".format(file_path)
        with open(txt_filename, 'r') as file:
            content = file.read()
            words = re.split("#|\n",content)
            print(words)
            return words
    except ValueError :
        tkinter.messagebox.showerror("Information", "the file you have choosen is invalid ")
        return None
    except FileNotFoundError :
        tkinter.messagebox.showerror("Information", f"No such file as this file name")
        return None
    except Exception as e:
        tkinter.messagebox.showerror("Information", f"{str(e)}")
        return None



# NFA Graph Design
nfa_label = ctk.CTkLabel(app,text="NFA Graph Design",font=('Times', 24))
nfa_label.place(relx=0.36,rely=0.2)


# read_exp_button
read_exp_button = ctk.CTkButton(master=app,text="get your RE",font=('Times', 16),command=read_exp)
read_exp_button.place(relx=0.1,rely=0.75)

# read_exp_label
read_exp_label = ctk.CTkLabel(app,text="")
read_exp_label.place(relx=0.1,rely=0.82)

# read_file_button
read_file_button = ctk.CTkButton(master=app,text="read From File",font=('Times', 16),command=read_file)
read_file_button.place(relx=0.65,rely=0.75)

# read_file_label
read_file_label = ctk.CTkLabel(app,text="")
read_file_label.place(relx=0.65,rely=0.82)


# check_validation_label
check_validation_label = ctk.CTkLabel(app, text="")
check_validation_label.place(relx=0.2,rely=0.55)

# entry_box
entry_box =ctk.CTkEntry(app,placeholder_text="Drop File/Write RE",font=("Times", 20),width= 300,height=35)
entry_box.place(relx=0.2,rely=0.45)
app.mainloop()





