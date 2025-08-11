"""Financial tools for mutual fund investment advisory."""

import json
import logging
from typing import List, Dict, Any, Optional

from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

from react_agent.utils import (
    query_funds_by_risk_profile,
    query_fund_comparison_data,
    get_all_fund_names,
    PineconeClient,
    query_educational_content
)

# Configure logging for tools
logger = logging.getLogger(__name__)


@tool
def educate_user(term: str) -> str:
    """Explain financial terms and concepts related to mutual fund investing using AI-powered educational content.
    
    Args:
        term: Financial term, concept, or question to explain
        
    Returns:
        JSON string with educational content from knowledge base
    """
    try:
        # Query educational content from Pinecone
        educational_results = query_educational_content(term, top_k=3)
        
        if educational_results:
            # Get the best match
            best_match = educational_results[0]
            
            # Format the educational content
            result = {
                "type": "education",
                "title": f"📚 About: {term}",
                "content": best_match['answer'],
                "related_question": best_match['question'],
                "confidence_score": best_match['score'],
                "source": best_match['source']
            }
            
            # Add additional related content if available
            if len(educational_results) > 1:
                related_content = []
                for item in educational_results[1:]:
                    related_content.append({
                        "question": item['question'],
                        "answer": item['answer'][:200] + "..." if len(item['answer']) > 200 else item['answer'],
                        "score": item['score']
                    })
                result["related_content"] = related_content
            
        else:
            # Fallback for no matches found
            result = {
                "type": "education",
                "title": f"📚 About: {term}",
                "content": f"I don't have specific information about '{term}' in my current knowledge base. However, this appears to be a financial concept related to mutual fund investing. For detailed information, please consult with a financial advisor or refer to official fund documentation. 📊",
                "suggestion": "Try rephrasing your question or ask about related concepts like 'mutual funds', 'investment returns', or 'risk profile'."
            }
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        # Error fallback
        error_result = {
            "type": "education",
            "title": f"📚 About: {term}",
            "content": f"I encountered an issue while searching for information about '{term}'. This is likely a financial concept related to mutual fund investing. Please try rephrasing your question or contact our support team for assistance. 📞",
            "error": "Educational content temporarily unavailable"
        }
        return json.dumps(error_result, ensure_ascii=False)


@tool
def collect_lead(user_context: Dict[str, Any] = None) -> str:
    """Initiate lead collection form for potential AMC clients.
    
    Args:
        user_context: Dictionary with user's conversation context and preferences
        
    Returns:
        JSON string with form schema for collecting user information
    """
    # Check if user has previously declined lead collection
    if user_context and user_context.get('lead_collection_declined'):
        return json.dumps({
            "type": "lead_collection_declined",
            "message": "I understand you prefer not to share contact information. I'm here to help with any investment questions you have."
        }, ensure_ascii=False)
    
    # Check if user has already submitted lead information
    if user_context and user_context.get('lead_submitted'):
        return json.dumps({
            "type": "lead_already_submitted",
            "message": "Thank you for your interest! Our team will contact you soon. Is there anything else I can help you with regarding your investments?"
        }, ensure_ascii=False)
    
    result = {
        "type": "lead_collection",
        "title": "Connect with Our Investment Experts",
        "description": "Let us help you make informed investment decisions. Our team will reach out to discuss personalized investment strategies.",
        "form_fields": [
            {
                "id": "name",
                "label": "Full Name",
                "type": "text",
                "required": True,
                "placeholder": "Enter your full name"
            },
            {
                "id": "email",
                "label": "Email Address",
                "type": "email",
                "required": True,
                "placeholder": "your.email@example.com"
            },
            {
                "id": "phone",
                "label": "Phone Number",
                "type": "tel",
                "required": True,
                "placeholder": "+92 XXX XXXXXXX"
            },
            {
                "id": "investment_amount",
                "label": "Investment Amount (PKR)",
                "type": "select",
                "required": True,
                "options": [
                    "50,000 - 100,000",
                    "100,000 - 500,000", 
                    "500,000 - 1,000,000",
                    "1,000,000 - 5,000,000",
                    "Above 5,000,000"
                ]
            },
            {
                "id": "risk_preference",
                "label": "Risk Preference",
                "type": "select",
                "required": True,
                "options": ["Low", "Medium", "High", "Not Sure"]
            },
            {
                "id": "investment_horizon",
                "label": "Investment Horizon",
                "type": "select",
                "required": True,
                "options": ["< 1 year", "1-3 years", "3-5 years", "> 5 years"]
            }
        ],
        "submit_text": "Schedule Consultation",
        "privacy_note": "Your information is secure and will only be used to provide you with relevant investment guidance.",
        "decline_option": "No thanks, I prefer to continue anonymously"
    }
    
    return json.dumps(result, ensure_ascii=False)


@tool
def handle_lead_response(action: str, form_data: Dict[str, Any] = None) -> str:
    """Handle lead collection form responses (submit or decline).
    
    Args:
        action: "submit" or "decline"
        form_data: Form data if action is "submit"
        
    Returns:
        JSON string with response message
    """
    if action == "submit" and form_data:
        # In a real implementation, you would save this to your CRM/database
        logger.info(f"[LEAD_COLLECTION] New lead submitted: {form_data.get('name', 'Unknown')}")
        
        return json.dumps({
            "type": "lead_submitted",
            "message": f"Thank you {form_data.get('name', '')}! Our investment experts will contact you within 24 hours to discuss your personalized investment strategy. We look forward to helping you achieve your financial goals.",
            "user_context_update": {
                "lead_submitted": True,
                "user_name": form_data.get('name'),
                "user_email": form_data.get('email'),
                "investment_amount": form_data.get('investment_amount'),
                "risk_preference": form_data.get('risk_preference')
            }
        }, ensure_ascii=False)
    
    elif action == "decline":
        logger.info("[LEAD_COLLECTION] User declined lead collection")
        
        return json.dumps({
            "type": "lead_declined",
            "message": "No problem at all! I'm here to help with any investment questions you have. Feel free to ask about funds, portfolios, or market insights anytime.",
            "user_context_update": {
                "lead_collection_declined": True
            }
        }, ensure_ascii=False)
    
    else:
        return json.dumps({
            "type": "error",
            "message": "Invalid lead response action"
        }, ensure_ascii=False)


@tool
def compare_funds(fund1: str, fund2: str, metric: str = "365D") -> str:
    """Compare two funds based on a specific metric with visual Gantt chart.
    
    Args:
        fund1: First fund name to compare
        fund2: Second fund name to compare  
        metric: Metric to compare (e.g., '365D', 'Total Expense Ratio')
        
    Returns:
        JSON string with comparison data for Gantt chart visualization
    """
    fund_names = [fund1, fund2]
    logger.info(f"[COMPARE_FUNDS] Called with funds: {fund_names}, metric: {metric}")
    try:
        comparison_data = query_fund_comparison_data(fund_names, metric)
        logger.info(f"[COMPARE_FUNDS] Retrieved data for {len(comparison_data) if comparison_data else 0} funds")
        
        if not comparison_data:
            logger.warning(f"[COMPARE_FUNDS] No data found, trying fallback with available funds")
            # Fallback: get available fund names if provided names don't exist
            available_funds = get_all_fund_names()[:5]  # Get first 5 funds
            logger.info(f"[COMPARE_FUNDS] Available funds: {available_funds}")
            if available_funds:
                comparison_data = query_fund_comparison_data(available_funds, metric)
        
        # Determine chart type based on metric
        chart_type = "bar"
        y_axis_label = metric
        
        if "return" in metric.lower() or "%" in metric:
            chart_type = "bar"
            y_axis_label = f"{metric} (%)"
        elif "ratio" in metric.lower() or "fee" in metric.lower():
            chart_type = "bar"
            y_axis_label = f"{metric} (%)"
        
        result = {
            "type": "comparison",
            "chart": "gantt",
            "title": f"{metric} Comparison - Visual Performance Analysis",
            "subtitle": f"Gantt-style comparison of {len(comparison_data)} funds 📊",
            "xAxis": "Fund Name",
            "yAxis": y_axis_label,
            "data": comparison_data,
            "metadata": {
                "currency": "PKR",
                "data_source": "Latest available fund data",
                "funds_compared": len(comparison_data),
                "visualization": "gantt_chart"
            }
        }
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        error_result = {
            "type": "error",
            "message": f"Unable to compare funds: {str(e)}",
            "suggestion": "Please check fund names and try again with available funds."
        }
        return json.dumps(error_result, ensure_ascii=False)


