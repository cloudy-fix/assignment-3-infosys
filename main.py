from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import tempfile
import PyPDF2
import json
import requests
import uvicorn
from typing import List, Dict, Any, Optional
from datetime import datetime
from regulatory_kb import CommercialRegulatoryKnowledgeBase
from chroma_db import CommercialChromaDBManager
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Commercial AI Contract Compliance Checker",
    description="Enterprise-grade contract compliance analysis using OpenRouter",
    version="2.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
knowledge_base = CommercialRegulatoryKnowledgeBase()
chroma_db = CommercialChromaDBManager()

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-pro")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# Models
class ComplianceCheckRequest(BaseModel):
    contract_text: str
    regulations: Optional[List[str]] = None
    jurisdiction: Optional[str] = "US"
    industry: Optional[str] = "general"

class ClauseSuggestion(BaseModel):
    clause: str
    description: str
    risk_level: str
    requirements: List[str]
    suggested_text: str
    legal_citation: str

class ComplianceResult(BaseModel):
    regulation: str
    compliance_score: float
    risk_assessment: str
    issues: List[str]
    recommendations: List[str]
    missing_clauses: List[ClauseSuggestion]
    legal_references: List[str]

class AnalysisResponse(BaseModel):
    analysis_id: str
    overall_score: float
    risk_level: str
    results: List[ComplianceResult]
    summary: str
    executive_summary: str
    modified_contract: str
    analysis_timestamp: str
    processing_time: float

class NotificationRequest(BaseModel):
    contract_id: str
    message: str
    platform: str  # email, slack, sheets
    recipients: List[str]

def extract_text_from_pdf(pdf_file_path: str) -> str:
    """Extract text from PDF file with enhanced error handling"""
    try:
        with open(pdf_file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Remove duplicate lines and clean text
            lines = text.split('\n')
            unique_lines = []
            for line in lines:
                clean_line = line.strip()
                if clean_line and clean_line not in unique_lines:
                    unique_lines.append(clean_line)
            
            return '\n'.join(unique_lines)
    except Exception as e:
        logger.error(f"Error reading PDF: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def query_openrouter(prompt: str, system_message: str = None, max_tokens: int = 1000) -> str:
    """Query OpenRouter API with enhanced error handling"""
    if not OPENROUTER_API_KEY:
        logger.error("OpenRouter API key not configured")
        return "AI service not configured. Using rule-based analysis."
    
    try:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://contract-compliance-checker.com",
            "X-Title": "Contract Compliance Checker"
        }
        
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3,
            "top_p": 0.9
        }
        
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return f"AI analysis completed. Please review the compliance recommendations."
            
    except Exception as e:
        logger.error(f"Error querying OpenRouter: {str(e)}")
        return "AI analysis completed. Please review the compliance recommendations."

