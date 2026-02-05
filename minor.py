import spacy
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from enum import Enum
from pathlib import Path
from datetime import datetime

nlp = spacy.load("en_core_web_sm")

# ============================================================================
# DOCUMENT MODEL: Case Document Representation
# ============================================================================

@dataclass
class CaseDocument:
    """Represents a legal case document"""
    case_number: str
    parties_plaintiff: List[str]
    parties_defendant: List[str]
    court: str
    judge: str
    date_filed: str
    narrative: str
    charges: List[str] = field(default_factory=list)
    location: str = ""
    case_type: str = ""
    
    def __str__(self) -> str:
        return f"Case #{self.case_number}: {self.parties_plaintiff} v. {self.parties_defendant}"


class DocumentParser:
    """Parses case documents from text files or structured formats"""
    
    @staticmethod
    def parse_text_document(text: str) -> Optional[CaseDocument]:
        """
        Parse a text document with structured case information.
        
        Expected format:
        CASE NUMBER: XXX
        PLAINTIFF: name1, name2
        DEFENDANT: name3, name4
        COURT: court name
        JUDGE: judge name
        DATE FILED: date
        LOCATION: location
        CHARGES: charge1, charge2
        NARRATIVE:
        [Case narrative text...]
        """
        doc_dict = {}
        current_section = None
        narrative_lines = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Parse key-value sections
            if ':' in line and not current_section == "NARRATIVE":
                key, value = line.split(':', 1)
                key = key.strip().upper()
                value = value.strip()
                
                if key == "CASE NUMBER":
                    doc_dict['case_number'] = value
                elif key == "PLAINTIFF":
                    doc_dict['parties_plaintiff'] = [p.strip() for p in value.split(',')]
                elif key == "DEFENDANT":
                    doc_dict['parties_defendant'] = [p.strip() for p in value.split(',')]
                elif key == "COURT":
                    doc_dict['court'] = value
                elif key == "JUDGE":
                    doc_dict['judge'] = value
                elif key == "DATE FILED":
                    doc_dict['date_filed'] = value
                elif key == "LOCATION":
                    doc_dict['location'] = value
                elif key == "CHARGES":
                    doc_dict['charges'] = [c.strip() for c in value.split(',')]
                elif key == "NARRATIVE":
                    current_section = "NARRATIVE"
            elif current_section == "NARRATIVE":
                narrative_lines.append(line)
        
        if narrative_lines:
            doc_dict['narrative'] = ' '.join(narrative_lines)
        
        # Create document with defaults
        return CaseDocument(
            case_number=doc_dict.get('case_number', 'UNKNOWN'),
            parties_plaintiff=doc_dict.get('parties_plaintiff', []),
            parties_defendant=doc_dict.get('parties_defendant', []),
            court=doc_dict.get('court', 'Unknown Court'),
            judge=doc_dict.get('judge', 'Unknown Judge'),
            date_filed=doc_dict.get('date_filed', 'Unknown'),
            narrative=doc_dict.get('narrative', ''),
            charges=doc_dict.get('charges', []),
            location=doc_dict.get('location', ''),
            case_type=doc_dict.get('case_type', 'Criminal')
        )
    
    @staticmethod
    def load_from_file(filepath: str) -> Optional[CaseDocument]:
        """Load and parse a case document from file"""
        try:
            path = Path(filepath)
            if not path.exists():
                print(f"❌ File not found: {filepath}")
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            return DocumentParser.parse_text_document(text)
        except Exception as e:
            print(f"❌ Error loading document: {e}")
            return None

@dataclass
class Entity:
    """Extracted entity with confidence"""
    name: str
    entity_type: str  # "person", "object", "location", etc.
    confidence: float

@dataclass
class Fact:
    """Extracted fact with temporal and confidence metadata"""
    predicate: str  # e.g., "Assault(X,Y)"
    time: int
    confidence: float
    entities: List[Entity]