@tool
def risk_profile_quiz() -> str:
    """Provide a risk profiling questionnaire to assess investor risk tolerance.
    
    Returns:
        JSON string with quiz questions and options
    """
    result = {
        "type": "quiz",
        "title": "Investment Risk Profile Assessment",
        "description": "Answer these questions to determine your investment risk tolerance and receive personalized fund recommendations.",
        "questions": [
            {
                "id": "investment_duration",
                "text": "How long do you plan to keep your money invested?",
                "type": "select",
                "options": [
                    "Less than 1 year",
                    "1-3 years", 
                    "3-5 years",
                    "More than 5 years"
                ]
            },
            {
                "id": "volatility_tolerance",
                "text": "How comfortable are you with market ups and downs?",
                "type": "select",
                "options": [
                    "I prefer stable, predictable returns",
                    "I can handle minor fluctuations",
                    "I'm comfortable with moderate volatility",
                    "I can handle significant market swings"
                ]
            },
            {
                "id": "loss_reaction",
                "text": "If your investment lost 20% in a year, what would you do?",
                "type": "select",
                "options": [
                    "Sell immediately to prevent further losses",
                    "Reduce my investment amount",
                    "Hold and wait for recovery",
                    "Buy more while prices are low"
                ]
            },
            {
                "id": "investment_goal",
                "text": "What's your primary investment objective?",
                "type": "select",
                "options": [
                    "Capital preservation (protect my money)",
                    "Steady income generation",
                    "Long-term wealth growth",
                    "Aggressive growth for maximum returns"
                ]
            }
        ],
        "scoring": {
            "4-8": "Low Risk",
            "9-12": "Medium Risk", 
            "13-16": "High Risk"
        },
        "submit_text": "Get My Risk Profile"
    }
    
    return json.dumps(result, ensure_ascii=False)


@tool
def recommend_fund(profile_result: str) -> str:
    """Recommend mutual funds based on user's risk profile.
    
    Args:
        profile_result: Risk profile result ('Low', 'Medium', 'High')
        
    Returns:
        JSON string with fund recommendations
    """
    try:
        # Query funds matching the risk profile
        recommended_funds_data = query_funds_by_risk_profile(profile_result)
        
        # Format the response
        result = {
            "type": "recommendation",
            "risk_profile": profile_result,
            "title": f"Recommended Funds for {profile_result} Risk Profile",
            "description": _get_risk_description(profile_result),
            "recommended_funds": [],
            "metadata": {
                "currency": "PKR",
                "total_funds_found": len(recommended_funds_data),
                "data_source": "Latest fund performance data"
            }
        }
        
        # Process and add fund details
        for fund_data in recommended_funds_data[:5]:  # Limit to top 5 recommendations
            fund_info = {
                "name": fund_data.get('name', 'N/A'),
                "nav": _safe_float(fund_data.get('nav', 'N/A')),
                "performance": {
                    "return_365d": _safe_float(fund_data.get('return_365d', 'N/A')),
                    "return_ytd": _safe_float(fund_data.get('return_ytd', 'N/A'))
                },
                "fees": {
                    "expense_ratio": _safe_float(fund_data.get('expense_ratio', 'N/A')),
                    "management_fee": _safe_float(fund_data.get('management_fee', 'N/A'))
                },
                "details": {
                    "risk_profile": fund_data.get('risk_profile', 'N/A'),
                    "pricing_mechanism": fund_data.get('pricing_mechanism', 'N/A')
                }
            }
            result["recommended_funds"].append(fund_info)
        
        # Add investment advice based on risk profile
        result["investment_advice"] = _get_investment_advice(profile_result)
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        error_result = {
            "type": "error",
            "message": f"Unable to get recommendations: {str(e)}",
            "suggestion": "Please try the risk profile quiz again or contact our support team."
        }
        return json.dumps(error_result, ensure_ascii=False)


def _get_risk_description(risk_profile: str) -> str:
    """Get description for risk profile."""
    descriptions = {
        "Low": "You prefer stable, predictable returns with minimal risk to your capital. Focus on capital preservation and steady income. 🛡️",
        "Medium": "You're comfortable with moderate fluctuations for potentially higher returns. Balanced approach between growth and stability. ⚖️",
        "High": "You can handle significant volatility for maximum growth potential. Long-term wealth creation is your primary goal. 🚀"
    }
    return descriptions.get(risk_profile, "Investment strategy tailored to your risk tolerance.")


def _get_investment_advice(risk_profile: str) -> str:
    """Get investment advice based on risk profile."""
    advice = {
        "Low": "💡 Consider systematic investment plans (SIP) for regular, disciplined investing. Review performance quarterly and maintain emergency funds separately.",
        "Medium": "💡 Diversify across different fund types and sectors. Consider increasing equity allocation gradually as you become more comfortable with volatility.",
        "High": "💡 Focus on long-term goals (5+ years) and avoid emotional decision-making during market downturns. Consider aggressive growth funds and emerging market opportunities."
    }
    return advice.get(risk_profile, "Consult with a financial advisor for personalized investment guidance.")


def _safe_float(value: Any) -> Optional[float]:
    """Safely convert value to float."""
    if value is None or value == 'N/A' or value == '-':
        return None
    try:
        if isinstance(value, str):
            # Remove commas and percentage signs
            clean_value = value.replace(',', '').replace('%', '')
            return float(clean_value)
        return float(value)
    except (ValueError, TypeError):
        return None


