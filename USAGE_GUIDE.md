# Legal Case Analysis System - Complete Usage Guide

## Quick Start

### Option 1: Analyze from Case Document File

```python
from minor import DocumentParser, analyze_case_document

# Load case from file
doc = DocumentParser.load_from_file("sample_case.txt")

# Analyze the case
result = analyze_case_document(doc, theta=0.6)

# Save detailed report
result['report_generator'].save_report("case_verdict.txt")

# Access verdicts
for verdict in result['verdicts']:
    print(f"{verdict.charge}: {verdict.verdict}")
    print(f"Confidence: {verdict.confidence * 100:.1f}%")
```

### Option 2: Analyze from Text String

```python
from minor import analyze_case_document, CaseDocument

# Create case document from structured text
case_text = """CASE NUMBER: 2024-CV-001234
PLAINTIFF: John Doe
DEFENDANT: Jane Smith
COURT: District Court
JUDGE: Hon. Judge
DATE FILED: 2024-01-15
NARRATIVE:
John attacked Jane, who is a minor."""

doc = DocumentParser.parse_text_document(case_text)
result = analyze_case_document(doc)
```

### Option 3: Simple Text Analysis (Legacy)

```python
from minor import run_system

text = "Mary attacked John, who is a minor."
run_system(text, charge="Assault on Minor", theta=0.6)
```

---

## Document Format

Case documents must follow this format:

```
CASE NUMBER: [case identifier]
PLAINTIFF: [name1, name2, ...]
DEFENDANT: [name1, name2, ...]
COURT: [court name]
JUDGE: [judge name]
DATE FILED: [date]
LOCATION: [location]
CHARGES: [charge1, charge2, ...]
NARRATIVE:
[Full case narrative text describing facts, timeline, evidence, etc.]
```

**Important Notes:**
- Each field must be on its own line with a colon separator
- NARRATIVE section can span multiple lines
- Charges are optional but recommended for better analysis
- The narrative should contain action verbs and entity names for extraction

---

## Complete Output Structure

The `analyze_case_document()` function returns a dictionary with:

```python
{
    "document": CaseDocument,           # Original parsed document
    "facts": List[Fact],               # Extracted facts from narrative
    "kb": SymbolicKnowledgeBase,       # Knowledge base with facts & rules
    "reasoning_results": Dict,         # Raw reasoning output per charge
    "case_summary": Dict,              # Structured case summary
    "verdicts": List[VerdictReasoning], # Jury verdicts with confidence
    "report": str,                     # Full text report
    "report_generator": LegalCaseReport # Report object for saving
}
```

---

## Accessing Results

### Get Verdicts

```python
result = analyze_case_document(doc)

for verdict in result['verdicts']:
    print(f"Charge: {verdict.charge}")
    print(f"Verdict: {verdict.verdict}")
    print(f"Confidence: {verdict.confidence * 100:.1f}%")
    print(f"Recommendation: {verdict.recommendation}")
    print(f"Prosecution Score: {verdict.prosecution_score}")
    print(f"Defense Score: {verdict.defense_score}")
    print()
```

### Access Case Summary

```python
summary = result['case_summary']

print("Timeline:")
for event in summary['events']:
    print(f"  [{event['time']}] {event['event']}")

print("\nMitigating Factors:")
for factor in summary['mitigating_factors']:
    print(f"  - {factor}")

print("\nAggravating Factors:")
for factor in summary['aggravating_factors']:
    print(f"  - {factor}")
```

### Get Extracted Facts

```python
facts = result['facts']

for fact in facts:
    print(f"Fact: {fact.predicate}")
    print(f"  Time: {fact.time}")
    print(f"  Confidence: {fact.confidence}")
    print(f"  Entities: {[e.name for e in fact.entities]}")
```

### Access Reasoning Details

```python
reasoning = result['reasoning_results']

for charge, analysis in reasoning.items():
    print(f"Charge: {charge}")
    print(f"  Verdict: {analysis['verdict']}")
    print(f"  Prosecution Score: {analysis['prosecution_score']}")
    print(f"  Defense Score: {analysis['defense_score']}")
    print(f"  Difference: {analysis['difference']:.3f}")
    
    print(f"  Prosecution Arguments:")
    for rule in analysis['prosecution_rules']:
        print(f"    - {rule['name']}: {rule['score']}")
    
    print(f"  Defense Arguments:")
    for rule in analysis['defense_rules']:
        print(f"    - {rule['name']}: {rule['score']}")
```