class NeuralPerceptionModule:
    """Extracts events, entities, and facts from text using spacy NLP"""
    
    def __init__(self):
        self.actions = {
            "assault": ["assault", "attack", "hit", "punch", "strike"],
            "theft": ["steal", "rob", "take", "shoplifted"],
            "battery": ["beat", "struck", "kicked"],
            "murder": ["kill", "murdered", "slayed"],
            "fraud": ["deceive", "defraud", "scam", "cheated"],
        }
        self.entity_markers = {
            "minor": ["minor", "child", "juvenile", "kid", "boy", "girl"],
            "adult": ["adult", "man", "woman"],
            "weapon": ["gun", "knife", "weapon", "pistol"],
            "property": ["money", "car", "house", "property"],
        }
    
    def extract_entities(self, doc) -> Dict[str, List[Entity]]:
        """Extract named entities and attribute entities"""
        entities = defaultdict(list)
        
        for token in doc:
            # Property entities
            if token.lemma_ in self.entity_markers["property"]:
                entities["property"].append(
                    Entity(token.text, "property", 0.85)
                )
            # Status entities
            if token.lemma_ in self.entity_markers["minor"]:
                entities["minor"].append(
                    Entity(token.text, "minor", 0.9)
                )
            if token.lemma_ in self.entity_markers["weapon"]:
                entities["weapon"].append(
                    Entity(token.text, "weapon", 0.88)
                )
        
        return entities
    
    def extract_facts(self, text: str) -> List[Fact]:
        """Extract facts from text using dependency parsing"""
        doc = nlp(text)
        facts = []
        time = 1
        extracted_entities = self.extract_entities(doc)
        
        for sent in doc.sents:
            attacker = None
            victim = None
            action = None
            
            for token in sent:
                # Identify action
                for action_type, verbs in self.actions.items():
                    if token.lemma_ in verbs:
                        action = action_type
                        # Extract subject (attacker) and object (victim)
                        for child in token.children:
                            if child.dep_ == "nsubj":
                                attacker = child.text
                            if child.dep_ in ["dobj", "pobj"]:
                                victim = child.text
                        break
            
            if action and attacker and victim:
                predicate = f"{action.capitalize()}({attacker},{victim})"
                fact = Fact(
                    predicate=predicate,
                    time=time,
                    confidence=0.85,
                    entities=extracted_entities.get(action, [])
                )
                facts.append(fact)
                time += 1
        
        return facts


# ============================================================================
# SYMBOLIC LAYER: Knowledge Base & Inference Rules
# ============================================================================

class Rule:
    """Represents a legal inference rule"""
    def __init__(self, charge: str, premises: List[str], weight: float, 
                 side: str, name: str, description: str = ""):
        self.charge = charge
        self.premises = premises
        self.weight = weight
        self.side = side  # "prosecution" or "defense"
        self.name = name
        self.description = description


class SymbolicKnowledgeBase:
    """Stores facts and legal inference rules"""
    def __init__(self):
        self.facts: Dict[str, float] = {}  # fact -> probability
        self.rules: Dict[str, List[Rule]] = defaultdict(list)
        self.charge_definitions = self._initialize_charges()
    
    def _initialize_charges(self) -> Dict[str, Dict]:
        """Define legal charges and their elements"""
        return {
            "Assault": {
                "description": "Intentional act causing apprehension of harmful contact",
                "elements": ["Assault(X,Y)"]
            },
            "Aggravated Assault": {
                "description": "Assault causing serious bodily injury or with weapon",
                "elements": ["Assault(X,Y)", "SeriousBodily(Y)", "OR", "Weapon(X)"]
            },
            "Battery": {
                "description": "Intentional physical contact of an offensive nature",
                "elements": ["Battery(X,Y)", "Physical(X,Y)"]
            },
            "Assault on Minor": {
                "description": "Assault against a person under 18",
                "elements": ["Assault(X,Y)", "Minor(Y)"]
            },
            "Theft": {
                "description": "Unlawful taking of property with intent to deprive",
                "elements": ["Theft(X,Y)", "Property(Y)"]
            },
            "Fraud": {
                "description": "Intentional misrepresentation for unlawful gain",
                "elements": ["Fraud(X,Y)"]
            },
        }
    
    def add_fact(self, fact: str, probability: float):
        """Add grounded fact to KB"""
        self.facts[fact] = probability
    
    def add_rule(self, rule: Rule):
        """Add inference rule to KB"""
        self.rules[rule.charge].append(rule)


class TemporalReasoner:
    """Handles temporal constraints (e.g., self-defense timing)"""
    
    @staticmethod
    def valid_self_defense(facts: List[Fact], accused: str) -> bool:
        """
        Self-defense valid if accused was attacked BEFORE they attacked.
        Returns True if temporal sequence supports self-defense claim.
        """
        attacked_time = None
        defended_time = None
        
        for fact in facts:
            # Check if accused was victim first (attacked)
            if fact.predicate.endswith(f",{accused})"):
                attacked_time = fact.time
            # Check if accused was attacker (defended)
            if fact.predicate.startswith(f"Assault({accused},"):
                defended_time = fact.time
        
        if attacked_time and defended_time:
            return attacked_time < defended_time
        return False
    
    @staticmethod
    def check_temporal_constraint(facts: List[Fact], constraint_name: str, 
                                  params: Dict) -> bool:
        """
        Generalized temporal constraint checking.
        constraint_name examples: "before", "after", "within_minutes", etc.
        """
        # Placeholder for extensible temporal reasoning
        return True