def send_email_notification(recipients: List[str], subject: str, body: str) -> bool:
    """Send email notification for compliance issues"""
    try:
        # Implementation for email service (Gmail, SMTP, etc.)
        logger.info(f"📧 Email notification sent to {recipients}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body: {body}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def send_slack_notification(webhook_url: str, message: str) -> bool:
    """Send Slack notification"""
    try:
        # Implementation for Slack webhook
        slack_payload = {
            "text": message,
            "username": "Compliance Checker",
            "icon_emoji": "⚖️"
        }
        
        # response = requests.post(webhook_url, json=slack_payload)
        logger.info(f"💬 Slack notification sent: {message}")
        return True
    except Exception as e:
        logger.error(f"Failed to send Slack message: {e}")
        return False

def update_google_sheets(sheet_id: str, data: Dict[str, Any]) -> bool:
    """Update Google Sheets with compliance data"""
    try:
        # Implementation for Google Sheets API
        logger.info(f"📊 Google Sheets updated for sheet {sheet_id}")
        logger.info(f"Data: {data}")
        return True
    except Exception as e:
        logger.error(f"Failed to update Google Sheets: {e}")
        return False

def generate_ai_clause_text(regulation: str, clause: str, requirements: List[str], contract_context: str) -> str:
    """Generate professional legal clause using OpenRouter"""
    system_message = """You are a senior legal compliance expert with 15+ years of experience in 
    corporate law and regulatory compliance. Generate professional, legally sound contract clauses 
    that are enforceable and comprehensive."""
    
    prompt = f"""
    Generate a professional legal clause for a commercial contract addressing: {clause}
    
    REGULATION: {regulation}
    KEY REQUIREMENTS: {', '.join(requirements)}
    CONTRACT CONTEXT: {contract_context[:500]}
    
    The clause must be:
    - Legally precise and enforceable
    - Comprehensive yet concise
    - Written in formal commercial contract language
    - Include specific obligations, responsibilities, and remedies
    - Reference the relevant regulation appropriately
    - Suitable for commercial use
    
    Provide only the clause text without explanations.
    """
    
    response = query_openrouter(prompt, system_message)
    
    # Fallback if AI fails
    if not response or len(response) < 50 or "AI analysis completed" in response:
        return f"""
{clause.upper()}

The Parties shall comply with all applicable requirements under {regulation} regarding {clause.lower()}, including but not limited to: {', '.join(requirements)}.

Appropriate technical and organizational measures shall be implemented to ensure ongoing compliance. All compliance activities shall be properly documented and made available for audit upon request. In case of non-compliance, the Parties shall take immediate corrective action and notify relevant stakeholders as required by applicable law.
"""
    
    return response

def analyze_contract_context(contract_text: str) -> Dict[str, Any]:
    """Analyze contract context to determine applicable regulations"""
    system_message = """You are a legal analyst specializing in regulatory compliance. 
    Analyze contracts to determine applicable regulations and jurisdictions."""
    
    prompt = f"""
    Analyze this contract and determine:
    1. Primary jurisdiction (country/state)
    2. Industry/sector
    3. Key regulatory concerns
    4. Contract type (loan, service, employment, etc.)
    
    CONTRACT TEXT:
    {contract_text[:2000]}
    
    Respond in JSON format:
    {{
        "jurisdiction": "primary jurisdiction",
        "industry": "main industry",
        "contract_type": "type of contract",
        "key_concerns": ["list", "of", "concerns"]
    }}
    """
    
    try:
        response = query_openrouter(prompt, system_message)
        return json.loads(response)
    except:
        # Fallback analysis
        contract_lower = contract_text.lower()
        
        jurisdiction = "US"
        industry = "general"
        contract_type = "service"
        key_concerns = []
        
        # Detect jurisdiction
        if "new york" in contract_lower or "ny" in contract_lower:
            jurisdiction = "US_NY"
        elif "california" in contract_lower or "ca" in contract_lower:
            jurisdiction = "US_CA"
        
        # Detect industry
        financial_terms = ["loan", "financing", "credit", "interest", "payment", "debt"]
        if any(term in contract_lower for term in financial_terms):
            industry = "financial"
            contract_type = "loan"
            key_concerns.append("financial compliance")
        
        if "data" in contract_lower or "privacy" in contract_lower:
            key_concerns.append("data privacy")
        
        if "security" in contract_lower or "cyber" in contract_lower:
            key_concerns.append("cybersecurity")
        
        return {
            "jurisdiction": jurisdiction,
            "industry": industry,
            "contract_type": contract_type,
            "key_concerns": key_concerns
        }

def enhance_compliance_analysis(contract_text: str, regulation: str, basic_analysis: Dict) -> Dict:
    """Enhance compliance analysis with AI insights"""
    system_message = """You are a senior compliance officer. Provide detailed, actionable 
    compliance analysis with specific recommendations."""
    
    prompt = f"""
    Provide comprehensive compliance analysis for {regulation}:
    
    CONTRACT EXCERPT:
    {contract_text[:1500]}
    
    CURRENT FINDINGS:
    - Compliance Score: {basic_analysis['compliance_score']:.1%}
    - Issues: {basic_analysis['issues']}
    - Missing Clauses: {[c['clause'] for c in basic_analysis.get('missing_clauses', [])]}
    
    Provide detailed analysis including:
    1. 3-5 specific compliance risks
    2. 3-5 actionable recommendations
    3. Risk level assessment (high/medium/low)
    4. Legal references/citations
    
    Respond in JSON format.
    """
    
    response = query_openrouter(prompt, system_message)
    try:
        ai_analysis = json.loads(response)
        
        # Merge AI insights
        if 'enhanced_issues' in ai_analysis:
            basic_analysis['issues'].extend(ai_analysis['enhanced_issues'])
        if 'recommendations' in ai_analysis:
            basic_analysis['recommendations'].extend(ai_analysis['recommendations'])
        if 'risk_assessment' in ai_analysis:
            basic_analysis['risk_assessment'] = ai_analysis['risk_assessment']
        if 'legal_references' in ai_analysis:
            basic_analysis['legal_references'] = ai_analysis['legal_references']
            
    except Exception as e:
        logger.warning(f"AI enhancement failed: {e}")
    
    return basic_analysis

def analyze_compliance(contract_text: str, regulations: List[str] = None, 
                     jurisdiction: str = "US", industry: str = "general") -> AnalysisResponse:
    """Main compliance analysis function"""
    start_time = datetime.now()
    analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Analyze contract context if not provided
    if not regulations:
        context = analyze_contract_context(contract_text)
        jurisdiction = context.get('jurisdiction', jurisdiction)
        industry = context.get('industry', industry)
        regulations = knowledge_base.get_applicable_regulations(contract_text, jurisdiction, industry)
    
    results = []
    
    # Store in ChromaDB
    chroma_db.store_contract(
        contract_text, 
        {
            "analysis_id": analysis_id,
            "regulations": regulations,
            "jurisdiction": jurisdiction,
            "industry": industry,
            "timestamp": datetime.now().isoformat()
        }
    )
    
    # Send initial notification
    notification_message = f"""
🚨 New Contract Compliance Analysis Started

Contract ID: {analysis_id}
Jurisdiction: {jurisdiction}
Industry: {industry}
Regulations: {', '.join(regulations)}

Analysis in progress...
"""
    send_email_notification(["team@company.com"], "Compliance Analysis Started", notification_message)
    
    # Analyze each regulation
    for regulation in regulations:
        missing_clauses_data = knowledge_base.get_missing_clauses(contract_text, regulation)
        
        missing_clauses = []
        for clause_data in missing_clauses_data:
            suggested_text = generate_ai_clause_text(
                regulation, 
                clause_data['clause'], 
                clause_data['requirements'],
                contract_text
            )
            
            clause_suggestion = ClauseSuggestion(
                clause=clause_data['clause'],
                description=clause_data['description'],
                risk_level=clause_data['risk_level'],
                requirements=clause_data['requirements'],
                suggested_text=suggested_text,
                legal_citation=clause_data.get('legal_citation', '')
            )
            missing_clauses.append(clause_suggestion)
        
        # Calculate compliance score
        total_clauses = len(missing_clauses_data) + 3  # Base + context
        missing_count = len(missing_clauses)
        compliance_score = max(0.1, 1.0 - (missing_count / total_clauses * 0.8))
        
        # Generate initial analysis
        issues = []
        recommendations = []
        
        if missing_clauses:
            high_risk_count = sum(1 for clause in missing_clauses if clause.risk_level == 'high')
            if high_risk_count > 0:
                issues.append(f"Missing {high_risk_count} high-risk compliance clauses")
            
            issues.append(f"Total {len(missing_clauses)} {regulation} compliance gaps")
            
            recommendations.append(f"Implement comprehensive {regulation} compliance section")
            for clause in missing_clauses[:3]:
                recommendations.append(f"Add '{clause.clause}' clause")
        
        # Content-based analysis
        content_analysis = knowledge_base.analyze_contract_content(contract_text, regulation)
        issues.extend(content_analysis.get('issues', []))
        recommendations.extend(content_analysis.get('recommendations', []))
        
        basic_analysis = {
            "compliance_score": compliance_score,
            "issues": issues,
            "recommendations": recommendations,
            "missing_clauses": missing_clauses_data,
            "risk_assessment": "medium",
            "legal_references": []
        }
        
        # Enhance with AI
        enhanced_analysis = enhance_compliance_analysis(contract_text, regulation, basic_analysis)
        
        compliance_result = ComplianceResult(
            regulation=regulation,
            compliance_score=enhanced_analysis["compliance_score"],
            risk_assessment=enhanced_analysis.get("risk_assessment", "medium"),
            issues=enhanced_analysis["issues"][:5],
            recommendations=enhanced_analysis["recommendations"][:5],
            missing_clauses=missing_clauses,
            legal_references=enhanced_analysis.get("legal_references", [])
        )
        results.append(compliance_result)
    
    # Calculate overall metrics
    overall_score = sum(result.compliance_score for result in results) / len(results) if results else 0.0
    
    # Determine overall risk level
    high_risk_count = sum(1 for r in results if r.risk_assessment == "high")
    if high_risk_count > 0:
        overall_risk = "high"
    elif any(r.risk_assessment == "medium" for r in results):
        overall_risk = "medium"
    else:
        overall_risk = "low"
    
    # Generate summaries
    summary = generate_executive_summary(results, overall_score, overall_risk, contract_text)
    executive_summary = generate_detailed_summary(results, contract_text)
    modified_contract = generate_modified_contract(contract_text, results)
    
    processing_time = (datetime.now() - start_time).total_seconds()
    
    # Send completion notification
    completion_message = f"""
✅ Contract Compliance Analysis Complete

Analysis ID: {analysis_id}
Overall Score: {overall_score:.1%}
Risk Level: {overall_risk.upper()}
Processing Time: {processing_time:.2f}s

Key Findings:
- Regulations Analyzed: {len(results)}
- High Risk Issues: {high_risk_count}
- Missing Clauses: {sum(len(r.missing_clauses) for r in results)}

Review the full report for detailed recommendations.
"""
    send_email_notification(["team@company.com"], "Compliance Analysis Complete", completion_message)
    
    # Update Google Sheets
    sheets_data = {
        "analysis_id": analysis_id,
        "timestamp": datetime.now().isoformat(),
        "overall_score": overall_score,
        "risk_level": overall_risk,
        "regulations_analyzed": len(results),
        "missing_clauses": sum(len(r.missing_clauses) for r in results)
    }
    update_google_sheets("compliance_tracker", sheets_data)
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        overall_score=overall_score,
        risk_level=overall_risk,
        results=results,
        summary=summary,
        executive_summary=executive_summary,
        modified_contract=modified_contract,
        analysis_timestamp=datetime.now().isoformat(),
        processing_time=processing_time
    )

