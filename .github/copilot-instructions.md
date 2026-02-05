# AI Coding Agent Instructions

## Project Overview
This is a **Neuro-Symbolic AI system** for comprehensive legal case analysis. It combines neural NLP (spacy) for fact extraction with symbolic logic for evidence evaluation, jury decision-making, and comprehensive report generation. The system supports analyzing complete case documents and generating detailed legal verdicts.

**Key Components:**
- **Document Parser** (`DocumentParser`, `CaseDocument`): Loads and parses legal case documents from text files
- **Neural Perception Module** (`NeuralPerceptionModule`): Uses spacy NLP to extract events, entities, and facts from unstructured case narratives
- **Symbolic Knowledge Base** (`SymbolicKnowledgeBase`): Stores grounded facts and legal inference rules
- **Reasoning Engine** (`BurdenOfProofReasoner`): Evaluates charges using burden of proof logic with prosecution/defense weighting
- **Jury Decision System** (`JuryDecision`): Determines verdicts with confidence levels
- **Case Summarizer** (`CaseSummarizer`): Generates structured summaries of case details, timelines, evidence, and applicable charges
- **Report Generator** (`LegalCaseReport`): Creates comprehensive legal analysis reports with verdicts

## Architecture: Clean Neural/Symbolic Separation

### Layer 0: Document Loading
- Class: `DocumentParser`, `CaseDocument`
- Input: Text file or string with structured case information
- Output: `CaseDocument` with metadata and narrative
- Supported format: CASE NUMBER, PLAINTIFF, DEFENDANT, COURT, JUDGE, DATE FILED, CHARGES, NARRATIVE

### Layer 1: Neural Extraction
- Class: `NeuralPerceptionModule`
- Input: Raw case narrative text
- Output: `List[Fact]` with predicates, timestamps, confidence scores, entities
- Action extraction: Maps verbs ("assault", "steal", "deceive") to action types
- Entity extraction: Identifies person status (minor/adult), weapons, property using lemma patterns
- Pattern: `predicate = f"{action.capitalize()}({subject},{object})"` (e.g., `"Assault(Mary,John)"`)

### Layer 2: Symbolic Grounding & Reasoning
- Classes: `SymbolicKnowledgeBase`, `Rule`, `BurdenOfProofReasoner`
- Grounding: Neural facts → KB facts with probabilities
- Rules encode legal domain knowledge with `side="prosecution"` or `side="defense"`
- Score formula: `min(premise_confidences) * rule_weight` (all premises must be satisfied)
- Verdict formula: `prosecution_score - defense_score >= theta` → "Guilty" (theta default=0.6)

### Layer 3: Jury Decision & Confidence
- Class: `JuryDecision`
- Calculates confidence levels: `confidence = min(1.0, abs(difference) / theta)`
- Generates recommendations: "Guilty (Strong Evidence)" vs "Insufficient Evidence"
- Returns `List[VerdictReasoning]` with detailed justifications

### Layer 4: Case Summarization & Reporting
- Classes: `CaseSummarizer`, `LegalCaseReport`
- Generates: parties, chronological timeline, applicable charges, evidence categorization, mitigating/aggravating factors
- Report includes: full case analysis, verdict reasoning, methodology, and recommendations
- Saves to file for distribution

## Workflow: Document to Verdict

```
Case Document (file/string)
    ↓
DocumentParser.parse_text_document() or load_from_file()
    ↓
CaseDocument object
    ↓
analyze_case_document()
    ├─ NeuralPerceptionModule.extract_facts()
    ├─ SymbolicKnowledgeBase + Rules
    ├─ BurdenOfProofReasoner.evaluate_charge()
    ├─ JuryDecision.determine_verdicts()
    ├─ CaseSummarizer.generate_summary()
    ├─ LegalCaseReport.generate_full_report()
    └─ Returns: Facts, KB, Verdicts, Summary, Report
    ↓
Report File + Verdict Results
```

## Usage Examples

### Load and Analyze Case Document
```python
from minor import DocumentParser, analyze_case_document

# Load from file
doc = DocumentParser.load_from_file("case.txt")

# Analyze (threshold: 0.6 = default burden of proof)
result = analyze_case_document(doc, theta=0.6)

# Access verdicts
for verdict in result['verdicts']:
    print(f"{verdict.charge}: {verdict.verdict} ({verdict.confidence*100:.1f}%)")

# Save detailed report
result['report_generator'].save_report("verdict_report.txt")
```