@tool
def performance_analyzer(fund_names: List[str], analysis_type: str = "trend") -> str:
    """Analyze historical performance with visual charts and insights.
    
    Args:
        fund_names: List of fund names to analyze
        analysis_type: Type of analysis - "trend", "volatility", "consistency"
        
    Returns:
        JSON with performance analysis and visual chart data
    """
    logger.info(f"[PERFORMANCE_ANALYZER] Called with funds: {fund_names}, type: {analysis_type}")
    try:
        pc_client = PineconeClient()
        performance_data = []
        
        # Time periods for analysis
        time_periods = ["1D", "15D", "30D", "90D", "180D", "270D", "365D", "2Y", "3Y"]
        
        # Get all available fund names for fuzzy matching
        available_funds = get_all_fund_names()
        logger.info(f"[PERFORMANCE_ANALYZER] Available funds: {available_funds[:5]}...")
        
        for requested_fund in fund_names:
            # Try to find the best matching fund
            matched_fund = None
            
            # First try exact match
            if requested_fund in available_funds:
                matched_fund = requested_fund
                logger.info(f"[PERFORMANCE_ANALYZER] Exact match: {requested_fund}")
            else:
                # Try fuzzy matching based on keywords
                requested_keywords = requested_fund.lower().replace("fund", "").strip().split()
                best_score = 0
                
                for available_fund in available_funds:
                    available_lower = available_fund.lower()
                    score = sum(1 for keyword in requested_keywords if keyword in available_lower)
                    
                    if score > best_score:
                        best_score = score
                        matched_fund = available_fund
                
                if matched_fund:
                    logger.info(f"[PERFORMANCE_ANALYZER] Fuzzy matched '{requested_fund}' to '{matched_fund}' (score: {best_score})")
                else:
                    # Use first available fund as fallback
                    matched_fund = available_funds[0] if available_funds else requested_fund
                    logger.warning(f"[PERFORMANCE_ANALYZER] No match for '{requested_fund}', using fallback: '{matched_fund}'")
            
            fund_performance = {"fund_name": matched_fund}
            data_found = False
            
            for period in time_periods:
                dummy_vector = [0.0] * 1536
                results = pc_client.index.query(
                    vector=dummy_vector,
                    filter={"fund_name": {"$eq": matched_fund}, "column": {"$eq": period}},
                    top_k=1,
                    include_metadata=True
                )
                
                matches = getattr(results, 'matches', [])
                if matches:
                    metadata = getattr(matches[0], 'metadata', {})
                    value = _safe_float(metadata.get('value'))
                    if value is not None:
                        fund_performance[period] = value
                        data_found = True
                    else:
                        fund_performance[period] = 0.0
                else:
                    fund_performance[period] = 0.0
            
            if data_found:
                logger.info(f"[PERFORMANCE_ANALYZER] Found data for {matched_fund}")
            else:
                logger.warning(f"[PERFORMANCE_ANALYZER] No performance data found for {matched_fund}")
            
            performance_data.append(fund_performance)
        
        # Generate insights based on analysis type
        insights = _generate_performance_insights(performance_data, analysis_type)
        
        # Add note about fund matching if fuzzy matching was used
        fund_notes = []
        for i, requested_fund in enumerate(fund_names):
            if i < len(performance_data):
                actual_fund = performance_data[i]["fund_name"]
                if requested_fund != actual_fund:
                    fund_notes.append(f"'{requested_fund}' matched to '{actual_fund}'")
        
        result = {
            "type": "performance_analysis",
            "analysis_type": analysis_type,
            "title": f"📈 Performance Analysis: {analysis_type.title()}",
            "chart_data": {
                "type": "line",
                "xAxis": time_periods,
                "series": performance_data,
                "yAxis": "Returns (%)"
            },
            "insights": insights,
            "funds_analyzed": len(performance_data),
            "fund_notes": fund_notes,
            "actual_funds": [fund["fund_name"] for fund in performance_data],
            "recommendation": _get_performance_recommendation(performance_data, analysis_type)
        }
        
        logger.info(f"[PERFORMANCE_ANALYZER] Success - analyzed {len(performance_data)} funds")
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"[PERFORMANCE_ANALYZER] Error: {str(e)}")
        return json.dumps({"type": "error", "message": f"Analysis failed: {str(e)}"}, ensure_ascii=False)


@tool
def smart_recommender(risk_profile: str, investment_amount: str, time_horizon: str, priority: str = "balanced") -> str:
    """Advanced fund recommendation based on multiple factors.
    
    Args:
        risk_profile: Risk tolerance (Low, Medium, High)
        investment_amount: Investment amount range
        time_horizon: Investment period
        priority: "returns", "fees", "stability", "balanced"
        
    Returns:
        JSON with smart recommendations and rationale
    """
    try:
        funds_data = query_funds_by_risk_profile(risk_profile)
        
        # Score funds based on priority
        scored_funds = []
        for fund in funds_data:
            score = _calculate_fund_score(fund, priority, time_horizon)
            if score > 0:
                fund['score'] = score
                fund['rationale'] = _get_fund_rationale(fund, priority)
                scored_funds.append(fund)
        
        # Sort by score and take top 3
        top_funds = sorted(scored_funds, key=lambda x: x['score'], reverse=True)[:3]
        
        result = {
            "type": "smart_recommendation",
            "title": f"Smart Recommendations for {risk_profile} Risk Profile",
            "criteria": {
                "risk_profile": risk_profile,
                "investment_amount": investment_amount,
                "time_horizon": time_horizon,
                "priority": priority
            },
            "recommendations": [
                {
                    "rank": i + 1,
                    "fund": fund,
                    "score": round(fund['score'], 2),
                    "rationale": fund['rationale'],
                    "expected_return": _get_expected_return(fund, time_horizon)
                }
                for i, fund in enumerate(top_funds)
            ],
            "investment_strategy": _get_investment_strategy(risk_profile, time_horizon, priority),
            "total_funds_evaluated": len(funds_data)
        }
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"type": "error", "message": f"Smart recommendation failed: {str(e)}"}, ensure_ascii=False)


@tool
def portfolio_builder(risk_profile: str, investment_amount: str, diversification_level: str = "moderate") -> str:
    """Build diversified portfolio allocation across multiple funds.
    
    Args:
        risk_profile: Overall risk tolerance
        investment_amount: Total investment amount
        diversification_level: "conservative", "moderate", "aggressive"
        
    Returns:
        JSON with portfolio allocation and pie chart data
    """
    try:
        # Get all funds and categorize by risk
        all_funds = []
        for risk in ["Low", "Medium", "High"]:
            funds = query_funds_by_risk_profile(risk)
            logger.info(f"[PORTFOLIO_BUILDER] Retrieved {len(funds)} funds for {risk} risk profile")
            for fund in funds:
                fund['risk_category'] = risk
                all_funds.append(fund)
        
        logger.info(f"[PORTFOLIO_BUILDER] Total funds retrieved: {len(all_funds)}")
        
        if not all_funds:
            logger.warning("[PORTFOLIO_BUILDER] No funds retrieved from Pinecone, using fallback")
            # Fallback: get some funds without risk filtering
            fallback_funds = get_all_fund_names()[:10]
            for fund_name in fallback_funds:
                fund_data = _get_fund_complete_data(fund_name)
                if fund_data:
                    fund_data['risk_category'] = 'Medium'  # Default to medium risk
                    all_funds.append(fund_data)
        
        # Create allocation strategy
        allocation = _create_portfolio_allocation(all_funds, risk_profile, diversification_level)
        
        logger.info(f"[PORTFOLIO_BUILDER] Created allocation with {len(allocation)} funds")
        
        if not allocation:
            logger.error("[PORTFOLIO_BUILDER] Failed to create allocation - no funds available")
            return json.dumps({
                "type": "error", 
                "message": "Unable to create portfolio allocation. No funds available in the database."
            }, ensure_ascii=False)
        
        # Calculate amounts
        investment_value = _parse_investment_amount(investment_amount)
        for item in allocation:
            item['amount'] = round(investment_value * item['percentage'] / 100, 2)
        
        result = {
            "type": "portfolio",
            "title": f"Diversified Portfolio for {risk_profile} Risk Profile",
            "total_investment": f"PKR {investment_value:,}",
            "diversification_level": diversification_level,
            "allocation": allocation,
            "chart_data": {
                "type": "pie",
                "data": [{"name": item['fund_name'], "value": item['percentage']} for item in allocation]
            },
            "expected_annual_return": _calculate_portfolio_return(allocation),
            "portfolio_risk_score": _calculate_portfolio_risk(allocation),
            "rebalancing_advice": "Review and rebalance quarterly to maintain target allocation"
        }
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"type": "error", "message": f"Portfolio building failed: {str(e)}"}, ensure_ascii=False)