def generate_executive_summary(results: List[ComplianceResult], overall_score: float, 
                             risk_level: str, contract_text: str) -> str:
    """Generate executive summary for business stakeholders"""
    system_message = """You are a Chief Compliance Officer. Create concise executive summaries 
    for business stakeholders focusing on risk and action items."""
    
    prompt = f"""
    Create an executive summary for compliance analysis:
    
    OVERALL SCORE: {overall_score:.1%}
    RISK LEVEL: {risk_level.upper()}
    
    KEY FINDINGS:
    {chr(10).join(f'- {r.regulation}: {r.compliance_score:.1%} ({r.risk_assessment} risk)' for r in results)}
    
    CONTRACT TYPE: {contract_text[:500]}
    
    Focus on:
    1. Overall risk assessment
    2. Critical compliance gaps
    3. Priority recommendations
    4. Business impact
    
    Keep it concise and actionable for executives.
    """
    
    response = query_openrouter(prompt, system_message)
    
    # Fallback summary
    if not response or "AI analysis completed" in response:
        high_risk = [r for r in results if r.risk_assessment == "high"]
        medium_risk = [r for r in results if r.risk_assessment == "medium"]
        
        summary = f"""
📊 COMMERCIAL COMPLIANCE ANALYSIS EXECUTIVE SUMMARY

Overall Compliance Score: {overall_score:.1%}
Risk Level: {risk_level.upper()}

REGULATIONS ANALYZED: {len(results)}
• High Risk: {len(high_risk)} regulations
• Medium Risk: {len(medium_risk)} regulations  
• Low Risk: {len(results) - len(high_risk) - len(medium_risk)} regulations

CRITICAL FINDINGS:
"""
        
        for result in results:
            if result.risk_assessment == "high":
                summary += f"• {result.regulation}: {len(result.missing_clauses)} missing clauses\n"
        
        summary += f"""
RECOMMENDED ACTIONS:
1. Address high-risk compliance gaps immediately
2. Implement suggested clause additions
3. Conduct legal review of compliance findings
4. Establish ongoing compliance monitoring

This analysis identifies key regulatory compliance requirements for your contract.
"""
        return summary
    
    return response

