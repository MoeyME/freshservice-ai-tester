"""
Claude API integration for generating realistic IT ticket email content.
"""

import requests
import time
from typing import Dict, Tuple, Optional
import random


class ContentGenerator:
    """Generates realistic IT ticket email content using Claude API."""

    CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

    # Pricing per 1M tokens for Claude 3.5 Haiku (cheapest Claude model)
    # https://www.anthropic.com/pricing
    COST_PER_1M_INPUT_TOKENS = 0.80  # $0.80 per 1M input tokens
    COST_PER_1M_OUTPUT_TOKENS = 4.00  # $4.00 per 1M output tokens

    # Email generation prompt template
    EMAIL_PROMPT_TEMPLATE = """Generate a realistic IT support ticket email from an end user for Dahlsens (a building supplies company).

TICKET SPECIFICATIONS:
Category: {category}
Sub-Category: {subcategory}
Item: {item}
Priority Level: {priority}
Ticket Type: {ticket_type}

PRIORITY LEVEL GUIDELINES:

Priority 1 - URGENT (Critical Incident):
- High Impact + High Urgency
- Critical business operations halted
- Examples: Entire site network down, VPN down for all users, All POS systems offline, ERP unavailable for entire site
- Tone: Urgent, stressed, business-critical
- Subject style: Direct, factual problem statement (e.g., "Can't access network", "POS systems not working", "Framework is down")

Priority 2 - HIGH (Major Incident):
- Significant disruption requiring quick resolution
- Examples: One POS unit down, PC won't boot, EFTPOS terminal not working, Production device offline, Site-wide network slowness
- Tone: Concerned, needs quick attention
- Subject style: Clear problem description (e.g., "POS terminal 2 not working", "Computer won't start", "EFTPOS down")

Priority 3 - MEDIUM (Standard):
- Issue affects work but doesn't halt operations
- Can be Incident or Service Request
- Examples: Laptop intermittently rebooting, Secondary monitor not working, Printer issues, New user account setup, Access to former employee's files
- Tone: Normal, matter-of-fact
- Subject style: Simple issue or request (e.g., "Laptop keeps restarting", "Monitor not working", "Need new user setup")

Priority 4 - LOW (Service Request):
- Minimal disruption, can be scheduled
- Examples: Peripheral requests (keyboard/mouse), Password reset, Mobile troubleshooting, General software installations, VPN issue for one user
- Tone: Polite, non-urgent
- Subject style: Simple request (e.g., "Need new keyboard", "Password reset needed", "VPN not connecting")

TICKET TYPE GUIDELINES:

Incident:
- Something is broken, not working, or malfunctioning
- Focus on the problem and its impact on work
- Examples: System crashes, network issues, hardware failures, software errors, can't access something they normally can

Service Request:
- Requesting something new or a standard service
- Focus on what is needed
- Examples: New account, access request, password reset, hardware request, software installation, information request

CRITICAL SUBJECT LINE RULES:
- NEVER include priority words like "URGENT", "HIGH PRIORITY", "CRITICAL", "EMERGENCY" in the subject
- NEVER include descriptive words like "intermittent", "occasional", "sporadic" in the subject
- DO write subjects as a user would naturally write them - short, direct, factual
- DO keep it simple: just state the problem or request (e.g., "Printer not working", "Need access to shared drive")
- The subject should be 3-8 words maximum
- Let the email body content convey the urgency, impact, and details

WRITING STYLE: {writing_style}

INSTRUCTIONS:
Create an email that:
- Has a natural, concise subject line that a real user would write (no urgency keywords, no technical jargon)
- Sounds like a real employee at a building supplies company (use appropriate context: branch staff, warehouse, sales, estimators, production, etc.)
- Matches the urgency and tone of the priority level in the EMAIL BODY (not the subject)
- Is specific to the category, sub-category, and item
- Includes realistic business impact relevant to the priority
- For incidents: describes the problem, what's not working, and how it affects their work
- For service requests: clearly states what is being requested and why they need it
- Uses Australian English spelling and terminology
- Mentions specific business functions when relevant (POS, Framework ERP, estimating, detailing, production, TAF processing, etc.)

Respond ONLY with JSON in this exact format:
{{"subject": "email subject here", "description": "email body here"}}

Do not include any other text, explanation, or markdown formatting."""

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-20241022", temperature: float = 0.85, writing_quality: str = "realistic"):
        """
        Initialize the content generator.

        Args:
            api_key: Claude API key
            model: Model to use (default: claude-3-5-haiku-20241022 - cheapest option)
            temperature: Sampling temperature for variety (0.8-0.9 recommended)
            writing_quality: "realistic" for typical user writing (10th grade level) or "polished" for well-written emails
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.writing_quality = writing_quality
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def generate_email_content(
        self,
        category: str,
        subcategory: str,
        item: str,
        priority: str,
        ticket_type: str,
        ticket_number: int,
        retry_count: int = 3
    ) -> Tuple[str, str]:
        """
        Generate email subject and description for a ticket.

        Args:
            category: IT ticket category
            subcategory: IT ticket sub-category
            item: Specific item within the sub-category
            priority: Priority level (Priority 1-4)
            ticket_type: Incident or Service Request
            ticket_number: Sequential ticket number to include in description
            retry_count: Number of retries on failure

        Returns:
            Tuple of (subject, description)

        Raises:
            Exception: If generation fails after retries
        """
        # Define writing style based on quality setting
        if self.writing_quality == "basic":
            writing_style = """BASIC USER WRITING (7th grade level):