---

## Customizing Analysis

### Adjust Burden of Proof Threshold

```python
# Stricter (higher burden)
result = analyze_case_document(doc, theta=0.8)

# More lenient
result = analyze_case_document(doc, theta=0.4)
```

### Evaluate Specific Charges

```python
charges = ["Theft", "Fraud"]
result = analyze_case_document(doc, charges_to_evaluate=charges)
```

### Generate Report with Custom Path

```python
result = analyze_case_document(doc)
result['report_generator'].save_report("reports/case_2024_001.txt")
```

---

## Report Structure

The generated report includes:

1. **Header** - Case number, court, judge, date
2. **Case Details** - Parties, charges, case type
3. **Chronological Timeline** - Events with confidence scores
4. **Evidence Analysis** - Actus reus, mens rea, circumstantial evidence
5. **Mitigating/Aggravating Factors** - Contextual factors
6. **Jury Verdicts** - Verdict per charge with detailed reasoning
7. **Legal Analysis** - Methodology and burden of proof explanation
8. **Conclusion** - Summary of findings and recommendations

---

## Confidence Levels Explained

Confidence is calculated from the difference between prosecution and defense scores:

- **0.8-1.0 (Strong)**: Clear evidence, high certainty
- **0.5-0.8 (Moderate)**: Reasonable evidence, moderate certainty
- **0.3-0.5 (Weak)**: Limited evidence, low certainty
- **<0.3 (Insufficient)**: Not enough evidence for clear decision

---

## Sample Workflow

```python
from minor import DocumentParser, analyze_case_document

# 1. Load case document
print("Loading case document...")
doc = DocumentParser.load_from_file("sample_case.txt")

# 2. Analyze with standard burden of proof
print("\nAnalyzing case...")
result = analyze_case_document(doc, theta=0.6)

# 3. Print verdicts
print("\n" + "="*60)
print("JURY VERDICTS")
print("="*60)
for v in result['verdicts']:
    print(f"\n{v.charge}")
    print(f"  Decision: {v.verdict}")
    print(f"  Confidence: {v.confidence*100:.1f}%")

# 4. Save report
print("\nSaving detailed report...")
result['report_generator'].save_report(f"verdict_{doc.case_number}.txt")

# 5. Print first 50 lines of report
report_text = result['report']
print("\n" + "="*60)
print("REPORT PREVIEW")
print("="*60)
print("\n".join(report_text.split("\n")[:50]))
```

---

## Supported Charges

Current system supports:
- Assault
- Aggravated Assault
- Assault on Minor
- Battery
- Theft
- Fraud
- Murder

To add new charges, modify:
1. `NeuralPerceptionModule.actions` - Add action verb mappings
2. `SymbolicKnowledgeBase._initialize_charges()` - Add charge definition
3. `analyze_case_document()` - Add rules for the new charge

---

## Troubleshooting

### No facts extracted
- Ensure narrative contains action verbs (assault, steal, attack, etc.)
- Check that subject/object entities are properly identified
- Try improving entity recognition with enhanced markers

### Low confidence verdicts
- Verify all necessary facts are in the narrative
- Check that rules have appropriate weight values
- Consider adjusting theta threshold

### Missing charges in analysis
- Ensure charges are listed in document CHARGES field
- Verify action verbs appear in the narrative
- Add corresponding rules in `analyze_case_document()`

---

## Advanced: Custom Rules

Add custom inference rules:

```python
from minor import Rule

# In analyze_case_document(), before reasoner step:
kb.add_rule(Rule(
    charge="Theft",
    premises=["Theft(X,Y)", "Premeditation(X)"],
    weight=1.0,
    side="prosecution",
    name="Premeditated Theft",
    description="Evidence shows theft was planned in advance"
))
```

---

## Python Version Requirements

- Python 3.10+ recommended
- Python 3.14 not currently compatible (spacy/pydantic v1 issue)
- Required packages: spacy, en_core_web_sm model

Install dependencies:
```bash
pip install spacy
python -m spacy download en_core_web_sm
```
