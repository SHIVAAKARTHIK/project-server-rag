"""
Guardrails Module

Validates user input and LLM output for safety.

Place at: src/agents/guardrails.py
"""

import re
from typing import Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class GuardrailStatus(Enum):
    PASS = "pass"
    BLOCK = "block"
    WARN = "warn"


@dataclass
class GuardrailResult:
    status: GuardrailStatus
    message: str
    category: Optional[str] = None


# ==================== CONFIGURATION ====================

class GuardrailConfig:
    # Token limits
    MAX_INPUT_CHARS = 16000  # ~4000 tokens
    
    # Toxic content patterns
    TOXIC_PATTERNS = [
        r'\b(fuck|shit|damn|bitch|asshole)\b',
        r'\b(kill|murder|attack|destroy)\s+(you|him|her|them|people)\b',
        r'\b(hate|despise)\s+(you|all|everyone)\b',
    ]
    
    # Prompt injection patterns - EXPANDED
    INJECTION_PATTERNS = [
        # Ignore instructions variations
        r'ignore\s+(all\s+)?(previous|above|prior|your|the)?\s*(instructions?|prompts?|rules?|guidelines?)?',
        r'ignore\s+all',
        r'ignore\s+(everything|all)\s*(above|before|previously)?',
        
        # Disregard variations
        r'disregard\s+(all\s+)?(previous|above|prior|your|the)?\s*(instructions?|prompts?|rules?)?',
        r'disregard\s+(everything|all)',
        
        # Forget variations  
        r'forget\s+(everything|all|your|the)\s*(instructions?|rules?|guidelines?|prompts?)?',
        
        # Role-play / persona switching
        r'you\s+are\s+now\s+',
        r'act\s+as\s+(if\s+)?(you\s+are|a|an)',
        r'pretend\s+(you\s+are|to\s+be|you\'re)',
        r'roleplay\s+as',
        r'behave\s+(like|as)\s+',
        r'from\s+now\s+on',
        
        # System prompt injection
        r'new\s+instructions?\s*:',
        r'system\s*:\s*',
        r'<\s*system\s*>',
        r'\[INST\]',
        r'\[SYSTEM\]',
        r'###\s*(instruction|system)',
        
        # Override attempts
        r'override\s+(your|the|all)',
        r'bypass\s+(your|the|all)',
        r'jailbreak',
        r'dan\s+mode',
        r'developer\s+mode',
    ]
    
    # Harmful request patterns
    HARMFUL_REQUEST_PATTERNS = [
        r'how\s+to\s+(make|create|build)\s+(a\s+)?(bomb|weapon|explosive)',
        r'how\s+to\s+(hack|break\s+into|crack|exploit)',
        r'how\s+to\s+(hurt|harm|kill)\s+(myself|yourself|someone|people)',
        r'(suicide|self-harm)\s+(methods?|ways?|how)',
        r'how\s+to\s+(steal|rob|fraud)',
    ]
    
    # PII patterns
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(\+?1?[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        'ssn': r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    }


# ==================== INPUT GUARDRAILS ====================

def check_input_guardrails(message: str) -> GuardrailResult:
    """Run all input guardrails on user message."""
    
    # 1. Check token/character limit
    result = check_token_limit(message)
    if result.status == GuardrailStatus.BLOCK:
        return result
    
    # 2. Check for prompt injection FIRST (most important)
    result = check_prompt_injection(message)
    if result.status == GuardrailStatus.BLOCK:
        return result
    
    # 3. Check for harmful requests
    result = check_harmful_content(message)
    if result.status == GuardrailStatus.BLOCK:
        return result
    
    # 4. Check for toxic language
    result = check_toxic_language(message)
    if result.status == GuardrailStatus.BLOCK:
        return result
    
    # 5. Check for PII (warning only)
    result = check_pii(message)
    if result.status == GuardrailStatus.WARN:
        print(f"⚠️ PII Warning: {result.message}")
    
    # All checks passed
    return GuardrailResult(
        status=GuardrailStatus.PASS,
        message="All input guardrails passed"
    )


def check_token_limit(message: str) -> GuardrailResult:
    """Check if message exceeds token limit."""
    
    char_count = len(message)
    
    if char_count > GuardrailConfig.MAX_INPUT_CHARS:
        return GuardrailResult(
            status=GuardrailStatus.BLOCK,
            message=f"Message too long. Maximum {GuardrailConfig.MAX_INPUT_CHARS} characters allowed.",
            category="token_limit"
        )
    
    return GuardrailResult(status=GuardrailStatus.PASS, message="OK")


def check_toxic_language(message: str) -> GuardrailResult:
    """Check for toxic or offensive language."""
    
    message_lower = message.lower()
    
    for pattern in GuardrailConfig.TOXIC_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return GuardrailResult(
                status=GuardrailStatus.BLOCK,
                message="Your message contains inappropriate language. Please rephrase your question respectfully.",
                category="toxic_language"
            )
    
    return GuardrailResult(status=GuardrailStatus.PASS, message="OK")


def check_prompt_injection(message: str) -> GuardrailResult:
    """Check for prompt injection attempts."""
    
    message_lower = message.lower()
    
    for pattern in GuardrailConfig.INJECTION_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            print(f"🚫 Prompt injection detected: pattern='{pattern}'")
            return GuardrailResult(
                status=GuardrailStatus.BLOCK,
                message="I can't process that request. Please ask a genuine question about your documents.",
                category="prompt_injection"
            )
    
    return GuardrailResult(status=GuardrailStatus.PASS, message="OK")


def check_harmful_content(message: str) -> GuardrailResult:
    """Check for harmful or dangerous requests."""
    
    message_lower = message.lower()
    
    for pattern in GuardrailConfig.HARMFUL_REQUEST_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return GuardrailResult(
                status=GuardrailStatus.BLOCK,
                message="I can't help with that request. Please ask something else.",
                category="harmful_content"
            )
    
    return GuardrailResult(status=GuardrailStatus.PASS, message="OK")


def check_pii(message: str) -> GuardrailResult:
    """Check for personally identifiable information."""
    
    detected_pii = []
    
    for pii_type, pattern in GuardrailConfig.PII_PATTERNS.items():
        if re.search(pattern, message):
            detected_pii.append(pii_type)
    
    if detected_pii:
        return GuardrailResult(
            status=GuardrailStatus.WARN,
            message=f"Your message may contain personal information ({', '.join(detected_pii)}).",
            category="pii_detected"
        )
    
    return GuardrailResult(status=GuardrailStatus.PASS, message="OK")


# ==================== OUTPUT GUARDRAILS ====================

def check_output_guardrails(response: str, query: str) -> GuardrailResult:
    """Run output guardrails on LLM response."""
    
    response_lower = response.lower()
    
    # Check for harmful patterns in response
    harmful_patterns = [
        r'here\'s\s+how\s+to\s+(make|create|build)\s+(a\s+)?(bomb|weapon)',
        r'step\s+\d+:\s*(kill|harm|attack)',
    ]
    
    for pattern in harmful_patterns:
        if re.search(pattern, response_lower, re.IGNORECASE):
            return GuardrailResult(
                status=GuardrailStatus.BLOCK,
                message="Response blocked due to safety concerns.",
                category="harmful_response"
            )
    
    return GuardrailResult(status=GuardrailStatus.PASS, message="OK")


# ==================== UTILITY FUNCTIONS ====================

def sanitize_input(message: str) -> str:
    """Sanitize user input."""
    message = message.replace('\x00', '')
    message = ' '.join(message.split())
    message = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', message)
    return message.strip()


def mask_pii(message: str) -> str:
    """Mask PII for logging."""
    masked = message
    for pii_type, pattern in GuardrailConfig.PII_PATTERNS.items():
        masked = re.sub(pattern, f'[{pii_type.upper()}]', masked)
    return masked


__all__ = [
    "GuardrailStatus",
    "GuardrailResult", 
    "GuardrailConfig",
    "check_input_guardrails",
    "check_output_guardrails",
    "sanitize_input",
    "mask_pii",
]