- Very casual, conversational tone like texting a friend
- Frequent missing punctuation (no periods, commas, apostrophes)
- Inconsistent or no capitalization (lowercase preferred)
- Common spelling mistakes and typos (definately, wierd, cant, wont, dont, ur, thru)
- Run-on sentences with multiple thoughts
- Very short fragments or very long run-ons with no structure
- Minimal or excessive detail without organization
- Text-speak acceptable (plz, asap, rn, idk)
- No greetings or sign-offs usually
- Examples:
  * "laptop keeps shutting off idk whats wrong can u fix it"
  * "printer not working tried turning it off and on still broken plz help"
  * "need to get into the shared drive for project cant access it rn"
  * "my computer wont turn on i tried everything its not working at all"
  * "pos system down cant process sales need help asap"
  * "cant login to framework keeps saying wrong password but its right i think"""
        elif self.writing_quality == "realistic":
            writing_style = """REALISTIC USER WRITING (10th grade level):
- Use casual, everyday language with minor grammatical imperfections
- Include common mistakes: missing punctuation, run-on sentences, informal phrasing
- Use contractions (can't, won't, it's, doesn't)
- May have spelling errors for technical terms or typos
- Short, choppy sentences or run-on sentences
- Minimal detail unless absolutely necessary
- Examples:
  * "hi, my laptop keeps shutting down randomly can someone help?"
  * "the printer in the warehouse isnt working again, tried restarting it but no luck"
  * "need access to the shared drive for the new project asap"
  * "computer wont turn on, tried everything not sure whats wrong"""
        else:  # polished
            writing_style = """POLISHED PROFESSIONAL WRITING:
- Use proper grammar, punctuation, and sentence structure
- Clear, well-organized explanations
- Professional tone throughout
- Proper capitalization and formatting
- Complete sentences with appropriate detail
- Examples:
  * "Hello, my laptop has been shutting down randomly. Could someone please assist?"
  * "The warehouse printer is not functioning. I've attempted to restart it without success."
  * "I require access to the shared drive for the new project as soon as possible."
  * "My computer will not power on. I have tried troubleshooting steps but am unable to resolve the issue."""

        prompt = self.EMAIL_PROMPT_TEMPLATE.format(
            category=category,
            subcategory=subcategory if subcategory else "General",
            item=item if item else "General",
            priority=priority,
            ticket_type=ticket_type,
            writing_style=writing_style
        )

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": 400  # Reasonable limit for email content
        }

        last_error = None
        for attempt in range(retry_count):
            try:
                response = requests.post(
                    self.CLAUDE_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()

                    # Track token usage
                    if "usage" in result:
                        self.total_input_tokens += result["usage"].get("input_tokens", 0)
                        self.total_output_tokens += result["usage"].get("output_tokens", 0)

                    # Extract content from Claude's response format
                    content = result["content"][0]["text"].strip()

                    # Parse JSON response
                    import json
                    import re

                    try:
                        # Remove markdown code blocks if present
                        if content.startswith("```"):
                            content = content.split("```")[1]
                            if content.startswith("json"):
                                content = content[4:]
                            content = content.strip()

                        # Try to find JSON in the response
                        json_match = re.search(r'\{[^{}]*"subject"[^{}]*"description"[^{}]*\}', content, re.DOTALL)
                        if json_match:
                            content = json_match.group(0)

                        email_data = json.loads(content)
                        subject = email_data.get("subject", "").strip()
                        description = email_data.get("description", "").strip()

                        if subject and description:
                            # Add test prefix to subject for Freshservice tracking
                            subject_with_prefix = f"[TEST-TKT-{ticket_number}] {subject}"
                            # Add ticket number to description
                            description_with_ticket = f"[Ticket #{ticket_number}]\n\n{description}"
                            return subject_with_prefix, description_with_ticket
                        else:
                            raise ValueError("Empty subject or description in response")

                    except (json.JSONDecodeError, ValueError) as e:
                        # If JSON parsing fails, extract from the literal format
                        # Look for "subject": "..." and "description": "..."
                        subject_match = re.search(r'"subject"\s*:\s*"([^"]+)"', content)
                        desc_match = re.search(r'"description"\s*:\s*"([^"]+(?:\n[^"]+)*)"', content, re.DOTALL)

                        if subject_match and desc_match:
                            subject = subject_match.group(1).strip()
                            description = desc_match.group(1).strip()
                            # Add ticket number to description
                            description_with_ticket = f"[Ticket #{ticket_number}]\n\n{description}"
                            return subject, description_with_ticket

                        # Last resort: try simple text extraction
                        subject = ""
                        description = ""

                        # Try to extract subject
                        subj_match1 = re.search(r'"subject"\s*:\s*"([^"]+)"', content, re.IGNORECASE)
                        subj_match2 = re.search(r'subject:\s*([^\n]+)', content, re.IGNORECASE)
                        if subj_match1:
                            subject = subj_match1.group(1).strip()
                        elif subj_match2:
                            subject = subj_match2.group(1).strip()

                        # Try to extract description
                        desc_match1 = re.search(r'"description"\s*:\s*"([^"]+)"', content, re.IGNORECASE | re.DOTALL)
                        desc_match2 = re.search(r'description:\s*(.+)', content, re.IGNORECASE | re.DOTALL)
                        if desc_match1:
                            description = desc_match1.group(1).strip()
                        elif desc_match2:
                            description = desc_match2.group(1).strip()

                        if subject and description:
                            # Add test prefix to subject for Freshservice tracking
                            subject_with_prefix = f"[TEST-TKT-{ticket_number}] {subject}"
                            # Add ticket number to description
                            description_with_ticket = f"[Ticket #{ticket_number}]\n\n{description.strip()}"
                            return subject_with_prefix, description_with_ticket

                        raise Exception(f"Failed to parse Claude response. Content: {content[:200]}")

                elif response.status_code == 429:
                    # Rate limit - wait and retry
                    wait_time = (attempt + 1) * 2
                    print(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    last_error = "Rate limit exceeded"

                else:
                    error_msg = f"Claude API error: {response.status_code} - {response.text}"
                    last_error = error_msg
                    if attempt < retry_count - 1:
                        time.sleep(1)
                    else:
                        raise Exception(error_msg)

            except requests.exceptions.Timeout:
                last_error = "Request timeout"
                if attempt < retry_count - 1:
                    time.sleep(2)
                else:
                    raise Exception("Claude API request timed out after retries")

            except requests.exceptions.RequestException as e:
                last_error = str(e)
                if attempt < retry_count - 1:
                    time.sleep(2)
                else:
                    raise Exception(f"Claude API request failed: {e}")

        raise Exception(f"Failed to generate content after {retry_count} attempts. Last error: {last_error}")

    def get_estimated_cost(self) -> float:
        """
        Calculate estimated cost based on token usage.

        Returns:
            Estimated cost in USD
        """
        input_cost = (self.total_input_tokens / 1_000_000) * self.COST_PER_1M_INPUT_TOKENS
        output_cost = (self.total_output_tokens / 1_000_000) * self.COST_PER_1M_OUTPUT_TOKENS
        return input_cost + output_cost

    def get_token_stats(self) -> Dict[str, int]:
        """
        Get token usage statistics.

        Returns:
            Dictionary with input, output, and total tokens
        """
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens
        }


def validate_api_key(api_key: str) -> bool:
    """
    Validate Claude API key format.

    Args:
        api_key: Claude API key

    Returns:
        True if format appears valid
    """
    if not api_key:
        print("Error: Claude API key is empty")
        return False

    if not api_key.startswith("sk-ant-"):
        print("Error: Claude API key should start with 'sk-ant-'")
        return False

    if len(api_key) < 20:
        print("Error: Claude API key appears too short")
        return False

    return True