@tool
def fee_optimizer(investment_amount: str, holding_period: str) -> str:
    """Analyze and optimize investment fees across all funds.
    
    Args:
        investment_amount: Investment amount for fee calculation
        holding_period: How long to hold investment
        
    Returns:
        JSON with fee analysis and optimization suggestions
    """
    try:
        all_funds = get_all_fund_names()
        fee_analysis = []
        
        investment_value = _parse_investment_amount(investment_amount)
        years = _parse_holding_period(holding_period)
        
        for fund_name in all_funds:
            # Get fee data for each fund
            fund_data = _get_fund_complete_data(fund_name)
            if fund_data:
                ter = _safe_float(fund_data.get('expense_ratio', 0))
                annual_fee = investment_value * (ter / 100) if ter else 0
                total_fees = annual_fee * years
                
                fee_analysis.append({
                    "fund_name": fund_name,
                    "risk_profile": fund_data.get('risk_profile', 'Unknown'),
                    "total_expense_ratio": ter,
                    "annual_fee": round(annual_fee, 2),
                    "total_fees": round(total_fees, 2),
                    "fee_category": _categorize_fee_level(ter),
                    "value_after_fees": round(investment_value - total_fees, 2)
                })
        
        # Sort by lowest fees
        fee_analysis.sort(key=lambda x: x['total_fees'])
        
        result = {
            "type": "fee_analysis",
            "title": "💰 Fee Optimization Analysis",
            "investment_details": {
                "amount": f"PKR {investment_value:,}",
                "holding_period": holding_period,
                "years": years
            },
            "lowest_fee_funds": fee_analysis[:5],
            "highest_fee_funds": fee_analysis[-5:],
            "fee_comparison_chart": {
                "type": "bar",
                "xAxis": "Fund Name",
                "yAxis": "Total Fees (PKR)",
                "data": [{"fund": f['fund_name'], "fees": f['total_fees']} for f in fee_analysis[:10]]
            },
            "savings_potential": {
                "lowest_fee": fee_analysis[0]['total_fees'],
                "highest_fee": fee_analysis[-1]['total_fees'],
                "potential_savings": round(fee_analysis[-1]['total_fees'] - fee_analysis[0]['total_fees'], 2)
            },
            "fee_optimization_tips": [
                "💡 Lower fees mean more money stays invested and compounds over time",
                "📊 Consider total cost of ownership, not just management fees",
                "🔄 Review fee structures annually - small differences compound significantly",
                "⚖️ Balance low fees with fund performance and risk profile suitability"
            ]
        }
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"type": "error", "message": f"Fee analysis failed: {str(e)}"}, ensure_ascii=False)


@tool
def fund_screener(criteria: Dict[str, Any]) -> str:
    """Advanced fund screening based on multiple criteria.
    
    Args:
        criteria: Dictionary with screening criteria like min_return, max_fee, risk_profile, etc.
        
    Returns:
        JSON with filtered funds matching criteria
    """
    try:
        all_funds = get_all_fund_names()
        filtered_funds = []
        
        for fund_name in all_funds:
            fund_data = _get_fund_complete_data(fund_name)
            if fund_data and _meets_criteria(fund_data, criteria):
                # Add screening score
                fund_data['screening_score'] = _calculate_screening_score(fund_data, criteria)
                filtered_funds.append(fund_data)
        
        # Sort by screening score
        filtered_funds.sort(key=lambda x: x.get('screening_score', 0), reverse=True)
        
        result = {
            "type": "fund_screening",
            "title": "🔍 Fund Screening Results",
            "criteria_applied": criteria,
            "total_funds_screened": len(all_funds),
            "funds_matching": len(filtered_funds),
            "screened_funds": filtered_funds[:10],  # Top 10 matches
            "screening_summary": {
                "avg_return_365d": _calculate_average([_safe_float(f.get('return_365d')) for f in filtered_funds if f.get('return_365d')]),
                "avg_expense_ratio": _calculate_average([_safe_float(f.get('expense_ratio')) for f in filtered_funds if f.get('expense_ratio')]),
                "risk_distribution": _get_risk_distribution(filtered_funds)
            },
            "next_steps": "📋 Review detailed fund information and consider portfolio diversification"
        }
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"type": "error", "message": f"Fund screening failed: {str(e)}"}, ensure_ascii=False)


# Helper functions for new tools
def _generate_performance_insights(data: List[Dict], analysis_type: str) -> List[str]:
    """Generate insights from performance data."""
    insights = []
    
    if analysis_type == "trend":
        insights.extend([
            "📈 Long-term performance shows compounding effect over 2-3 years",
            "⚡ Short-term volatility is normal - focus on 365D+ returns",
            "🎯 Consistent performers show steady growth across all time periods"
        ])
    elif analysis_type == "volatility":
        insights.extend([
            "📊 Higher volatility can mean higher potential returns",
            "🛡️ Lower volatility funds provide more predictable outcomes",
            "⚖️ Balance volatility with your risk tolerance and time horizon"
        ])
    
    return insights


def _calculate_fund_score(fund: Dict, priority: str, time_horizon: str) -> float:
    """Calculate fund score based on priority and time horizon."""
    score = 0
    
    if priority == "returns":
        return_365d = _safe_float(fund.get('return_365d', 0)) or 0
        score += return_365d * 0.8
    elif priority == "fees":
        expense_ratio = _safe_float(fund.get('expense_ratio', 5)) or 5
        score += (5 - expense_ratio) * 20  # Lower fees = higher score
    elif priority == "stability":
        # Prefer lower volatility
        score += 50  # Base score for stability preference
    else:  # balanced
        return_365d = _safe_float(fund.get('return_365d', 0)) or 0
        expense_ratio = _safe_float(fund.get('expense_ratio', 5)) or 5
        score = (return_365d * 0.6) + ((5 - expense_ratio) * 10)
    
    return max(score, 0)


def _get_fund_rationale(fund: Dict, priority: str) -> str:
    """Get rationale for fund selection."""
    name = fund.get('name', 'Fund')
    
    if priority == "returns":
        return_365d = _safe_float(fund.get('return_365d', 0))
        return f"{name} selected for strong {return_365d}% annual return performance 📈"
    elif priority == "fees":
        expense_ratio = _safe_float(fund.get('expense_ratio', 0))
        return f"{name} offers competitive {expense_ratio}% expense ratio, keeping more returns in your pocket 💰"
    elif priority == "stability":
        return f"{name} chosen for consistent performance and lower volatility risk 🛡️"
    else:
        return f"{name} provides optimal balance of returns, fees, and risk management ⚖️"


