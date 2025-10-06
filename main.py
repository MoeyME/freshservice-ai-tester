#!/usr/bin/env python3
"""
IT Ticket Email Generator
Generates and sends realistic IT support ticket emails for testing purposes.
"""

import sys
from typing import Optional

from auth import GraphAuthenticator, validate_credentials
from content_generator import ContentGenerator, validate_api_key
from email_sender import EmailSender
from logger import TicketLogger
from ticket_counter import TicketCounter
from config import load_env_file, get_config, get_integer_config
from utils import (
    read_categories,
    read_priorities_and_types,
    generate_distribution,
    calculate_distribution_stats,
    display_distribution_summary
)
from ui_styles import (
    Colors,
    print_header,
    print_section,
    print_subsection,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_status,
    print_key_value,
    print_menu_option,
    format_number,
    format_currency,
    format_email,
    format_ticket_number,
    clear_line
)


def get_user_input(prompt: str, validation_func=None, error_msg: str = "Invalid input") -> str:
    """
    Get validated input from user.

    Args:
        prompt: Prompt to display
        validation_func: Optional validation function
        error_msg: Error message for invalid input

    Returns:
        Validated user input
    """
    while True:
        value = input(f"{Colors.BRIGHT_CYAN}{prompt}{Colors.RESET}").strip()
        if not value:
            print_error("Input cannot be empty", prefix="✗")
            continue

        if validation_func and not validation_func(value):
            print_error(error_msg, prefix="✗")
            continue

        return value


def get_integer_input(prompt: str, min_value: int = 1, max_value: Optional[int] = None) -> int:
    """
    Get integer input from user.

    Args:
        prompt: Prompt to display
        min_value: Minimum allowed value
        max_value: Maximum allowed value (optional)

    Returns:
        Integer value
    """
    while True:
        try:
            value = int(input(f"{Colors.BRIGHT_CYAN}{prompt}{Colors.RESET}").strip())

            if value < min_value:
                print_error(f"Value must be at least {min_value}", prefix="✗")
                continue

            if max_value and value > max_value:
                print_error(f"Value must be at most {max_value}", prefix="✗")
                continue

            return value

        except ValueError:
            print_error("Please enter a valid number", prefix="✗")