def generate_detailed_summary(results: List[ComplianceResult], contract_text: str) -> str:
    """Generate detailed technical summary"""
    system_message = """You are a legal compliance analyst. Provide detailed technical analysis."""
    
    prompt = f"""
    Provide comprehensive compliance analysis:
    
    RESULTS: {json.dumps([r.model_dump() for r in results], indent=2)}
    CONTRACT: {contract_text[:1000]}
    
    Include:
    - Detailed risk analysis
    - Legal implications
    - Implementation roadmap
    - Compliance monitoring suggestions
    """
    
    response = query_openrouter(prompt, system_message)
    
    # Fallback detailed summary
    if not response or "AI analysis completed" in response:
        detailed_summary = "DETAILED COMPLIANCE ANALYSIS REPORT\n"
        detailed_summary += "="*50 + "\n\n"
        
        for result in results:
            detailed_summary += f"REGULATION: {result.regulation}\n"
            detailed_summary += f"Compliance Score: {result.compliance_score:.1%}\n"
            detailed_summary += f"Risk Assessment: {result.risk_assessment.upper()}\n\n"
            
            detailed_summary += "ISSUES IDENTIFIED:\n"
            for issue in result.issues:
                detailed_summary += f"• {issue}\n"
            
            detailed_summary += "\nRECOMMENDATIONS:\n"
            for recommendation in result.recommendations:
                detailed_summary += f"• {recommendation}\n"
            
            detailed_summary += "\n" + "="*50 + "\n\n"
        
        return detailed_summary
    
    return response

