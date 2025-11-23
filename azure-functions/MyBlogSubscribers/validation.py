"""
Shared validation utilities for blog subscriber management.

Provides centralized validation logic that can be used across:
- Azure Functions (Python backend)
- Client-side validation (JavaScript - see patterns below)
- Testing and utilities

This ensures consistency between client and server validation.
"""
import re
from typing import Tuple

# Email validation constants
EMAIL_REGEX = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
EMAIL_REGEX_JS = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'  # Same pattern for JavaScript
MAX_EMAIL_LENGTH = 254  # RFC 5321 maximum email address length
MIN_EMAIL_LENGTH = 6    # Minimum reasonable email: a@b.co


def validate_email(email: str, strip_whitespace: bool = True) -> Tuple[bool, str]:
    """
    Validate email address format and length.
    
    Validation rules (consistent with client-side validation):
    1. Must not be empty
    2. Must be between MIN_EMAIL_LENGTH and MAX_EMAIL_LENGTH characters
    3. Must match EMAIL_REGEX pattern (basic RFC 5322 format)
    4. Whitespace is stripped by default (can be disabled)
    
    Args:
        email: Email address to validate
        strip_whitespace: If True, strip leading/trailing whitespace before validation
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
        If valid: (True, "")
        If invalid: (False, "specific error message")
        
    Examples:
        >>> validate_email("user@example.com")
        (True, "")
        
        >>> validate_email("invalid")
        (False, "Invalid email format")
        
        >>> validate_email("  user@example.com  ")
        (True, "")
        
        >>> validate_email("x" * 255 + "@test.com")
        (False, "Email address is too long")
    """
    if strip_whitespace and email:
        email = email.strip()
    
    # Check if empty
    if not email:
        return False, "Email is required"
    
    # Check minimum length
    if len(email) < MIN_EMAIL_LENGTH:
        return False, "Email address is too short"
    
    # Check maximum length
    if len(email) > MAX_EMAIL_LENGTH:
        return False, "Email address is too long"
    
    # Check format using regex
    if not re.match(EMAIL_REGEX, email):
        return False, "Invalid email format"
    
    return True, ""


def is_valid_email(email: str, strip_whitespace: bool = True) -> bool:
    """
    Simple boolean check if email is valid.
    
    Args:
        email: Email address to validate
        strip_whitespace: If True, strip leading/trailing whitespace
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> is_valid_email("user@example.com")
        True
    """
    is_valid, _ = validate_email(email, strip_whitespace)
    return is_valid


def normalize_email(email: str) -> str:
    """
    Normalize email address for storage and comparison.
    
    Normalization steps:
    1. Strip leading/trailing whitespace
    2. Convert to lowercase
    
    Args:
        email: Email address to normalize
        
    Returns:
        Normalized email address
        
    Example:
        >>> normalize_email("  User@Example.COM  ")
        "user@example.com"
    """
    return email.strip().lower()


# JavaScript validation pattern for client-side use
JAVASCRIPT_VALIDATION_PATTERN = f"""
// Email validation constants (keep in sync with Python backend)
const EMAIL_REGEX = /{EMAIL_REGEX_JS}/;
const MAX_EMAIL_LENGTH = {MAX_EMAIL_LENGTH};
const MIN_EMAIL_LENGTH = {MIN_EMAIL_LENGTH};

/**
 * Validates email format and length (matches backend validation).
 * @param {{string}} email - Email address to validate
 * @returns {{{{isValid: boolean, error: string}}}} - Validation result
 */
function validateEmail(email) {{
    // Strip whitespace
    email = email.trim();
    
    // Check if empty
    if (!email) {{
        return {{ isValid: false, error: 'Email is required' }};
    }}
    
    // Check minimum length
    if (email.length < MIN_EMAIL_LENGTH) {{
        return {{ isValid: false, error: 'Email address is too short' }};
    }}
    
    // Check maximum length
    if (email.length > MAX_EMAIL_LENGTH) {{
        return {{ isValid: false, error: 'Email address is too long' }};
    }}
    
    // Check format
    if (!EMAIL_REGEX.test(email)) {{
        return {{ isValid: false, error: 'Invalid email format' }};
    }}
    
    return {{ isValid: true, error: '' }};
}}

/**
 * Simple boolean check if email is valid.
 * @param {{string}} email - Email address to validate
 * @returns {{boolean}} - True if valid
 */
function isValidEmail(email) {{
    return validateEmail(email).isValid;
}}
"""

# Export validation constants for other modules
__all__ = [
    'EMAIL_REGEX',
    'EMAIL_REGEX_JS',
    'MAX_EMAIL_LENGTH',
    'MIN_EMAIL_LENGTH',
    'validate_email',
    'is_valid_email',
    'normalize_email',
    'JAVASCRIPT_VALIDATION_PATTERN'
]