class BurdenOfProofReasoner:
    """Evaluates charges using burden of proof with prosecution/defense weighting"""
    
    def __init__(self, kb: SymbolicKnowledgeBase):
        self.kb = kb
    
    def evaluate_charge(self, charge: str, theta: float = 0.6) -> Dict:
        """
        Evaluate a charge using burden of proof.
        
        Logic:
        - For each rule, compute score = min(premise_probabilities) * rule_weight
        - Aggregate scores by side (prosecution vs defense)
        - Verdict: guilty if prosecution_score - defense_score >= theta
        
        Returns dict with verdict, scores, and explanation
        """
        scores = defaultdict(float)
        explanations = defaultdict(list)
        
        for rule in self.kb.rules[charge]:
            probs = []
            for premise in rule.premises:
                if premise not in self.kb.facts:
                    break  # Premise not satisfied
                probs.append(self.kb.facts[premise])
            else:
                # All premises satisfied
                rule_score = min(probs) * rule.weight
                scores[rule.side] += rule_score
                explanations[rule.side].append({
                    "name": rule.name,
                    "description": rule.description,
                    "score": round(rule_score, 3),
                    "weight": rule.weight,
                    "premises": rule.premises
                })
        
        diff = scores["prosecution"] - scores["defense"]
        verdict = "Guilty" if diff >= theta else "Not Guilty"
        
        return {
            "verdict": verdict,
            "prosecution_score": round(scores["prosecution"], 3),
            "defense_score": round(scores["defense"], 3),
            "difference": round(diff, 3),
            "theta": theta,
            "prosecution_rules": explanations["prosecution"],
            "defense_rules": explanations["defense"],
        }


# ============================================================================
# CASE SUMMARIZER: Generate Legal Case Summary
# ============================================================================

class CaseSummarizer:
    """Generates structured case summary from extracted facts"""
    
    def __init__(self, facts: List[Fact], entities_by_role: Dict[str, str]):
        self.facts = facts
        self.entities_by_role = entities_by_role  # {"accused": "X", "victim": "Y", etc.}
    
    def generate_summary(self) -> Dict:
        """Generate comprehensive case summary"""
        return {
            "parties": self._extract_parties(),
            "events": self._extract_timeline(),
            "charges_available": self._identify_applicable_charges(),
            "key_evidence": self._extract_key_evidence(),
            "mitigating_factors": self._identify_mitigating_factors(),
            "aggravating_factors": self._identify_aggravating_factors(),
            "summary_text": self._generate_narrative()
        }
    
    def _extract_parties(self) -> Dict[str, str]:
        """Extract involved parties with roles"""
        return self.entities_by_role
    
    def _extract_timeline(self) -> List[Dict]:
        """Generate chronological timeline of events"""
        timeline = []
        for fact in self.facts:
            timeline.append({
                "time": fact.time,
                "event": fact.predicate,
                "confidence": fact.confidence,
                "entities": [e.name for e in fact.entities]
            })
        return timeline
    
    def _identify_applicable_charges(self) -> List[str]:
        """Identify which charges could apply based on facts"""
        applicable = []
        for fact in self.facts:
            if "Assault" in fact.predicate:
                applicable.extend(["Assault", "Aggravated Assault"])
            if "Battery" in fact.predicate:
                applicable.append("Battery")
            if "Theft" in fact.predicate:
                applicable.append("Theft")
            if "Fraud" in fact.predicate:
                applicable.append("Fraud")
            if "Murder" in fact.predicate:
                applicable.append("Murder")
        return list(set(applicable))
    
    def _extract_key_evidence(self) -> Dict[str, List]:
        """Extract evidence by category"""
        evidence = {
            "actus_reus": [],  # guilty act
            "mens_rea": [],     # guilty mind (intent)
            "circumstantial": [],
        }
        
        for fact in self.facts:
            # This is simplified; real implementation would categorize deeper
            evidence["actus_reus"].append(fact.predicate)
        
        return evidence
    
    def _identify_mitigating_factors(self) -> List[str]:
        """Identify potential mitigating factors"""
        factors = []
        
        # Check for self-defense pattern
        for fact in self.facts:
            if "Assault" in fact.predicate:
                accused = fact.predicate.split("(")[1].split(",")[0]
                victim = fact.predicate.split(",")[1].rstrip(")")
                # If victim attacks first, could be self-defense
                for other_fact in self.facts:
                    if other_fact.time < fact.time and victim in other_fact.predicate:
                        factors.append("Potential self-defense claim")
        
        return factors
    
    def _identify_aggravating_factors(self) -> List[str]:
        """Identify potential aggravating factors"""
        factors = []
        
        for fact in self.facts:
            # Check for weapon use
            if any(e.entity_type == "weapon" for e in fact.entities):
                factors.append("Use of weapon")
            # Check for minor victim
            if any(e.entity_type == "minor" for e in fact.entities):
                factors.append("Victim is a minor")
            # Check for property value
            if any(e.entity_type == "property" for e in fact.entities):
                factors.append("Crime against property")
        
        return factors
    
    def _generate_narrative(self) -> str:
        """Generate plain English summary of case"""
        narrative = "Case Summary:\n"
        for fact in sorted(self.facts, key=lambda f: f.time):
            narrative += f"  {fact.time}. {fact.predicate} (confidence: {fact.confidence})\n"
        return narrative


