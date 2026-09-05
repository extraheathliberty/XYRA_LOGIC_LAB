from xyra_logic import (
    Atom,
    Not,
    And,
    Or,
    Implies,
    truth_table,
    is_tautology,
    is_contradiction,
    is_valid_argument,
)


P = Atom("P")
Q = Atom("Q")


print()
print("==============================================")
print("      XYRA LOGIC-L0 LIVE DEMONSTRATION")
print("==============================================")


print()
print("=== DEMO 1: IMPLICATION TRUTH TABLE ===")
print()
print("P      Q      P -> Q")
print("--------------------")

for row in truth_table(Implies(P, Q)):
    assignment = row["assignment"]
    print(
        "{:<6} {:<6} {:<6}".format(
            assignment["P"],
            assignment["Q"],
            row["result"],
        )
    )


print()
print("=== DEMO 2: TAUTOLOGY ===")

tautology = Or(P, Not(P))

print("Expression: P OR NOT P")
print(
    "Result:",
    "TAUTOLOGY"
    if is_tautology(tautology)
    else "NOT TAUTOLOGY",
)


print()
print("=== DEMO 3: CONTRADICTION ===")

contradiction = And(P, Not(P))

print("Expression: P AND NOT P")
print(
    "Result:",
    "CONTRADICTION"
    if is_contradiction(contradiction)
    else "NOT CONTRADICTION",
)


print()
print("=== DEMO 4: MODUS PONENS ===")

print("Premise 1: P")
print("Premise 2: P -> Q")
print("Conclusion: Q")

modus_ponens = is_valid_argument(
    [P, Implies(P, Q)],
    Q,
)

print(
    "Result:",
    "VALID ARGUMENT"
    if modus_ponens
    else "INVALID ARGUMENT",
)


print()
print("=== DEMO 5: AFFIRMING THE CONSEQUENT ===")

print("Premise 1: P -> Q")
print("Premise 2: Q")
print("Conclusion: P")

affirming_consequent = is_valid_argument(
    [Implies(P, Q), Q],
    P,
)

print(
    "Result:",
    "VALID ARGUMENT"
    if affirming_consequent
    else "INVALID ARGUMENT",
)


print()
print("=== DEMO 6: LOGIC / TRUTH BOUNDARY ===")

print(
    "Formal validity answers whether a conclusion follows."
)
print(
    "It does NOT establish that the premises are factually true."
)


print()
print("==============================================")
print("            LOGIC-L0 DEMO COMPLETE")
print("==============================================")