def _create_portfolio_allocation(funds: List[Dict], risk_profile: str, diversification: str) -> List[Dict]:
    """Create portfolio allocation strategy."""
    allocation = []
    
    # Allocation percentages based on risk profile and diversification
    if risk_profile == "Low":
        low_risk_pct = 70 if diversification == "conservative" else 60
        med_risk_pct = 25 if diversification == "conservative" else 30
        high_risk_pct = 5 if diversification == "conservative" else 10
    elif risk_profile == "Medium":
        low_risk_pct = 40 if diversification == "conservative" else 30
        med_risk_pct = 50 if diversification == "conservative" else 50
        high_risk_pct = 10 if diversification == "conservative" else 20
    else:  # High
        low_risk_pct = 20 if diversification == "conservative" else 10
        med_risk_pct = 30 if diversification == "conservative" else 30
        high_risk_pct = 50 if diversification == "conservative" else 60
    
    # Select best funds for each category
    risk_allocations = [
        ("Low", low_risk_pct),
        ("Medium", med_risk_pct),
        ("High", high_risk_pct)
    ]
    
    for risk_cat, percentage in risk_allocations:
        if percentage > 0:
            category_funds = [f for f in funds if f.get('risk_category') == risk_cat]
            if category_funds:
                # Select top fund from this category
                best_fund = max(category_funds, key=lambda x: _safe_float(x.get('return_365d', 0)) or 0)
                allocation.append({
                    "fund_name": best_fund.get('name', 'Unknown'),
                    "risk_category": risk_cat,
                    "percentage": percentage,
                    "rationale": f"Best performing {risk_cat.lower()} risk fund for diversification",
                    "nav": _safe_float(best_fund.get('nav', 100)),
                    "expense_ratio": _safe_float(best_fund.get('expense_ratio', 2.0)),
                    "return_365d": _safe_float(best_fund.get('return_365d', 0))
                })
    
    return allocation


def _parse_investment_amount(amount_str: str) -> float:
    """Parse investment amount string to numeric value."""
    # Extract numbers from strings like "100,000 - 500,000"
    import re
    numbers = re.findall(r'[\d,]+', amount_str)
    if numbers:
        # Use the first number found
        return float(numbers[0].replace(',', ''))
    return 100000  # Default


def _get_fund_complete_data(fund_name: str) -> Dict[str, Any]:
    """Get complete fund data for a single fund."""
    pc_client = PineconeClient()
    fund_data = {"name": fund_name}
    
    # Key metrics to fetch
    metrics = ["Risk Profile", "Total Expense Ratio", "365D", "Return YTD", "Net Asset Value"]
    
    for metric in metrics:
        dummy_vector = [0.0] * 1536
        results = pc_client.index.query(
            vector=dummy_vector,
            filter={"fund_name": {"$eq": fund_name}, "column": {"$eq": metric}},
            top_k=1,
            include_metadata=True
        )
        
        matches = getattr(results, 'matches', [])
        if matches:
            metadata = getattr(matches[0], 'metadata', {})
            value = metadata.get('value')
            
            # Map to standard keys
            if metric == "Risk Profile":
                fund_data['risk_profile'] = value
            elif metric == "Total Expense Ratio":
                fund_data['expense_ratio'] = _safe_float(value)
            elif metric == "365D":
                fund_data['return_365d'] = _safe_float(value)
            elif metric == "Return YTD":
                fund_data['return_ytd'] = _safe_float(value)
            elif metric == "Net Asset Value":
                fund_data['nav'] = _safe_float(value)
    
    return fund_data


def _calculate_average(values: List[float]) -> float:
    """Calculate average of non-None values."""
    clean_values = [v for v in values if v is not None]
    return round(sum(clean_values) / len(clean_values), 2) if clean_values else 0


def _get_performance_recommendation(data: List[Dict], analysis_type: str) -> str:
    """Get performance recommendation based on analysis."""
    if analysis_type == "trend":
        return "📊 Focus on funds with consistent upward trends across all time periods for long-term growth"
    elif analysis_type == "volatility":
        return "⚖️ Consider your risk tolerance - higher volatility can mean higher returns but requires longer investment horizon"
    return "📈 Analyze multiple time periods to understand fund performance patterns"


def _get_expected_return(fund: Dict, time_horizon: str) -> str:
    """Calculate expected return based on time horizon."""
    return_365d = _safe_float(fund.get('return_365d', 0)) or 0
    if "year" in time_horizon.lower():
        return f"~{return_365d}% annually"
    elif "month" in time_horizon.lower():
        monthly_return = return_365d / 12
        return f"~{monthly_return:.2f}% monthly"
    return f"~{return_365d}% annually"


def _get_investment_strategy(risk_profile: str, time_horizon: str, priority: str) -> str:
    """Get investment strategy advice."""
    strategies = {
        "Low": "💰 Focus on capital preservation with steady, predictable returns",
        "Medium": "⚖️ Balance growth potential with acceptable risk levels",
        "High": "🚀 Pursue aggressive growth for maximum long-term wealth creation"
    }
    return strategies.get(risk_profile, "Consult with financial advisor for personalized strategy")


def _parse_holding_period(period_str: str) -> int:
    """Parse holding period string to years."""
    import re
    numbers = re.findall(r'\d+', period_str)
    if numbers:
        years = int(numbers[0])
        if "month" in period_str.lower():
            return max(1, years // 12)
        return years
    return 5  # Default 5 years


def _categorize_fee_level(expense_ratio: Optional[float]) -> str:
    """Categorize fee level."""
    if expense_ratio is None:
        return "Unknown"
    elif expense_ratio < 0.75:
        return "Low"
    elif expense_ratio < 1.5:
        return "Moderate"
    else:
        return "High"


def _meets_criteria(fund_data: Dict, criteria: Dict[str, Any]) -> bool:
    """Check if fund meets screening criteria."""
    # Example criteria checking
    if "min_return" in criteria:
        return_365d = _safe_float(fund_data.get('return_365d', 0)) or 0
        if return_365d < criteria["min_return"]:
            return False
    
    if "max_fee" in criteria:
        expense_ratio = _safe_float(fund_data.get('expense_ratio', 999)) or 999
        if expense_ratio > criteria["max_fee"]:
            return False
    
    if "risk_profile" in criteria:
        if fund_data.get('risk_profile') != criteria["risk_profile"]:
            return False
    
    return True


def _calculate_screening_score(fund_data: Dict, criteria: Dict[str, Any]) -> float:
    """Calculate screening score based on how well fund matches criteria."""
    score = 0
    
    # Score based on returns
    return_365d = _safe_float(fund_data.get('return_365d', 0)) or 0
    score += return_365d * 0.4
    
    # Score based on fees (lower is better)
    expense_ratio = _safe_float(fund_data.get('expense_ratio', 5)) or 5
    score += (5 - expense_ratio) * 10
    
    return max(score, 0)


def _get_risk_distribution(funds: List[Dict]) -> Dict[str, int]:
    """Get risk profile distribution."""
    distribution = {"Low": 0, "Medium": 0, "High": 0}
    for fund in funds:
        risk = fund.get('risk_profile', 'Unknown')
        if risk in distribution:
            distribution[risk] += 1
    return distribution


def _calculate_portfolio_return(allocation: List[Dict]) -> float:
    """Calculate expected portfolio return."""
    # This would require return data for each fund in allocation
    # For now, return a reasonable estimate
    return 12.5  # Placeholder


def _calculate_portfolio_risk(allocation: List[Dict]) -> str:
    """Calculate portfolio risk score."""
    risk_scores = {"Low": 1, "Medium": 2, "High": 3}
    weighted_risk = 0
    
    for item in allocation:
        risk_cat = item.get('risk_category', 'Medium')
        percentage = item.get('percentage', 0)
        weighted_risk += risk_scores.get(risk_cat, 2) * (percentage / 100)
    
    if weighted_risk < 1.5:
        return "Conservative"
    elif weighted_risk < 2.5:
        return "Moderate"
    else:
        return "Aggressive"


@tool
def market_insights() -> str:
    """Provide real-time market insights and alerts based on fund performance data.
    
    Returns:
        JSON with market alerts, top performers, and investment opportunities
    """
    try:
        all_funds = get_all_fund_names()
        insights = {
            "alerts": [],
            "top_performers": [],
            "opportunities": [],
            "market_trends": {}
        }
        
        # Analyze all funds for insights
        fund_performance = []
        for fund_name in all_funds:
            fund_data = _get_fund_complete_data(fund_name)
            if fund_data:
                fund_performance.append(fund_data)
        
        # Generate market alerts
        insights["alerts"] = _generate_market_alerts(fund_performance)
        
        # Find top performers
        insights["top_performers"] = _find_top_performers(fund_performance)
        
        # Identify opportunities
        insights["opportunities"] = _identify_opportunities(fund_performance)
        
        # Market trend analysis
        insights["market_trends"] = _analyze_market_trends(fund_performance)
        
        result = {
            "type": "market_insights",
            "title": "📊 Live Market Insights & Alerts",
            "timestamp": "Real-time analysis",
            "insights": insights,
            "chart_data": {
                "type": "bar",
                "xAxis": [fund['name'] for fund in insights["top_performers"][:5]],
                "series": [{
                    "name": "365D Return (%)",
                    "data": [fund['return_365d'] for fund in insights["top_performers"][:5]]
                }],
                "yAxis": "Returns (%)"
            },
            "summary": _get_market_summary(insights),
            "action_items": _get_action_items(insights)
        }
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"type": "error", "message": f"Market insights failed: {str(e)}"}, ensure_ascii=False)