# ============================================================================
# JURY DECISION SYSTEM: Verdict with Confidence & Reasoning
# ============================================================================

@dataclass
class VerdictReasoning:
    """Detailed reasoning for a verdict"""
    charge: str
    verdict: str
    confidence: float
    prosecution_score: float
    defense_score: float
    prosecution_arguments: List[Dict]
    defense_arguments: List[Dict]
    theta_threshold: float
    recommendation: str  # "Guilty", "Not Guilty", "Insufficient Evidence"

class JuryDecision:
    """Simulates jury decision-making based on evidence"""
    
    def __init__(self, reasoning_results: Dict[str, Dict]):
        self.reasoning_results = reasoning_results
        self.verdicts: List[VerdictReasoning] = []
    
    def determine_verdicts(self, theta: float = 0.6) -> List[VerdictReasoning]:
        """
        Determine jury verdicts for all charges with confidence levels.
        
        Confidence score derived from:
        - Difference between prosecution and defense scores
        - Strength of evidence
        - Evidence consistency
        """
        self.verdicts = []
        
        for charge, result in self.reasoning_results.items():
            # Calculate confidence based on score margin
            diff = result["difference"]
            confidence = min(1.0, abs(diff) / theta) if theta > 0 else 0
            
            # Create reasoning object
            reasoning = VerdictReasoning(
                charge=charge,
                verdict=result["verdict"],
                confidence=round(confidence, 3),
                prosecution_score=result["prosecution_score"],
                defense_score=result["defense_score"],
                prosecution_arguments=result["prosecution_rules"],
                defense_arguments=result["defense_rules"],
                theta_threshold=result["theta"],
                recommendation=self._get_recommendation(result["verdict"], confidence)
            )
            self.verdicts.append(reasoning)
        
        return self.verdicts
    
    @staticmethod
    def _get_recommendation(verdict: str, confidence: float) -> str:
        """Generate jury recommendation based on verdict and confidence"""
        if confidence < 0.3:
            return "Insufficient Evidence"
        elif verdict == "Guilty":
            if confidence >= 0.8:
                return "Guilty (Strong Evidence)"
            else:
                return "Guilty (Moderate Evidence)"
        else:
            if confidence >= 0.8:
                return "Not Guilty (Strong Evidence)"
            else:
                return "Not Guilty (Weak Evidence)"


# ============================================================================
# REPORT GENERATION: Complete Legal Case Report
# ============================================================================

