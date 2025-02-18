"""Bill emails."""

from django.template.loader import render_to_string
from mjml.tools import mjml_render


def format_email_digest(user, keyword_dict):
    """Generate an HTML-formatted email digest for a user based on their keyword matches."""
    email_subject = "Your Daily Bill Digest"

    # Convert dictionary into a list of tuples for Django templates
    keyword_list = [{"keyword": k, "bills": v} for k, v in keyword_dict.items()]

    # Prepare context
    context = {
        "user_full_name": user.get_full_name(),
        "keyword_list": keyword_list,
        "unsubscribe_url": f"https://yourwebsite.com/unsubscribe/{user.id}",
        "profile_url": f"https://yourwebsite.com/profile/{user.id}",
    }

    # Render MJML template
    mjml_content = render_to_string("emails/digest_email.mjml", context)
    email_body = mjml_render(mjml_content)  # Convert MJML to HTML

    return email_subject, email_body