def confirm_action(message: str) -> bool:
    """
    Ask user for yes/no confirmation.

    Args:
        message: Confirmation message

    Returns:
        True if user confirms, False otherwise
    """
    while True:
        response = input(f"{Colors.BRIGHT_YELLOW}{message} (y/n):{Colors.RESET} ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print_warning("Please enter 'y' or 'n'", prefix="⚠")


def main():
    """Main application entry point."""
    print_header("IT TICKET EMAIL GENERATOR")

    # Load environment variables
    env_vars = load_env_file()
    print()

    # Step 1: Collect configuration
    print_section("STEP 1: Configuration")

    print_subsection("Microsoft Azure Configuration")
    client_id = get_config("AZURE_CLIENT_ID", env_vars, "Enter Azure Client ID: ")
    tenant_id = get_config("AZURE_TENANT_ID", env_vars, "Enter Azure Tenant ID: ")

    if not validate_credentials(client_id, tenant_id):
        print_error("Invalid Azure credentials format")
        sys.exit(1)

    sender_email = get_config(
        "SENDER_EMAIL", env_vars,
        "Enter your email address: ",
        lambda x: '@' in x,
        "Invalid email format"
    )
    recipient_email = get_config(
        "RECIPIENT_EMAIL", env_vars,
        "Enter recipient email address: ",
        lambda x: '@' in x,
        "Invalid email format"
    )

    print_subsection("Claude API Configuration")
    claude_api_key = get_config("CLAUDE_API_KEY", env_vars, "Enter Claude API key: ")

    if not validate_api_key(claude_api_key):
        print_error("Invalid Claude API key format")
        sys.exit(1)

    # Step 2: Load data files
    print_section("STEP 2: Loading Data Files")

    try:
        categories = read_categories()
        print_success(f"Loaded {format_number(len(categories))} categories from categories.csv")

        priorities_data = read_priorities_and_types()
        priorities = priorities_data['priorities']
        types = priorities_data['types']
        print_success(f"Loaded {format_number(len(priorities))} priorities and {format_number(len(types))} types from priorities_and_types.md")

    except Exception as e:
        print_error(f"Error loading data files: {str(e)}")
        sys.exit(1)

    # Step 3: Authentication (do this once before the loop)
    print_section("STEP 3: Authentication")

    try:
        print_info("Authenticating with Microsoft...")
        authenticator = GraphAuthenticator(client_id, tenant_id)
        access_token = authenticator.authenticate_device_flow()

    except Exception as e:
        print_error(f"Authentication failed: {str(e)}")
        sys.exit(1)

    # Initialize components once
    email_sender = EmailSender(access_token, sender_email)
    ticket_counter = TicketCounter()

    # Ask for writing quality preference
    print_section("STEP 4: Writing Quality")
    print_subsection("Choose email writing quality:")
    print_menu_option("1", "Basic", "7th grade level - very casual, common mistakes, minimal punctuation")
    print_menu_option("2", "Realistic", "10th grade level - typical user writing, minor errors")
    print_menu_option("3", "Polished", "professional, well-written")

    while True:
        quality_choice = input(f"\n{Colors.BRIGHT_CYAN}Enter choice (1, 2, or 3): {Colors.RESET}").strip()
        if quality_choice == "1":
            writing_quality = "basic"
            print_success("Using basic user writing style (7th grade level)")
            break
        elif quality_choice == "2":
            writing_quality = "realistic"
            print_success("Using realistic user writing style (10th grade level)")
            break
        elif quality_choice == "3":
            writing_quality = "polished"
            print_success("Using polished professional writing style")
            break
        else:
            print_error("Please enter 1, 2, or 3")

    content_gen = ContentGenerator(claude_api_key, writing_quality=writing_quality)

    # Test connection
    print_info("Testing Microsoft Graph API connection...")
    if not email_sender.test_connection():
        print_error("Failed to connect to Microsoft Graph API")
        sys.exit(1)

    # Main loop - keep asking if user wants to send more emails
    while True:
        # Step 5: Get number of emails
        print_section("STEP 5: Email Count")

        print(f"\n{Colors.BRIGHT_CYAN}Next ticket number:{Colors.RESET} {format_ticket_number(ticket_counter.get_current())}")
        num_emails = get_integer_input("\nHow many test emails to generate? ", min_value=1, max_value=1000)

        # Get ticket range
        start_ticket, end_ticket = ticket_counter.get_range(num_emails)

        # Generate distribution
        distribution = generate_distribution(num_emails, categories, priorities, types)
        priority_counts, type_counts = calculate_distribution_stats(distribution)
        display_distribution_summary(priority_counts, type_counts)

        # Step 6: Confirm
        print_section("STEP 6: Confirmation")

        print(f"\n{Colors.BRIGHT_WHITE}Ready to generate and send {format_number(num_emails)} emails{Colors.RESET}")
        print_key_value("Ticket range:", f"{format_ticket_number(start_ticket)} to {format_ticket_number(end_ticket)}")
        print_key_value("From:", format_email(sender_email))
        print_key_value("To:", format_email(recipient_email))

        if not confirm_action("\nProceed with email generation and sending?"):
            print_warning("Operation cancelled")
            # Ask if they want to try again with different settings
            if not confirm_action("\nDo you want to send emails with different settings?"):
                break
            continue

        # Create new logger for this batch
        logger = TicketLogger()
        log_file = logger.start_log(
            client_id, tenant_id, sender_email, recipient_email,
            claude_api_key, num_emails
        )
        print_success(f"Log file created: {Colors.DIM}{log_file}{Colors.RESET}")

        # Step 7: Generation Phase
        print_section("STEP 7: Generating Email Content")

        emails_to_send = []
        generation_errors = 0

        for i, ticket in enumerate(distribution, 1):
            ticket_number = start_ticket + i - 1
            try:
                print(f"{Colors.BRIGHT_BLUE}⏳ Generating {format_ticket_number(ticket_number)} ({i} of {num_emails})...{Colors.RESET}", end="", flush=True)

                subject, description = content_gen.generate_email_content(
                    category=ticket['category'],
                    subcategory=ticket['subcategory'],
                    item=ticket['item'],
                    priority=ticket['priority'],
                    ticket_type=ticket['type'],
                    ticket_number=ticket_number
                )

                # Build full category name for logging
                category_full = ticket['category']
                if ticket['subcategory']:
                    category_full += f" > {ticket['subcategory']}"
                if ticket['item']:
                    category_full += f" > {ticket['item']}"

                emails_to_send.append({
                    'number': ticket_number,
                    'category': category_full,
                    'priority': ticket['priority'],
                    'type': ticket['type'],
                    'subject': subject,
                    'description': description
                })

                clear_line()
                print(f"{Colors.BRIGHT_GREEN}✓ Generated {format_ticket_number(ticket_number)}:{Colors.RESET} {Colors.DIM}{subject[:60]}...{Colors.RESET}")

            except Exception as e:
                clear_line()
                print_error(f"Failed to generate email {i}: {str(e)}")
                generation_errors += 1

                # Build full category name for logging
                category_full = ticket['category']
                if ticket['subcategory']:
                    category_full += f" > {ticket['subcategory']}"
                if ticket['item']:
                    category_full += f" > {ticket['item']}"

                # Log the error
                logger.log_email(
                    email_number=i,
                    category=category_full,
                    ticket_type=ticket['type'],
                    priority=ticket['priority'],
                    subject="[GENERATION FAILED]",
                    description=f"Error: {str(e)}",
                    success=False,
                    error=str(e)
                )

        if generation_errors > 0:
            print_warning(f"{generation_errors} emails failed to generate")
            if not confirm_action(f"Continue sending {len(emails_to_send)} successfully generated emails?"):
                print_warning("Operation cancelled")
                continue

        # Step 8: Sending Phase
        print_section("STEP 8: Sending Emails")

        success_count = 0
        failure_count = 0

        for i, email in enumerate(emails_to_send):
            try:
                print(f"{Colors.BRIGHT_BLUE}📧 Sending {format_ticket_number(email['number'])}:{Colors.RESET} {Colors.DIM}{email['subject'][:55]}...{Colors.RESET}", end="", flush=True)

                # Send email (with delay for subsequent emails)
                if i > 0:
                    result = email_sender.send_email_with_delay(
                        to_email=recipient_email,
                        subject=email['subject'],
                        body=email['description'],
                        delay_seconds=10,
                        show_countdown=True
                    )
                else:
                    result = email_sender.send_email(
                        to_email=recipient_email,
                        subject=email['subject'],
                        body=email['description']
                    )

                if result['success']:
                    clear_line()
                    print(f"{Colors.BRIGHT_GREEN}✓ Sent {format_ticket_number(email['number'])}:{Colors.RESET} {Colors.DIM}{email['subject'][:60]}...{Colors.RESET}")
                    success_count += 1

                    logger.log_email(
                        email_number=email['number'],
                        category=email['category'],
                        ticket_type=email['type'],
                        priority=email['priority'],
                        subject=email['subject'],
                        description=email['description'],
                        success=True
                    )
                else:
                    clear_line()
                    print_error(f"Failed {format_ticket_number(email['number'])}: {result['error']}")
                    failure_count += 1

                    logger.log_email(
                        email_number=email['number'],
                        category=email['category'],
                        ticket_type=email['type'],
                        priority=email['priority'],
                        subject=email['subject'],
                        description=email['description'],
                        success=False,
                        error=result['error']
                    )

            except Exception as e:
                clear_line()
                print_error(f"Error {format_ticket_number(email['number'])}: {str(e)}")
                failure_count += 1

                logger.log_email(
                    email_number=email['number'],
                    category=email['category'],
                    ticket_type=email['type'],
                    priority=email['priority'],
                    subject=email['subject'],
                    description=email['description'],
                    success=False,
                    error=str(e)
                )

        # Step 9: Results Summary
        print_section("STEP 9: Results Summary")

        total_attempted = len(emails_to_send)
        print_key_value("Total Generated:", format_number(total_attempted))
        print_key_value("Successfully Sent:", f"{Colors.BRIGHT_GREEN}{success_count:,}{Colors.RESET}")
        if failure_count > 0:
            print_key_value("Failed:", f"{Colors.BRIGHT_RED}{failure_count:,}{Colors.RESET}")

        if total_attempted > 0:
            success_rate = (success_count/total_attempted*100)
            rate_color = Colors.BRIGHT_GREEN if success_rate >= 90 else Colors.BRIGHT_YELLOW if success_rate >= 75 else Colors.BRIGHT_RED
            print_key_value("Success Rate:", f"{rate_color}{success_rate:.1f}%{Colors.RESET}")

        # Token and cost stats
        token_stats = content_gen.get_token_stats()
        estimated_cost = content_gen.get_estimated_cost()

        print_subsection("Claude API Usage")
        print_key_value("Total Tokens:", format_number(token_stats['total_tokens']))
        print_key_value("Estimated Cost:", format_currency(estimated_cost))

        # Distribution summary
        display_distribution_summary(priority_counts, type_counts)

        # Finalize log
        logger.finalize_log(
            total_sent=total_attempted,
            success_count=success_count,
            failure_count=failure_count,
            distribution=priority_counts,
            type_distribution=type_counts,
            estimated_cost=estimated_cost,
            token_stats=token_stats
        )

        # Save ticket counter
        ticket_counter.finalize()

        print()
        print_success(f"Batch completed! Processed {format_ticket_number(start_ticket)} to {format_ticket_number(end_ticket)}")

        # Ask if user wants to send more emails
        if not confirm_action("\nDo you want to send more emails?"):
            print_info("Session closed. Goodbye!")
            break

    # Show total session summary
    print_header("SESSION COMPLETE")
    print_subsection("Total Session Stats")
    print_key_value("Total Tokens Used:", format_number(content_gen.get_token_stats()['total_tokens']))
    print_key_value("Total Estimated Cost:", format_currency(content_gen.get_estimated_cost()))
    print(f"\n{Colors.BRIGHT_CYAN}Thank you for using IT Ticket Email Generator!{Colors.RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_YELLOW}⚠ Operation cancelled by user (Ctrl+C){Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.BRIGHT_RED}✗ Unexpected error: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