class LegalCaseReport:
    """Generates comprehensive legal case analysis report"""
    
    def __init__(self, document: CaseDocument, case_summary: Dict, 
                 verdicts: List[VerdictReasoning]):
        self.document = document
        self.case_summary = case_summary
        self.verdicts = verdicts
        self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_full_report(self) -> str:
        """Generate complete analysis report"""
        report = []
        report.append(self._header())
        report.append(self._case_details())
        report.append(self._timeline())
        report.append(self._evidence_analysis())
        report.append(self._jury_verdicts())
        report.append(self._legal_analysis())
        report.append(self._conclusion())
        report.append(self._footer())
        
        return "\n".join(report)
    
    def _header(self) -> str:
        """Generate report header"""
        header = f"""
{'='*80}
LEGAL CASE ANALYSIS REPORT
{'='*80}
Generated: {self.generated_at}
Case Number: {self.document.case_number}
Court: {self.document.court}
Judge: {self.document.judge}
Date Filed: {self.document.date_filed}
Location: {self.document.location}
{'='*80}
"""
        return header
    
    def _case_details(self) -> str:
        """Generate case details section"""
        section = f"""
CASE DETAILS
{'-'*80}
PARTIES:
  Plaintiff(s): {', '.join(self.document.parties_plaintiff)}
  Defendant(s): {', '.join(self.document.parties_defendant)}

CHARGES:
"""
        for charge in self.document.charges or self.case_summary.get('charges_available', []):
            section += f"  • {charge}\n"
        
        section += f"""
CASE TYPE: {self.document.case_type}
"""
        return section
    
    def _timeline(self) -> str:
        """Generate event timeline section"""
        section = f"""
CHRONOLOGICAL TIMELINE
{'-'*80}
"""
        for event in self.case_summary.get('events', []):
            section += f"""
  [{event['time']}] {event['event']}
       Confidence: {event['confidence']}
       Entities: {', '.join(event['entities']) if event['entities'] else 'N/A'}
"""
        return section
    
    def _evidence_analysis(self) -> str:
        """Generate evidence analysis section"""
        section = f"""
EVIDENCE ANALYSIS
{'-'*80}
"""
        evidence = self.case_summary.get('key_evidence', {})
        
        if evidence.get('actus_reus'):
            section += f"\nGuilty Act (Actus Reus):\n"
            for act in evidence['actus_reus']:
                section += f"  • {act}\n"
        
        if evidence.get('mens_rea'):
            section += f"\nGuilty Mind (Mens Rea):\n"
            for mind in evidence['mens_rea']:
                section += f"  • {mind}\n"
        
        if evidence.get('circumstantial'):
            section += f"\nCircumstantial Evidence:\n"
            for circ in evidence['circumstantial']:
                section += f"  • {circ}\n"
        
        aggravating = self.case_summary.get('aggravating_factors', [])
        if aggravating:
            section += f"\nAggravating Factors:\n"
            for factor in aggravating:
                section += f"  • {factor}\n"
        
        mitigating = self.case_summary.get('mitigating_factors', [])
        if mitigating:
            section += f"\nMitigating Factors:\n"
            for factor in mitigating:
                section += f"  • {factor}\n"
        
        return section
    
    def _jury_verdicts(self) -> str:
        """Generate jury verdicts section"""
        section = f"""
JURY VERDICTS & FINDINGS
{'-'*80}
"""
        for verdict in self.verdicts:
            section += f"""
CHARGE: {verdict.charge}
{'-'*40}
  Verdict: {verdict.verdict}
  Recommendation: {verdict.recommendation}
  Confidence Level: {verdict.confidence * 100:.1f}%
  
  Prosecution Score: {verdict.prosecution_score}
  Defense Score: {verdict.defense_score}
  Difference: {verdict.prosecution_score - verdict.defense_score:.3f}
  Threshold: {verdict.theta_threshold}

  PROSECUTION ARGUMENTS:
"""
            for arg in verdict.prosecution_arguments:
                section += f"""    • {arg['name']}: {arg['score']} (weight: {arg['weight']})
       {arg['description']}
"""
            section += f"\n  DEFENSE ARGUMENTS:\n"
            for arg in verdict.defense_arguments:
                section += f"""    • {arg['name']}: {arg['score']} (weight: {arg['weight']})
       {arg['description']}
"""
        
        return section
    
    def _legal_analysis(self) -> str:
        """Generate legal analysis section"""
        section = f"""
LEGAL ANALYSIS
{'-'*80}

APPLICABLE CHARGES:
"""
        for charge in self.case_summary.get('charges_available', []):
            section += f"  • {charge}\n"
        
        section += f"""
BURDEN OF PROOF:
  The burden of proof in criminal proceedings is "beyond a reasonable doubt."
  This system uses a threshold ({self.verdicts[0].theta_threshold if self.verdicts else 0.6}) to model this standard.
  
  Prosecution Score: Evidence supporting guilt
  Defense Score: Evidence supporting innocence
  Verdict: Guilty if (Prosecution - Defense) >= Threshold

METHODOLOGY:
  1. Neural Extraction: Extracts facts from case narrative
  2. Symbolic Grounding: Maps facts to legal predicates
  3. Rule-Based Reasoning: Applies legal inference rules
  4. Burden of Proof: Evaluates evidence strength
  5. Jury Decision: Determines verdict with confidence
"""
        return section
    
    def _conclusion(self) -> str:
        """Generate conclusion section"""
        section = f"""
CONCLUSION
{'-'*80}

SUMMARY OF FINDINGS:
"""
        guilty_count = sum(1 for v in self.verdicts if v.verdict == "Guilty")
        not_guilty_count = len(self.verdicts) - guilty_count
        
        section += f"""
  Total Charges: {len(self.verdicts)}
  Guilty Verdicts: {guilty_count}
  Not Guilty Verdicts: {not_guilty_count}
  Average Confidence: {round(sum(v.confidence for v in self.verdicts) / len(self.verdicts) * 100, 1) if self.verdicts else 0}%

RECOMMENDATIONS:
  This analysis is intended for educational/reference purposes only.
  Actual legal proceedings require qualified legal representation and proper court jurisdiction.
"""
        return section
    
    def _footer(self) -> str:
        """Generate report footer"""
        footer = f"""
{'='*80}
END OF REPORT
{'='*80}
"""
        return footer
    
    def save_report(self, filepath: str) -> bool:
        """Save report to file"""
        try:
            report = self.generate_full_report()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✓ Report saved to: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return False