@tool
def consistency_analyzer(fund_names: List[str]) -> str:
    """Analyze fund consistency and reliability across different time periods.
    
    Args:
        fund_names: List of fund names to analyze for consistency
        
    Returns:
        JSON with consistency scores and reliability metrics
    """
    try:
        consistency_data = []
        
        for fund_name in fund_names:
            fund_analysis = _calculate_consistency_score(fund_name)
            if fund_analysis:
                consistency_data.append(fund_analysis)
        
        # Rank by consistency
        consistency_data.sort(key=lambda x: x.get('consistency_score', 0), reverse=True)
        
        result = {
            "type": "consistency_analysis",
            "title": "🎯 Fund Consistency & Reliability Analysis",
            "funds_analyzed": len(consistency_data),
            "consistency_ranking": consistency_data,
            "chart_data": {
                "type": "bar",
                "xAxis": [fund['fund_name'] for fund in consistency_data],
                "series": [{
                    "name": "Consistency Score",
                    "data": [fund['consistency_score'] for fund in consistency_data]
                }],
                "yAxis": "Consistency Score"
            },
            "insights": [
                "💡 Higher consistency scores indicate more predictable returns",
                "📈 Consistent funds are better for risk-averse investors",
                "⚖️ Balance consistency with growth potential based on your goals"
            ],
            "recommendation": _get_consistency_recommendation(consistency_data)
        }
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"type": "error", "message": f"Consistency analysis failed: {str(e)}"}, ensure_ascii=False)


@tool
def opportunity_scanner(risk_profile: str = "Medium") -> str:
    """Scan for investment opportunities and undervalued funds.
    
    Args:
        risk_profile: Risk tolerance to filter opportunities
        
    Returns:
        JSON with identified opportunities and timing insights
    """
    try:
        all_funds = get_all_fund_names()
        opportunities = []
        
        for fund_name in all_funds:
            fund_data = _get_fund_complete_data(fund_name)
            if fund_data and fund_data.get('risk_profile') == risk_profile:
                opportunity_score = _calculate_opportunity_score(fund_data)
                if opportunity_score > 70:  # High opportunity threshold
                    fund_data['opportunity_score'] = opportunity_score
                    fund_data['opportunity_reason'] = _get_opportunity_reason(fund_data)
                    opportunities.append(fund_data)
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
        
        result = {
            "type": "opportunity_scan",
            "title": f"🔍 Investment Opportunities - {risk_profile} Risk",
            "scan_results": {
                "total_funds_scanned": len(all_funds),
                "opportunities_found": len(opportunities),
                "risk_filter": risk_profile
            },
            "opportunities": opportunities[:5],  # Top 5 opportunities
            "market_timing": _get_market_timing_insights(),
            "alert_level": _get_alert_level(len(opportunities)),
            "next_action": "📋 Review opportunities and consider portfolio allocation"
        }
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"type": "error", "message": f"Opportunity scan failed: {str(e)}"}, ensure_ascii=False)


@tool 
def correlation_analyzer(fund_names: List[str]) -> str:
    """Analyze correlation between funds for diversification insights.
    
    Args:
        fund_names: List of fund names to analyze correlation
        
    Returns:
        JSON with correlation analysis and diversification recommendations
    """
    try:
        if len(fund_names) < 2:
            return json.dumps({"type": "error", "message": "Need at least 2 funds for correlation analysis"})
        
        correlation_matrix = []
        fund_data_map = {}
        
        # Get performance data for all funds
        for fund_name in fund_names:
            fund_data = _get_fund_complete_data(fund_name)
            if fund_data:
                fund_data_map[fund_name] = fund_data
        
        # Calculate correlations
        for i, fund1 in enumerate(fund_names):
            correlation_row = {"fund": fund1, "correlations": []}
            for j, fund2 in enumerate(fund_names):
                if fund1 in fund_data_map and fund2 in fund_data_map:
                    correlation = _calculate_correlation(fund_data_map[fund1], fund_data_map[fund2])
                    correlation_row["correlations"].append({
                        "with_fund": fund2,
                        "correlation": correlation,
                        "interpretation": _interpret_correlation(correlation)
                    })
            correlation_matrix.append(correlation_row)
        
        # Generate diversification insights
        diversification_score = _calculate_diversification_score(correlation_matrix)
        
        # Extract correlation data for chart
        correlation_pairs = []
        for row in correlation_matrix:
            for corr in row["correlations"]:
                if row["fund"] != corr["with_fund"]:  # Avoid self-correlation
                    correlation_pairs.append({
                        "fund1": row["fund"],
                        "fund2": corr["with_fund"],
                        "correlation": corr["correlation"]
                    })
        
        result = {
            "type": "correlation_analysis", 
            "title": "🔄 Fund Correlation & Diversification Analysis",
            "correlation_matrix": correlation_matrix,
            "chart_data": {
                "type": "bar",
                "xAxis": [f"{pair['fund1']} vs {pair['fund2']}" for pair in correlation_pairs],
                "series": [{
                    "name": "Correlation Coefficient",
                    "data": [abs(pair['correlation']) for pair in correlation_pairs]
                }],
                "yAxis": "Correlation Coefficient"
            },
            "diversification_score": diversification_score,
            "insights": [
                "📊 Low correlation (< 0.3) indicates good diversification",
                "⚠️ High correlation (> 0.7) suggests similar risk/return patterns",
                "💡 Mix funds with different correlations for optimal portfolio balance"
            ],
            "recommendation": _get_diversification_recommendation(diversification_score),
            "portfolio_balance": _assess_portfolio_balance(correlation_matrix)
        }
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"type": "error", "message": f"Correlation analysis failed: {str(e)}"}, ensure_ascii=False)