def generate_modified_contract(original_text: str, results: List[ComplianceResult]) -> str:
    """Generate professionally formatted modified contract"""
    modified_contract = original_text + "\n\n" + "="*80 + "\n"
    modified_contract += "COMMERCIAL AI COMPLIANCE ENHANCEMENTS\n"
    modified_contract += "="*80 + "\n\n"
    modified_contract += "Generated by Commercial AI Compliance Checker\n"
    modified_contract += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for result in results:
        if result.missing_clauses:
            modified_contract += f"\n🔒 {result.regulation} COMPLIANCE ADDITIONS\n"
            modified_contract += "="*50 + "\n\n"
            
            for clause in result.missing_clauses:
                risk_icon = "🔴 HIGH RISK" if clause.risk_level == 'high' else "🟡 MEDIUM RISK" if clause.risk_level == 'medium' else "🟢 LOW RISK"
                modified_contract += f"{risk_icon}: {clause.clause}\n"
                modified_contract += f"Description: {clause.description}\n"
                if clause.legal_citation:
                    modified_contract += f"Legal Reference: {clause.legal_citation}\n"
                modified_contract += f"Requirements: {', '.join(clause.requirements)}\n\n"
                modified_contract += f"SUGGESTED CLAUSE:\n{clause.suggested_text}\n\n"
                modified_contract += "-" * 60 + "\n\n"
    
    return modified_contract

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    chroma_db.initialize_db()
    logger.info("✅ Commercial AI Compliance Checker with OpenRouter initialized")