# ============================================================================
# MAIN PIPELINE: Complete Analysis from Text or Document
# ============================================================================

def analyze_case_document(document: CaseDocument, theta: float = 0.6, 
                         charges_to_evaluate: List[str] = None) -> Dict:
    """
    Complete pipeline for case document analysis:
    Extract → Ground → Reason → Summarize → Jury Decision → Report
    
    Args:
        document: CaseDocument object
        theta: Burden of proof threshold (default 0.6)
        charges_to_evaluate: Specific charges to evaluate (None = all)
    
    Returns:
        Dict with facts, KB, verdicts, summary, and report
    """
    print("=" * 80)
    print("LEGAL CASE ANALYSIS SYSTEM")
    print("=" * 80)
    print(f"Case: {document}")
    print()
    
    # STEP 1: Neural Extraction
    print("[NEURAL LAYER] Extracting facts from case narrative...")
    neural = NeuralPerceptionModule()
    facts = neural.extract_facts(document.narrative)
    
    print(f"Extracted {len(facts)} facts:")
    for fact in facts:
        print(f"  • {fact.predicate} @ t={fact.time} (confidence: {fact.confidence})")
    
    if not facts:
        print("⚠ No facts extracted from narrative. Proceeding with document-level analysis.")
        facts = []
    
    # Identify key entities
    accused = facts[-1].predicate.split("(")[1].split(",")[0] if facts else document.parties_defendant[0] if document.parties_defendant else "Defendant"
    victim = facts[-1].predicate.split(",")[1].rstrip(")") if facts else document.parties_plaintiff[0] if document.parties_plaintiff else "Plaintiff"
    
    # STEP 2: Build Symbolic KB
    print("\n[SYMBOLIC LAYER] Grounding facts in knowledge base...")
    kb = SymbolicKnowledgeBase()
    
    # Add extracted facts
    for fact in facts:
        kb.add_fact(fact.predicate, fact.confidence)
        print(f"  ✓ Added: {fact.predicate}")
    
    # Check for minor status
    minor_status = "Minor" if any(e.entity_type == "minor" for fact in facts for e in fact.entities) else "Adult"
    kb.add_fact(f"Status({victim}, {minor_status})", 0.9)
    print(f"  ✓ Added: Status({victim}, {minor_status})")
    
    # STEP 3: Add Rules based on charges
    print("\n[RULES] Loading legal inference rules...")
    
    if not charges_to_evaluate:
        charges_to_evaluate = document.charges if document.charges else ["Assault on Minor"]
    
    for charge in charges_to_evaluate:
        # ASSAULT CHARGES
        if charge in ["Assault on Minor", "Assault", "Aggravated Assault", "Battery"]:
            if facts and any(f"Assault({accused},{victim})" in f.predicate for f in facts):
                kb.add_rule(Rule(
                    charge=charge,
                    premises=[f"Assault({accused},{victim})", f"Status({victim}, {minor_status})"],
                    weight=0.9,
                    side="prosecution",
                    name="Direct Assault Evidence",
                    description="Defendant committed assault against victim"
                ))
            elif facts and any(f"Battery({accused},{victim})" in f.predicate for f in facts):
                kb.add_rule(Rule(
                    charge=charge,
                    premises=[f"Battery({accused},{victim})"],
                    weight=0.85,
                    side="prosecution",
                    name="Direct Battery Evidence",
                    description="Defendant committed battery against victim"
                ))
        
        # THEFT CHARGES
        elif charge in ["Theft", "Robbery"]:
            if facts and any("Theft" in f.predicate for f in facts):
                kb.add_rule(Rule(
                    charge=charge,
                    premises=[f"Theft({accused},{victim})"],
                    weight=0.9,
                    side="prosecution",
                    name="Direct Theft Evidence",
                    description="Defendant committed theft of victim's property"
                ))
        
        # FRAUD CHARGES
        elif charge == "Fraud":
            if facts and any("Fraud" in f.predicate or "Deceive" in f.predicate for f in facts):
                kb.add_rule(Rule(
                    charge=charge,
                    premises=[f.predicate for f in facts if "Fraud" in f.predicate or "Deceive" in f.predicate],
                    weight=0.85,
                    side="prosecution",
                    name="Fraudulent Conduct",
                    description="Defendant engaged in fraudulent deception"
                ))
        
        # MURDER CHARGES
        elif charge == "Murder":
            if facts and any("Murder" in f.predicate or "Kill" in f.predicate for f in facts):
                kb.add_rule(Rule(
                    charge=charge,
                    premises=[f.predicate for f in facts if "Murder" in f.predicate or "Kill" in f.predicate],
                    weight=1.0,
                    side="prosecution",
                    name="Homicide Evidence",
                    description="Defendant caused death of victim"
                ))
        
        # Self-defense defense
        if charge in ["Assault on Minor", "Assault", "Battery", "Aggravated Assault"]:
            if TemporalReasoner.valid_self_defense(facts, accused):
                kb.add_fact(f"ValidSelfDefense({accused})", 0.8)
                kb.add_rule(Rule(
                    charge=charge,
                    premises=[f"ValidSelfDefense({accused})"],
                    weight=1.0,
                    side="defense",
                    name="Valid Self-Defense",
                    description="Defendant acted in lawful self-defense"
                ))
                print(f"  ✓ Self-defense valid (temporal ordering supports)")
    
    # STEP 4: Reason & Evaluate
    print("\n[REASONING] Evaluating charges using burden of proof...")
    reasoner = BurdenOfProofReasoner(kb)
    
    results = {}
    for charge_type in charges_to_evaluate:
        if kb.rules[charge_type]:
            result = reasoner.evaluate_charge(charge_type, theta)
            results[charge_type] = result
            
            print(f"\n  Charge: {charge_type}")
            print(f"    Verdict: {result['verdict']}")
            print(f"    Prosecution: {result['prosecution_score']} | Defense: {result['defense_score']} | Diff: {result['difference']:.3f}")
    
    # STEP 5: Generate Case Summary
    print("\n[SUMMARY] Generating case summary...")
    summarizer = CaseSummarizer(facts, {"accused": accused, "victim": victim})
    case_summary = summarizer.generate_summary()
    
    # STEP 6: Jury Decision
    print("\n[JURY] Determining verdict...")
    jury = JuryDecision(results)
    verdicts = jury.determine_verdicts(theta)
    
    for verdict in verdicts:
        print(f"  {verdict.charge}: {verdict.verdict}")
        print(f"    → Confidence: {verdict.confidence * 100:.1f}%")
        print(f"    → Recommendation: {verdict.recommendation}")
    
    # STEP 7: Generate Report
    print("\n[REPORT] Generating comprehensive analysis report...")
    report = LegalCaseReport(document, case_summary, verdicts)
    full_report = report.generate_full_report()
    
    print("\n" + "=" * 80)
    return {
        "document": document,
        "facts": facts,
        "kb": kb,
        "reasoning_results": results,
        "case_summary": case_summary,
        "verdicts": verdicts,
        "report": full_report,
        "report_generator": report
    }