### Parse Case from String
```python
case_text = """CASE NUMBER: 2024-001
PLAINTIFF: State
DEFENDANT: John Doe
COURT: District Court
JUDGE: Hon. Judge
DATE FILED: 2024-01-15
CHARGES: Theft, Fraud
NARRATIVE:
John stole $5000 from the bank. He deceived employees by using a fake ID."""

doc = DocumentParser.parse_text_document(case_text)
result = analyze_case_document(doc)
```

## Generalized Design for Multiple Charges

### Adding New Charges
1. Add to `SymbolicKnowledgeBase._initialize_charges()`:
   ```python
   "Charge_Name": {
       "description": "Legal definition",
       "elements": ["Element1", "Element2"]
   }
   ```

2. Add action verb to `NeuralPerceptionModule.actions`:
   ```python
   "charge_action": ["verb1", "verb2", ...]
   ```

3. Add rules in `analyze_case_document()`:
   ```python
   kb.add_rule(Rule(
       charge="Charge_Name",
       premises=["ExtractedFact(X,Y)"],
       weight=0.9,
       side="prosecution",
       name="Rule Name",
       description="Why this applies"
   ))
   ```

### Action Types Currently Supported
- `"assault"`: assault, attack, hit, punch, strike
- `"theft"`: steal, rob, take, shoplifted
- `"battery"`: beat, struck, kicked
- `"murder"`: kill, murdered, slayed
- `"fraud"`: deceive, defraud, scam, cheated

### Entity Types Currently Supported
- `"minor"`: minor, child, juvenile, kid, boy, girl
- `"weapon"`: gun, knife, weapon, pistol
- `"property"`: money, car, house, property
- `"adult"`: adult, man, woman

## Key Patterns & Critical Gotchas

1. **Document Format**: Must follow structured format with CASE NUMBER, PLAINTIFF, DEFENDANT, etc.
2. **Fact Predicate Format**: Must use exact syntax `"Predicate(X,Y)"` for parsing. Inconsistency breaks rule matching.
3. **Min-Aggregation Logic**: If ANY premise is missing from KB, rule scores zero. Use conservative confidence thresholds when grounding.
4. **Theta Sensitivity**: Verdict flips at `difference >= theta`. Typical: 0.6 (60% prosecution advantage needed). Lower theta = more guilty verdicts.
5. **Temporal Reasoning**: `TemporalReasoner.valid_self_defense()` checks if accused was victim (attacked time) before attacker (defended time).
6. **Confidence Calculation**: `confidence = min(1.0, abs(difference) / theta)`. Higher theta = lower confidence for same score margin.

## File Organization

| File | Purpose |
|------|---------|
| `minor.py` | Complete production system with document parsing, analysis, jury decision, and reporting |
| `analyze_case.py` | Example script: load case document and generate verdict report |
| `sample_case.txt` | Sample case document demonstrating required format |
| `neuro_symbolic_abstrat.ipynb` | Iterative exploration: 9 cells building from basic extraction to full reasoning |
| `USAGE_GUIDE.md` | Comprehensive usage guide with examples and API reference |
| `EXPANSION_GUIDE.md` | Guide for extending the system with new charges and patterns |

## Development Workflow

- **Analyze new case**: `DocumentParser.load_from_file()` → `analyze_case_document()` → save report
- **Add new charges**: Update dicts in `NeuralPerceptionModule` and `SymbolicKnowledgeBase`, add rules
- **Customize verdict threshold**: Pass `theta` parameter (0.4-0.8 typical range)
- **Extract structured results**: Access `result['verdicts']`, `result['case_summary']`, `result['reasoning_results']`
- **Generate reports**: Use `LegalCaseReport.save_report()` for text output

## Dependencies
- **spacy** (en_core_web_sm model): NLP, dependency parsing for subject/object extraction
- Python 3.10+ (3.14 has compatibility issues with current spacy version)
- Pure symbolic logic after grounding—no ML training required
- No external dependencies beyond spacy for report generation