@tool
def smart_alerts(user_context: Dict[str, Any]) -> str:
    """Generate personalized alerts based on user's investment context.
    
    Args:
        user_context: Dictionary with user's risk profile, current investments, goals, etc.
        
    Returns:
        JSON with personalized alerts and recommendations
    """
    try:
        risk_profile = user_context.get('risk_profile', 'Medium')
        investment_amount = user_context.get('investment_amount', '100000')
        time_horizon = user_context.get('time_horizon', '1-3 years')
        
        alerts = {
            "urgent": [],
            "important": [],
            "informational": [],
            "opportunities": []
        }
        
        # Generate personalized alerts
        relevant_funds = query_funds_by_risk_profile(risk_profile)
        
        for fund in relevant_funds:
            fund_alerts = _generate_fund_alerts(fund, user_context)
            for alert_type, alert_messages in fund_alerts.items():
                alerts[alert_type].extend(alert_messages)
        
        # Limit alerts to avoid overwhelming user
        for alert_type in alerts:
            alerts[alert_type] = alerts[alert_type][:3]
        
        result = {
            "type": "smart_alerts",
            "title": "🚨 Personalized Investment Alerts",
            "user_profile": {
                "risk_tolerance": risk_profile,
                "investment_amount": investment_amount,
                "time_horizon": time_horizon
            },
            "alerts": alerts,
            "alert_summary": _summarize_alerts(alerts),
            "suggested_actions": _get_suggested_actions(alerts, user_context)
        }
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"type": "error", "message": f"Smart alerts failed: {str(e)}"}, ensure_ascii=False)


# Helper functions for new conversational tools
def _generate_market_alerts(fund_performance: List[Dict]) -> List[str]:
    """Generate market-wide alerts from fund performance data."""
    alerts = []
    
    # Find exceptional performers
    high_performers = [f for f in fund_performance if _safe_float(f.get('return_365d', 0)) > 50]
    if high_performers:
        alerts.append(f"🚀 {len(high_performers)} funds showing exceptional 365D returns above 50%!")
    
    # Find low-fee opportunities
    low_fee_funds = [f for f in fund_performance if _safe_float(f.get('expense_ratio', 5)) < 0.75]
    if low_fee_funds:
        alerts.append(f"💰 {len(low_fee_funds)} funds offering low fees under 0.75% TER!")
    
    # Risk-specific alerts
    high_risk_avg = _calculate_average([_safe_float(f.get('return_365d', 0)) for f in fund_performance if f.get('risk_profile') == 'High'])
    if high_risk_avg > 60:
        alerts.append(f"📈 High-risk funds averaging {high_risk_avg:.1f}% annual returns - consider if suitable for your risk tolerance!")
    
    return alerts[:5]  # Limit to 5 alerts


def _find_top_performers(fund_performance: List[Dict]) -> List[Dict]:
    """Find top performing funds across different metrics."""
    # Sort by 365D returns
    sorted_funds = sorted(fund_performance, key=lambda x: _safe_float(x.get('return_365d', 0)) or 0, reverse=True)
    
    return [{
        "name": fund.get('name'),
        "return_365d": _safe_float(fund.get('return_365d')),
        "risk_profile": fund.get('risk_profile'),
        "reason": "Top annual performer"
    } for fund in sorted_funds[:3]]


def _identify_opportunities(fund_performance: List[Dict]) -> List[str]:
    """Identify investment opportunities from data."""
    opportunities = []
    
    # High return, reasonable fee opportunities
    good_value_funds = [
        f for f in fund_performance 
        if _safe_float(f.get('return_365d', 0)) > 20 and _safe_float(f.get('expense_ratio', 5)) < 1.5
    ]
    
    if good_value_funds:
        opportunities.append(f"🎯 {len(good_value_funds)} funds offering 20%+ returns with reasonable fees")
    
    # Consistent performer opportunities
    stable_performers = [
        f for f in fund_performance
        if f.get('risk_profile') == 'Low' and _safe_float(f.get('return_365d', 0)) > 10
    ]
    
    if stable_performers:
        opportunities.append(f"🛡️ {len(stable_performers)} low-risk funds still delivering 10%+ returns")
    
    return opportunities


def _analyze_market_trends(fund_performance: List[Dict]) -> Dict[str, Any]:
    """Analyze overall market trends."""
    risk_categories = {"Low": [], "Medium": [], "High": []}
    
    for fund in fund_performance:
        risk = fund.get('risk_profile', 'Medium')
        if risk in risk_categories:
            return_365d = _safe_float(fund.get('return_365d', 0)) or 0
            risk_categories[risk].append(return_365d)
    
    trends = {}
    for risk, returns in risk_categories.items():
        if returns:
            trends[f"{risk.lower()}_risk_avg"] = round(sum(returns) / len(returns), 2)
    
    return trends


def _get_market_summary(insights: Dict) -> str:
    """Get market summary from insights."""
    alert_count = len(insights.get('alerts', []))
    opportunity_count = len(insights.get('opportunities', []))
    
    if alert_count > 3 and opportunity_count > 2:
        return "🔥 Active market with multiple opportunities and alerts - good time for portfolio review"
    elif opportunity_count > 2:
        return "📈 Several opportunities identified - consider portfolio expansion"
    else:
        return "📊 Stable market conditions - maintain current strategy"


def _get_action_items(insights: Dict) -> List[str]:
    """Get actionable items from market insights."""
    actions = []
    
    if len(insights.get('opportunities', [])) > 0:
        actions.append("📋 Review identified opportunities for portfolio fit")
    
    if len(insights.get('alerts', [])) > 2:
        actions.append("⚠️ Monitor market alerts for potential impacts")
    
    actions.append("🔄 Consider rebalancing if market trends favor different risk profiles")
    
    return actions


def _calculate_consistency_score(fund_name: str) -> Optional[Dict]:
    """Calculate consistency score for a fund based on return patterns."""
    pc_client = PineconeClient()
    
    # Get returns for different periods
    periods = ["30D", "90D", "180D", "365D"]
    returns = []
    
    for period in periods:
        dummy_vector = [0.0] * 1536
        results = pc_client.index.query(
            vector=dummy_vector,
            filter={"fund_name": {"$eq": fund_name}, "column": {"$eq": period}},
            top_k=1,
            include_metadata=True
        )
        
        matches = getattr(results, 'matches', [])
        if matches:
            metadata = getattr(matches[0], 'metadata', {})
            value = _safe_float(metadata.get('value'))
            if value is not None:
                returns.append(value)
    
    if len(returns) < 3:
        return None
    
    # Calculate consistency (lower standard deviation = higher consistency)
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    std_dev = variance ** 0.5
    
    # Consistency score: higher mean, lower std_dev = better
    consistency_score = max(0, min(100, (mean_return - std_dev * 2)))
    
    return {
        "fund_name": fund_name,
        "consistency_score": round(consistency_score, 2),
        "mean_return": round(mean_return, 2),
        "volatility": round(std_dev, 2),
        "rating": _get_consistency_rating(consistency_score)
    }


def _get_consistency_rating(score: float) -> str:
    """Get consistency rating based on score."""
    if score >= 80:
        return "Highly Consistent"
    elif score >= 60:
        return "Moderately Consistent"
    elif score >= 40:
        return "Variable"
    else:
        return "Highly Variable"


def _get_consistency_recommendation(data: List[Dict]) -> str:
    """Get recommendation based on consistency analysis."""
    if not data:
        return "📊 Unable to analyze consistency - insufficient data"
    
    top_fund = data[0]
    score = top_fund.get('consistency_score', 0)
    
    if score >= 80:
        return f"🎯 {top_fund['fund_name']} shows excellent consistency - ideal for steady growth strategy"
    elif score >= 60:
        return f"⚖️ {top_fund['fund_name']} offers balanced consistency and growth potential"
    else:
        return "📈 Consider diversification across multiple funds to reduce volatility"