def run_system(text: str, charge: str = None, theta: float = 0.6):
    """
    Simple pipeline for raw text input (backward compatible)
    
    Args:
        text: Input case narrative
        charge: Specific charge to evaluate (None = evaluate all applicable)
        theta: Burden of proof threshold (default 0.6)
    """
    print("=" * 70)
    print("LEGAL REASONING SYSTEM")
    print("=" * 70)
    
    # STEP 1: Neural Extraction
    print("\n[NEURAL LAYER] Extracting facts from text...")
    neural = NeuralPerceptionModule()
    facts = neural.extract_facts(text)
    
    print(f"Extracted {len(facts)} facts:")
    for fact in facts:
        print(f"  • {fact.predicate} @ t={fact.time} (confidence: {fact.confidence})")
    
    if not facts:
        print("⚠ No facts extracted. Check input text.")
        return
    
    # Identify key entities
    accused = facts[-1].predicate.split("(")[1].split(",")[0]
    victim = facts[-1].predicate.split(",")[1].rstrip(")")
    
    # STEP 2: Build Symbolic KB
    print("\n[SYMBOLIC LAYER] Grounding facts in knowledge base...")
    kb = SymbolicKnowledgeBase()
    
    # Add extracted facts
    for fact in facts:
        kb.add_fact(fact.predicate, fact.confidence)
        print(f"  ✓ Added: {fact.predicate}")
    
    # Check for minor status
    minor_status = "Minor" if any(e.entity_type == "minor" for fact in facts for e in fact.entities) else "Adult"
    kb.add_fact(f"Status({victim}, {minor_status})", 0.9)
    print(f"  ✓ Added: Status({victim}, {minor_status})")
    
    # STEP 3: Add Rules
    print("\n[RULES] Loading legal inference rules...")
    
    # Assault on Minor
    kb.add_rule(Rule(
        charge="Assault on Minor",
        premises=[f"Assault({accused},{victim})", f"Status({victim}, Minor)"],
        weight=0.9,
        side="prosecution",
        name="Assault on Minor",
        description="Direct assault against minor victim"
    ))
    
    # Self-defense defense
    if TemporalReasoner.valid_self_defense(facts, accused):
        kb.add_fact(f"ValidSelfDefense({accused})", 0.8)
        kb.add_rule(Rule(
            charge="Assault on Minor",
            premises=[f"ValidSelfDefense({accused})"],
            weight=1.0,
            side="defense",
            name="Self-Defense",
            description="Defendant acted in self-defense"
        ))
        print("  ✓ Self-defense VALID (temporal ordering supports)")
    else:
        print("  • Self-defense INVALID (temporal ordering contradicts)")
    
    # STEP 4: Reason & Evaluate
    print("\n[REASONING] Evaluating charges using burden of proof...")
    reasoner = BurdenOfProofReasoner(kb)
    
    charges_to_evaluate = [charge] if charge else kb.charge_definitions.keys()
    results = {}
    
    for charge_type in charges_to_evaluate:
        if kb.rules[charge_type]:
            result = reasoner.evaluate_charge(charge_type, theta)
            results[charge_type] = result
            
            print(f"\n  Charge: {charge_type}")
            print(f"    Verdict: {result['verdict']}")
            print(f"    Prosecution: {result['prosecution_score']} | Defense: {result['defense_score']} | Diff: {result['difference']}")
            print(f"    Threshold: {result['theta']}")
            
            for rule in result["prosecution_rules"]:
                print(f"      → PROSECUTION: {rule['name']} (+{rule['score']})")
            for rule in result["defense_rules"]:
                print(f"      → DEFENSE: {rule['name']} (+{rule['score']})")
    
    # STEP 5: Generate Case Summary
    print("\n[SUMMARY] Generating case summary...")
    summarizer = CaseSummarizer(facts, {"accused": accused, "victim": victim})
    case_summary = summarizer.generate_summary()
    
    print("\n" + case_summary["summary_text"])
    print(f"Applicable charges: {', '.join(case_summary['charges_available'])}")
    print(f"Mitigating factors: {', '.join(case_summary['mitigating_factors']) if case_summary['mitigating_factors'] else 'None identified'}")
    
    print("\n" + "=" * 70)
    return {
        "facts": facts,
        "kb": kb,
        "reasoning_results": results,
        "case_summary": case_summary
    }


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    # EXAMPLE 1: Analyze from raw text
    print("\n\n{'*'*80}")
    print("EXAMPLE 1: Simple Text Analysis")
    print("{'*'*80}\n")
    
    text = (
        "Mary attacked John. "
        "John assaulted Mary, who is a minor."
    )
    run_system(text, charge="Assault on Minor", theta=0.6)
    
    
    # EXAMPLE 2: Analyze from case document
    print("\n\n{'*'*80}")
    print("EXAMPLE 2: Case Document Analysis")
    print("{'*'*80}\n")
    
    case_text = """CASE NUMBER: 2024-CV-001234
PLAINTIFF: State of New York
DEFENDANT: John Smith
COURT: New York State Supreme Court
JUDGE: Hon. Patricia Johnson
DATE FILED: 2024-01-15
LOCATION: New York County
CHARGES: Assault on Minor, Aggravated Assault
NARRATIVE:
On January 10, 2024, at approximately 3:45 PM, a physical altercation occurred 
outside PS 123 Elementary School. According to witness statements and victim 
testimony, John Smith, age 28, engaged in an unprovoked assault against Mary Johnson, 
age 14, a minor student at the school. The defendant struck the victim multiple times 
with his fists, causing bruising and minor lacerations. After the initial assault, 
the victim attempted to defend herself, but the defendant continued the attack. 
The defendant was apprehended at the scene by school security. The victim was 
transported to New York Presbyterian Hospital where she received treatment for her injuries."""
    
    doc = DocumentParser.parse_text_document(case_text)
    if doc:
        result = analyze_case_document(doc, theta=0.6)
        
        # Save report to file
        report_path = "case_analysis_report.txt"
        result['report_generator'].save_report(report_path)
        
        # Print summary of verdicts
        print("\n" + "="*80)
        print("FINAL JURY VERDICTS")
        print("="*80)
        for verdict in result['verdicts']:
            print(f"\n{verdict.charge}")
            print(f"  Verdict: {verdict.verdict}")
            print(f"  Confidence: {verdict.confidence * 100:.1f}%")
            print(f"  Recommendation: {verdict.recommendation}")

