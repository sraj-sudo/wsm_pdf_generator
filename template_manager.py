# templates/template_manager.py
from jinja2 import Template
from datetime import datetime, date
import os

def get_available_templates():
    """Get list of available templates from the templates folder"""
    templates = {}
    templates_dir = os.path.dirname(os.path.abspath(__file__))

    # Look for all HTML files in the templates directory
    for file in os.listdir(templates_dir):
        if file.endswith('.html') and not file.startswith('_'):
            template_key = file.replace('.html', '').upper()
            template_name = file.replace('.html', '').replace('_', ' ').title()
            templates[template_key] = template_name
    return templates

def _format_value(v):
    """Return a string representation for template rendering"""
    if v is None:
        return ''
    if isinstance(v, datetime):
        return v.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(v, date):
        return v.isoformat()
    return str(v)

def get_template_content(template_name, project_data):
    """Get template content by name and populate with project data"""
    # Ensure project_data is a dict copy so we don't mutate caller's object
    pdata = {k: _format_value(v) for k, v in (project_data or {}).items()}

    # Add generated date and alias 'date'
    pdata.setdefault('generated_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    pdata.setdefault('date', pdata['generated_date'])

    # Validate template exists
    available_templates = get_available_templates()
    if template_name not in available_templates:
        # allow direct filename (without extension)
        # if template_name contains .html, strip it
        tn = template_name.replace('.html','').upper()
        if tn in available_templates:
            template_name = tn
        else:
            raise ValueError(f"Template '{template_name}' does not exist. Available templates: {', '.join(available_templates.keys())}")

    templates_dir = os.path.dirname(os.path.abspath(__file__))
    # If a file with the given name exists in the folder, use it
    possible_file = os.path.join(templates_dir, f"{template_name}.html")
    if os.path.exists(possible_file):
        template_file = possible_file
    else:
        # try to find any file matching case-insensitively
        found = None
        for file in os.listdir(templates_dir):
            if file.lower().startswith(template_name.lower()):
                found = os.path.join(templates_dir, file)
                break
        if found:
            template_file = found
        else:
            raise FileNotFoundError(f"Template file '{template_name}.html' not found in templates directory")

    with open(template_file, 'r', encoding='utf-8') as f:
        html_template = f.read()

    # Render using Jinja2
    try:
        template = Template(html_template)
        return template.render(**pdata)
    except Exception as e:
        raise ValueError(f"Error rendering template '{template_name}': {str(e)}")

def validate_template_exists(template_name):
    """Validate if a template exists"""
    available_templates = get_available_templates()
    return template_name in available_templates

def get_template_display_name(template_key):
    """Get the display name for a template key"""
    available_templates = get_available_templates()
    return available_templates.get(template_key, template_key)
