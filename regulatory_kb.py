import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CommercialRegulatoryKnowledgeBase:
    def __init__(self):
        self.regulatory_data = self._initialize_commercial_regulations()
        self.jurisdiction_map = self._initialize_jurisdiction_map()
        self.industry_map = self._initialize_industry_map()
        logger.info("✅ Commercial Regulatory Knowledge Base initialized")
    
    def _initialize_commercial_regulations(self) -> Dict[str, List[Dict]]:
        """Initialize comprehensive commercial regulatory database"""
        return {
            "GLBA": [
                {
                    "clause": "Financial Privacy Notice",
                    "description": "Gramm-Leach-Bliley Act privacy requirements for financial institutions",
                    "risk_level": "high",
                    "requirements": [
                        "Privacy notice delivery",
                        "Opt-out mechanisms",
                        "Information sharing policies",
                        "Safeguards rule compliance",
                        "Annual privacy notices"
                    ],
                    "legal_citation": "15 U.S.C. § 6801-6809",
                    "jurisdictions": ["US"],
                    "industries": ["financial", "banking", "lending", "insurance"]
                },
                {
                    "clause": "Data Safeguards Program",
                    "description": "Information security program for customer data protection",
                    "risk_level": "high",
                    "requirements": [
                        "Written security program",
                        "Employee training",
                        "Access controls",
                        "Data encryption",
                        "Incident response plan"
                    ],
                    "legal_citation": "16 CFR Part 314",
                    "jurisdictions": ["US"],
                    "industries": ["financial", "banking", "lending"]
                }
            ],
            
            "FCRA": [
                {
                    "clause": "Credit Reporting Authorization",
                    "description": "Fair Credit Reporting Act requirements for credit checks",
                    "risk_level": "high",
                    "requirements": [
                        "Consumer authorization",
                        "Permissible purpose certification",
                        "Adverse action notices",
                        "Dispute investigation procedures",
                        "Accuracy requirements"
                    ],
                    "legal_citation": "15 U.S.C. § 1681 et seq.",
                    "jurisdictions": ["US"],
                    "industries": ["financial", "employment", "lending", "housing"]
                }
            ],
            
            "TILA": [
                {
                    "clause": "Truth in Lending Disclosures",
                    "description": "Regulation Z requirements for loan cost disclosures",
                    "risk_level": "high",
                    "requirements": [
                        "APR disclosure",
                        "Finance charge calculation",
                        "Payment schedule",
                        "Total payments disclosure",
                        "Right of rescission"
                    ],
                    "legal_citation": "15 U.S.C. § 1601 et seq.",
                    "jurisdictions": ["US"],
                    "industries": ["lending", "financial", "auto_finance", "mortgage"]
                }
            ],
            
            "EFTA": [
                {
                    "clause": "Electronic Fund Transfer Authorization",
                    "description": "Regulation E requirements for electronic payments",
                    "risk_level": "medium",
                    "requirements": [
                        "EFT authorization",
                        "Error resolution procedures",
                        "Liability limitations",
                        "Receipt requirements",
                        "Periodic statements"
                    ],
                    "legal_citation": "15 U.S.C. § 1693 et seq.",
                    "jurisdictions": ["US"],
                    "industries": ["financial", "banking", "payment_processing"]
                }
            ],
            
            "CCPA_CPRA": [
                {
                    "clause": "California Consumer Privacy Rights",
                    "description": "California Consumer Privacy Act and Privacy Rights Act compliance",
                    "risk_level": "high",
                    "requirements": [
                        "Right to know disclosures",
                        "Right to delete procedures",
                        "Right to opt-out of sales",
                        "Non-discrimination policy",
                        "Data processing agreements"
                    ],
                    "legal_citation": "Cal. Civ. Code § 1798.100 et seq.",
                    "jurisdictions": ["US_CA", "US"],
                    "industries": ["all"]
                }
            ],
            
            "NY_DFS": [
                {
                    "clause": "NYDFS Cybersecurity Requirements",
                    "description": "New York Department of Financial Services cybersecurity regulation",
                    "risk_level": "high",
                    "requirements": [
                        "Cybersecurity program",
                        "Chief Information Security Officer",
                        "Penetration testing",
                        "Audit trail systems",
                        "Incident response plan"
                    ],
                    "legal_citation": "23 NYCRR Part 500",
                    "jurisdictions": ["US_NY", "US"],
                    "industries": ["financial", "insurance", "banking"]
                }
            ]
        }
    
    def _initialize_jurisdiction_map(self) -> Dict[str, List[str]]:
        """Map jurisdictions to applicable regulations"""
        return {
            "US": ["GLBA", "FCRA", "TILA", "EFTA", "CCPA_CPRA"],
            "US_CA": ["GLBA", "FCRA", "TILA", "EFTA", "CCPA_CPRA", "NY_DFS"],
            "US_NY": ["GLBA", "FCRA", "TILA", "EFTA", "CCPA_CPRA", "NY_DFS"],
            "global": ["CCPA_CPRA"]
        }
    
    def _initialize_industry_map(self) -> Dict[str, List[str]]:
        """Map industries to applicable regulations"""
        return {
            "financial": ["GLBA", "FCRA", "TILA", "EFTA", "NY_DFS"],
            "banking": ["GLBA", "FCRA", "TILA", "EFTA", "NY_DFS"],
            "lending": ["GLBA", "FCRA", "TILA", "EFTA"],
            "insurance": ["GLBA", "NY_DFS"],
            "auto_finance": ["GLBA", "FCRA", "TILA", "EFTA"],
            "general": ["CCPA_CPRA"]
        }
    
    def get_applicable_regulations(self, contract_text: str, jurisdiction: str = "US", industry: str = "general") -> List[str]:
        """Determine applicable regulations based on contract content, jurisdiction, and industry"""
        contract_lower = contract_text.lower()
        
        # Start with jurisdiction-based regulations
        applicable_regulations = set(self.jurisdiction_map.get(jurisdiction, []))
        
        # Add industry-specific regulations
        applicable_regulations.update(self.industry_map.get(industry, []))
        
        # Content-based regulation detection
        content_based_regs = self._detect_regulations_from_content(contract_lower)
        applicable_regulations.update(content_based_regs)
        
        # Remove inappropriate regulations based on content analysis
        self._filter_inappropriate_regulations(applicable_regulations, contract_lower, jurisdiction, industry)
        
        return sorted(list(applicable_regulations))
    
    def _detect_regulations_from_content(self, contract_text: str) -> List[str]:
        """Detect regulations based on contract content analysis"""
        detected_regulations = set()
        
        # Financial content detection
        financial_terms = ["loan", "financing", "credit", "interest rate", "apr", "payment", "debt"]
        if any(term in contract_text for term in financial_terms):
            detected_regulations.update(["GLBA", "FCRA", "TILA", "EFTA"])
        
        # Privacy content detection
        privacy_terms = ["personal data", "privacy", "confidential", "data processing", "consumer information"]
        if any(term in contract_text for term in privacy_terms):
            detected_regulations.update(["CCPA_CPRA"])
        
        # Cybersecurity content detection
        security_terms = ["security", "cyber", "data protection", "encryption", "access control"]
        if any(term in contract_text for term in security_terms):
            detected_regulations.update(["NY_DFS"])
        
        return list(detected_regulations)
    
    def _filter_inappropriate_regulations(self, regulations: set, contract_text: str, jurisdiction: str, industry: str):
        """Remove regulations that don't apply to this context"""
        inappropriate_regs = set()
        
        for regulation in regulations:
            reg_data = self.regulatory_data.get(regulation, [])
            if not reg_data:
                continue
            
            # Check jurisdiction compatibility
            first_clause = reg_data[0]
            allowed_jurisdictions = first_clause.get('jurisdictions', [])
            if jurisdiction not in allowed_jurisdictions and "global" not in allowed_jurisdictions:
                inappropriate_regs.add(regulation)
                continue
            
            # Check industry compatibility
            allowed_industries = first_clause.get('industries', [])
            if industry not in allowed_industries and "all" not in allowed_industries:
                inappropriate_regs.add(regulation)
                continue
        
        regulations.difference_update(inappropriate_regs)
    
    def get_missing_clauses(self, contract_text: str, regulation: str) -> List[Dict]:
        """Advanced clause detection with context awareness"""
        if regulation not in self.regulatory_data:
            return []
        
        contract_lower = contract_text.lower()
        missing_clauses = []
        
        for clause_data in self.regulatory_data[regulation]:
            if not self._is_clause_present(clause_data, contract_lower):
                missing_clauses.append(clause_data)
        
        return missing_clauses
    
    def _is_clause_present(self, clause_data: Dict, contract_text: str) -> bool:
        """Check if a clause is present in the contract using multiple detection strategies"""
        clause_name = clause_data['clause'].lower()
        description = clause_data['description'].lower()
        requirements = [req.lower() for req in clause_data['requirements']]
        
        # Strategy 1: Direct keyword matching
        keywords = self._extract_keywords(clause_name)
        direct_matches = sum(1 for keyword in keywords if keyword in contract_text)
        
        # Strategy 2: Requirement-based matching
        requirement_matches = sum(1 for req in requirements[:3] if any(word in contract_text for word in req.split()))
        
        # Strategy 3: Semantic concept matching
        concept_matches = self._check_semantic_concepts(clause_data, contract_text)
        
        # Weighted scoring
        total_score = (direct_matches * 0.5) + (requirement_matches * 0.3) + (concept_matches * 0.2)
        
        return total_score >= 1.0
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        return [word for word in words if word not in stop_words][:5]
    
    def _check_semantic_concepts(self, clause_data: Dict, contract_text: str) -> int:
        """Check for semantic concepts related to the clause"""
        concept_map = {
            "Financial Privacy Notice": ["privacy policy", "data sharing", "opt out", "confidentiality"],
            "Credit Reporting Authorization": ["credit check", "background check", "consumer report", "authorization"],
            "Data Safeguards Program": ["security program", "data protection", "encryption", "access control"],
            "Truth in Lending Disclosures": ["apr", "annual percentage rate", "finance charge", "disclosure"]
        }
        
        concepts = concept_map.get(clause_data['clause'], [])
        return sum(1 for concept in concepts if concept in contract_text)
    
    def analyze_contract_content(self, contract_text: str, regulation: str) -> Dict[str, List[str]]:
        """Analyze contract content for regulation-specific issues"""
        issues = []
        recommendations = []
        contract_lower = contract_text.lower()
        
        if regulation == "GLBA":
            if "privacy" not in contract_lower and "confidential" not in contract_lower:
                issues.append("Missing financial privacy provisions")
                recommendations.append("Add GLBA-compliant privacy notice clause")
            
            if "opt-out" not in contract_lower and "opt out" not in contract_lower:
                issues.append("Missing opt-out mechanisms for information sharing")
                recommendations.append("Include GLBA opt-out provisions")
        
        elif regulation == "FCRA":
            if "credit" in contract_lower and "authorization" not in contract_lower:
                issues.append("Missing credit check authorization")
                recommendations.append("Add FCRA-compliant authorization clause")
            
            if "adverse action" not in contract_lower:
                issues.append("Missing adverse action notice procedures")
                recommendations.append("Include FCRA adverse action requirements")
        
        elif regulation == "TILA":
            if "apr" not in contract_lower and "annual percentage rate" not in contract_lower:
                issues.append("Missing APR disclosure")
                recommendations.append("Add TILA-required APR disclosure")
            
            if "finance charge" not in contract_lower:
                issues.append("Missing finance charge disclosure")
                recommendations.append("Include TILA finance charge calculations")
        
        return {
            "issues": issues,
            "recommendations": recommendations
        }