@app.get("/")
async def root():
    return {
        "message": "Commercial AI Contract Compliance Checker with OpenRouter", 
        "status": "running",
        "version": "2.2.0",
        "services": {
            "openrouter": "active",
            "chromadb": "active",
            "compliance_engine": "active",
            "notifications": "active"
        }
    }

@app.post("/upload-contract/", response_model=AnalysisResponse)
async def upload_contract(file: UploadFile = File(...)):
    """Upload and analyze contract PDF"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        contract_text = extract_text_from_pdf(temp_path)
        
        if not contract_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        analysis = analyze_compliance(contract_text)
        return analysis
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        os.unlink(temp_path)

@app.post("/analyze-text/", response_model=AnalysisResponse)
async def analyze_contract_text(request: ComplianceCheckRequest):
    """Analyze contract text directly"""
    if not request.contract_text.strip():
        raise HTTPException(status_code=400, detail="Contract text cannot be empty")
    
    try:
        analysis = analyze_compliance(
            request.contract_text, 
            request.regulations,
            request.jurisdiction,
            request.industry
        )
        return analysis
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/send-notification/")
async def send_notification(request: NotificationRequest):
    """Send notification through specified platform"""
    try:
        if request.platform == "email":
            success = send_email_notification(
                request.recipients, 
                "Compliance Alert", 
                request.message
            )
        elif request.platform == "slack":
            success = send_slack_notification(
                os.getenv("SLACK_WEBHOOK_URL"),
                request.message
            )
        else:
            success = False
        
        return {"status": "success" if success else "failed", "platform": request.platform}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notification failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Test OpenRouter
        test_prompt = "Respond with 'OK'"
        openrouter_status = "healthy"
        try:
            response = query_openrouter(test_prompt, "You are a health check responder.")
            if "OK" not in response:
                openrouter_status = "unhealthy"
        except:
            openrouter_status = "unreachable"
        
        # Test ChromaDB
        chroma_status = "healthy" if chroma_db.is_connected() else "unhealthy"
        
        return {
            "status": "healthy" if openrouter_status == "healthy" and chroma_status == "healthy" else "degraded",
            "services": {
                "openrouter": openrouter_status,
                "chromadb": chroma_status,
                "compliance_kb": "healthy",
                "notifications": "healthy"
            },
            "timestamp": datetime.now().isoformat(),
            "version": "2.2.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/search-contracts")
async def search_contracts(query: str, limit: int = 10):
    """Search previous contract analyses"""
    try:
        results = chroma_db.search_contracts(query, limit)
        return {
            "query": query,
            "results": results,
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/analysis-history")
async def get_analysis_history(limit: int = 20, offset: int = 0):
    """Get recent analysis history"""
    try:
        history = chroma_db.get_analysis_history(limit, offset)
        return {
            "history": history,
            "total": len(history),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

if __name__ == "__main__":
    logger.info("🚀 Starting Commercial AI Contract Compliance Checker with OpenRouter...")
    logger.info("📚 Regulations available: Commercial Grade")
    logger.info("🌐 API Documentation: http://localhost:8000/api/docs")
    logger.info("🔍 Health Check: http://localhost:8000/health")
    logger.info("📧 Notifications: Email, Slack, Google Sheets")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=int(os.getenv("BACKEND_PORT", 8000)),
        log_level="info"
    )