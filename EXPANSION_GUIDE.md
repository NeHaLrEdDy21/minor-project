# Expansion Summary: Legal Reasoning System
I will make some changes here

## What Changed

### 1. **Generalized Architecture** (minor.py refactored)
Your original system focused on "assault on minors" with hardcoded logic. The new version:

- **NeuralPerceptionModule**: Modular class with configurable action/entity dictionaries
  - Supports 5 charge types: assault, battery, theft, fraud, murder
  - Easily add more by updating `.actions` and `.entity_markers` dicts
  
- **SymbolicKnowledgeBase**: Now stores charge definitions with legal element descriptions
  - 6 predefined charges with descriptions (easily extended)
  - Cleaner API: `add_fact()` and `add_rule()` methods

- **Rule-Based System**: Inference rules now first-class objects (`Rule` class)
  - Rules include description/documentation
  - Side ("prosecution"/"defense") is semantic, not buried in rule dict

- **TemporalReasoner**: Extracted temporal logic as separate module
  - `valid_self_defense()` works with `List[Fact]` (not Events)
  - Extensible `check_temporal_constraint()` for other temporal patterns

### 2. **Case Summarization** (NEW)
Added `CaseSummarizer` class that generates:
- **Parties**: Accused/victim/witnesses extracted from facts
- **Timeline**: Chronological sequence with confidence scores
- **Applicable Charges**: Auto-detect which charges match the facts
- **Evidence Categorization**: Actus reus (guilty act), mens rea (intent), circumstantial
- **Mitigating Factors**: Auto-detect self-defense patterns, etc.
- **Narrative**: Plain English case summary

### 3. **Unified Pipeline** (run_system function)
Complete end-to-end workflow with clear stages:
```
[NEURAL LAYER]    â Extract facts from text
[SYMBOLIC LAYER]  â Ground in KB, add rules
[RULES]           â Load legal inference rules
[REASONING]       â Evaluate charges with burden of proof
[SUMMARY]         â Generate case summary
```

Each stage prints debug info so you can trace execution.

---

## How to Extend to New Charges

### Example: Add "Murder" Charge

**Step 1:** Verify action is in `NeuralPerceptionModule.actions`
```python
"murder": ["kill", "murdered", "slayed"],  # Already there!
```

**Step 2:** Add charge definition (optional, for documentation)
```python
# In SymbolicKnowledgeBase._initialize_charges()
"Murder": {
    "description": "Unlawful killing with malice aforethought",
    "elements": ["Kill(X,Y)", "Malice(X)", "Premeditation(X)"]
}
```

**Step 3:** Add rules in `run_system()`
```python
kb.add_rule(Rule(
    charge="Murder",
    premises=["Murder(accused,victim)"],
    weight=1.0,
    side="prosecution",
    name="Direct Evidence of Murder",
    description="Defendant killed victim"
))

# Defense: Prove self-defense or accident
kb.add_rule(Rule(
    charge="Murder",
    premises=["Accident(murder_event)"],
    weight=0.8,
    side="defense",
    name="Accidental Death",
    description="Death was unintentional"
))
```

---

## How to Improve Extraction

### Add Support for Weapons in Assault

In `NeuralPerceptionModule.extract_entities()`, weapons already added to entity list. To use them:

```python
# In run_system(), after building KB:
weapon_found = any(e.entity_type == "weapon" for fact in facts for e in fact.entities)
if weapon_found:
    kb.add_fact("WeaponUsed(accused)", 0.88)
    kb.add_rule(Rule(
        charge="Aggravated Assault",
        premises=["Assault(accused,victim)", "WeaponUsed(accused)"],
        weight=0.95,
        side="prosecution",
        name="Assault with Weapon",
        description="Assault with deadly weapon"
    ))
```

### Add Custom Entity Recognition

Extend `entity_markers` to catch more patterns:
```python
self.entity_markers = {
    "minor": ["minor", "child", "juvenile", ...],
    "drunk": ["drunk", "intoxicated", "inebriated"],  # NEW
    "provoked": ["provoked", "antagonized", "insulted"],  # NEW
    ...
}
```

---

## Integration with Notebook (neuro_symbolic_abstrat.ipynb)

The notebook shows progressive complexity:
1. **Cells 1-3**: Simple neural extraction (detect assault/minor flags)
2. **Cells 4-6**: Add symbolic KB and forward-chaining inference
3. **Cells 7-9**: Add burden of proof reasoning with weights

The new `minor.py` combines all layers into production code. Use the notebook to:
- Prototype new charge types before adding to `minor.py`
- Experiment with different rule weights
- Visualize reasoning steps interactively

---

## Testing the System

### Test Case 1: Assault on Minor with Self-Defense
```python
text = "Mary attacked John. John assaulted Mary, who is a minor."
run_system(text, charge="Assault on Minor", theta=0.6)
```
Expected: `"Not Guilty"` (self-defense valid: Mary attacked first)

### Test Case 2: Theft
```python
text = "Bob stole Alice's money from her purse."
run_system(text, charge="Theft", theta=0.6)
```
Expected: Extracts `Theft(Bob,Alice)` and `Property(money)`

### Test Case 3: Multiple Charges
```python
text = "John assaulted Mary, a minor, with a knife."
run_system(text)  # No charge specified = evaluate all applicable
```
Expected: Evaluates both "Assault" and "Assault on Minor" charges

---

## Next Steps

1. **Extend `entity_markers`**: Add location, time expressions, mental states
2. **Add evidence strength categories**: Confidence propagation through rules
3. **Implement appeal reasoning**: Check verdict consistency if premises change
4. **Add sentencing logic**: Map verdict to penalty based on aggravating/mitigating factors
5. **Multi-party scenarios**: Handle disputes, multiple defendants