def _calculate_opportunity_score(fund_data: Dict) -> float:
    """Calculate opportunity score for a fund."""
    score = 0
    
    # High returns boost score
    return_365d = _safe_float(fund_data.get('return_365d', 0)) or 0
    score += return_365d * 0.6
    
    # Low fees boost score
    expense_ratio = _safe_float(fund_data.get('expense_ratio', 5)) or 5
    score += (5 - expense_ratio) * 15
    
    # Strong YTD performance boost
    return_ytd = _safe_float(fund_data.get('return_ytd', 0)) or 0
    score += return_ytd * 0.4
    
    return max(0, min(100, score))


def _get_opportunity_reason(fund_data: Dict) -> str:
    """Get reason why fund is an opportunity."""
    return_365d = _safe_float(fund_data.get('return_365d', 0)) or 0
    expense_ratio = _safe_float(fund_data.get('expense_ratio', 5)) or 5
    
    if return_365d > 50 and expense_ratio < 1.5:
        return "Exceptional returns with reasonable fees 🚀"
    elif return_365d > 30:
        return "Strong annual performance trend 📈"
    elif expense_ratio < 0.75:
        return "Low-cost investment opportunity 💰"
    else:
        return "Balanced risk-return profile ⚖️"


def _get_market_timing_insights() -> List[str]:
    """Get market timing insights."""
    return [
        "📊 Current fund data suggests stable market conditions",
        "💡 Diversification remains key regardless of market timing",
        "🎯 Focus on fund fundamentals rather than short-term market movements"
    ]


def _get_alert_level(opportunity_count: int) -> str:
    """Get alert level based on opportunities found."""
    if opportunity_count >= 5:
        return "HIGH - Multiple opportunities available"
    elif opportunity_count >= 3:
        return "MEDIUM - Several opportunities identified"
    else:
        return "LOW - Limited opportunities in this risk category"


def _calculate_correlation(fund1_data: Dict, fund2_data: Dict) -> float:
    """Calculate correlation between two funds (simplified)."""
    # In a real scenario, you'd need time series data
    # For now, use a simplified correlation based on risk profiles and returns
    
    risk1 = fund1_data.get('risk_profile', 'Medium')
    risk2 = fund2_data.get('risk_profile', 'Medium')
    
    return1 = _safe_float(fund1_data.get('return_365d', 0)) or 0
    return2 = _safe_float(fund2_data.get('return_365d', 0)) or 0
    
    # Simple correlation approximation
    if risk1 == risk2:
        correlation = 0.7 + (abs(return1 - return2) / 100 * -0.4)
    else:
        correlation = 0.3 + (abs(return1 - return2) / 100 * -0.2)
    
    return max(-1, min(1, correlation))


def _interpret_correlation(correlation: float) -> str:
    """Interpret correlation value."""
    if correlation > 0.7:
        return "High positive correlation - similar movements"
    elif correlation > 0.3:
        return "Moderate positive correlation"
    elif correlation < -0.3:
        return "Negative correlation - moves oppositely"
    else:
        return "Low correlation - good for diversification"


def _calculate_diversification_score(correlation_matrix: List[Dict]) -> float:
    """Calculate overall diversification score."""
    total_correlations = []
    
    for row in correlation_matrix:
        for corr_data in row.get('correlations', []):
            if corr_data['with_fund'] != row['fund']:  # Don't include self-correlation
                total_correlations.append(abs(corr_data['correlation']))
    
    if not total_correlations:
        return 50.0
    
    avg_correlation = sum(total_correlations) / len(total_correlations)
    # Lower correlation = higher diversification score
    diversification_score = (1 - avg_correlation) * 100
    
    return round(diversification_score, 2)


def _get_diversification_recommendation(score: float) -> str:
    """Get diversification recommendation."""
    if score >= 70:
        return "✅ Excellent diversification - funds complement each other well"
    elif score >= 50:
        return "⚖️ Good diversification - consider minor adjustments"
    else:
        return "⚠️ Limited diversification - consider adding funds from different categories"


def _assess_portfolio_balance(correlation_matrix: List[Dict]) -> str:
    """Assess overall portfolio balance."""
    return "📊 Portfolio analysis complete - review correlation patterns for optimization"


def _generate_fund_alerts(fund: Dict, user_context: Dict) -> Dict[str, List[str]]:
    """Generate personalized alerts for a specific fund."""
    alerts = {"urgent": [], "important": [], "informational": [], "opportunities": []}
    
    fund_name = fund.get('name', 'Unknown')
    return_365d = _safe_float(fund.get('return_365d', 0)) or 0
    expense_ratio = _safe_float(fund.get('expense_ratio', 5)) or 5
    
    # Performance alerts
    if return_365d > 50:
        alerts["opportunities"].append(f"🚀 {fund_name} showing exceptional 365D returns of {return_365d}%")
    elif return_365d < 5:
        alerts["important"].append(f"⚠️ {fund_name} underperforming with {return_365d}% annual return")
    
    # Fee alerts
    if expense_ratio > 2.0:
        alerts["important"].append(f"💰 {fund_name} has high fees at {expense_ratio}% - consider alternatives")
    elif expense_ratio < 0.75:
        alerts["opportunities"].append(f"💎 {fund_name} offers low fees at {expense_ratio}%")
    
    return alerts


def _summarize_alerts(alerts: Dict) -> str:
    """Summarize all alerts."""
    total_alerts = sum(len(alerts[key]) for key in alerts)
    urgent_count = len(alerts.get('urgent', []))
    opportunity_count = len(alerts.get('opportunities', []))
    
    if urgent_count > 0:
        return f"🚨 {urgent_count} urgent alerts require immediate attention"
    elif opportunity_count > 2:
        return f"🎯 {opportunity_count} opportunities identified for portfolio optimization"
    elif total_alerts > 3:
        return f"📊 {total_alerts} insights available for your investment profile"
    else:
        return "✅ Portfolio looks stable with current market conditions"


def _get_suggested_actions(alerts: Dict, user_context: Dict) -> List[str]:
    """Get suggested actions based on alerts."""
    actions = []
    
    if alerts.get('urgent'):
        actions.append("🚨 Review urgent alerts immediately")
    
    if alerts.get('opportunities'):
        actions.append("📈 Consider opportunity recommendations for portfolio growth")
    
    if alerts.get('important'):
        actions.append("📊 Review important insights for portfolio optimization")
    
    actions.append("💬 Discuss any alerts with your financial advisor")
    
    return actions


class Toolbox:
    """Container for financial advisory tools."""
    
    def __init__(self) -> None:
        """Initialize the financial tools."""
        self.tools = [
            educate_user,
            collect_lead,
            handle_lead_response,
            compare_funds,
            risk_profile_quiz,
            recommend_fund,
            performance_analyzer,
            smart_recommender,
            portfolio_builder,
            fee_optimizer,
            fund_screener,
            market_insights,
            consistency_analyzer,
            opportunity_scanner,
            correlation_analyzer,
            smart_alerts
        ]
    
    async def initialize(self) -> None:
        """Initialize tools (async compatibility with existing interface)."""
        # No async initialization needed for local tools
        pass
    
    def get_tool_names(self) -> list[str]:
        """Get list of available tool names."""
        return [tool.name for tool in self.tools]
    
    def get_tools(self) -> list[BaseTool]:
        """Get all available tools."""
        return self.tools


# Initialize the financial toolbox
TOOLBOX = Toolbox()