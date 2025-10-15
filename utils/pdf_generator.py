# utils/pdf_generator.py
import os
import tempfile
from datetime import datetime
from database import init_db
from jinja2 import Template
from xhtml2pdf import pisa
from io import BytesIO
import streamlit as st
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self):
        self.template_dir = "templates"
        
    def generate_pdf_to_bytes(self, project_no):
        """Generate PDF and return as bytes"""
        try:
            # Get project data
            db = init_db()
            project_data = db.get_project_data(project_no)
            
            if not project_data:
                st.error(f"No data found for project {project_no}")
                return None
            
            # Prepare template data
            template_data = self.prepare_template_data(project_data, project_no)
            
            # Get HTML template based on WSM type
            html_template = self.get_html_template(template_data['wsm_type'])
            
            # Render template with data
            html_content = html_template.render(template_data)
            
            # Convert HTML to PDF
            pdf_bytes = self.convert_html_to_pdf(html_content)
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            st.error(f"Error generating PDF: {str(e)}")
            return None
    
    def prepare_template_data(self, project_data, project_no):
        """Prepare all data for the template"""
        template_data = {}
        
        # General Information
        general_info = project_data.get('general_info', {})
        supply_services = project_data.get('supply_services', {})
        
        # Basic project info
        template_data.update({
            'project_no': project_no,
            'wsm_type': general_info.get('wsm_type', ''),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'revision': '1.0',
        })
        
        # Client & Personnel Information
        template_data.update({
            'client': self.get_safe_value(general_info.get('client')),
            'consultant': self.get_safe_value(general_info.get('consultant')),
            'branch_engineer': self.get_safe_value(general_info.get('branch_engineer')),
            'division_engineer': self.get_safe_value(general_info.get('division_engineer')),
            'reviewed_by': self.get_safe_value(general_info.get('created_by')),
        })
        
        # Site & Technical Details
        template_data.update({
            'site': self.get_safe_value(general_info.get('site')),
            'altitude': self.get_safe_value(general_info.get('altitude')),
            'temp_min_max': self.get_safe_value(general_info.get('temp_min_max')),
            'power_voltage': self.get_safe_value(general_info.get('power_voltage')),
            'control_voltage': self.get_safe_value(general_info.get('control_voltage')),
            'frequency': self.get_safe_value(general_info.get('frequency')),
        })
        
        # Order Details
        template_data.update({
            'customer_po': self.get_safe_value(general_info.get('customer_po')),
            'po_date': self.get_safe_value(general_info.get('po_date')),
            'delivery_date': self.get_safe_value(general_info.get('delivery_date')),
            'special_delivery': self.get_safe_value(general_info.get('special_delivery')),
        })
        
        # Terms & Conditions
        template_data.update({
            'supply_payment_terms': self.get_safe_value(general_info.get('supply_payment_terms')),
            'service_payment_terms': self.get_safe_value(general_info.get('service_payment_terms')),
            'direct_orders': self.get_safe_value(general_info.get('direct_orders')),
            'fm_role': self.get_safe_value(general_info.get('fm_role')),
            'inspection': self.get_safe_value(general_info.get('inspection')),
            'price_basis': self.get_safe_value(general_info.get('price_basis')),
            'commission': self.get_safe_value(general_info.get('commission')),
            'ld_delivery_time': self.get_safe_value(general_info.get('ld_delivery_time')),
            'ld_performance': self.get_safe_value(general_info.get('ld_performance')),
        })
        
        # Boiler Information
        template_data.update({
            'boiler_type': self.get_safe_value(general_info.get('boiler_type')),
        })
        
        # Supply/Services Data
        wsm_type = general_info.get('wsm_type', 'Standard')
        if wsm_type == 'WHRB':
            self.prepare_whrb_data(template_data, supply_services)
        elif wsm_type == 'Standard':
            self.prepare_standard_data(template_data, supply_services)
        elif wsm_type == 'Electrical':
            self.prepare_electrical_data(template_data, supply_services)
        elif wsm_type == 'Non-Standard':
            self.prepare_non_standard_data(template_data, supply_services)
        else:  # Custom
            self.prepare_custom_data(template_data, supply_services)
        
        return template_data
    
    def get_safe_value(self, value):
        """Return empty string if value is None or empty"""
        if value is None:
            return ""
        return str(value).strip()
    
    def prepare_whrb_data(self, template_data, supply_services):
        """Prepare WHRB-specific data"""
        template_data.update({
            'boiler_capacity': self.get_safe_value(supply_services.get('boiler_capacity')),
            'design_pressure': self.get_safe_value(supply_services.get('design_pressure')),
            'boiler_type_whrb': self.get_safe_value(supply_services.get('boiler_type')),
            'flue_gas_pressure_drop': self.get_safe_value(supply_services.get('flue_gas_pressure_drop')),
            'flue_gas_pass_count': self.get_safe_value(supply_services.get('flue_gas_pass_count')),
            'boiler_quantity': self.get_safe_value(supply_services.get('boiler_quantity')),
            'level_controller': self.get_safe_value(supply_services.get('level_controller')),
            'pumps': self.get_safe_value(supply_services.get('pumps')),
            'motors': self.get_safe_value(supply_services.get('motors')),
            'valves': self.get_safe_value(supply_services.get('valves')),
            'flanges': self.get_safe_value(supply_services.get('flanges')),
            'insulation_density': self.get_safe_value(supply_services.get('insulation_density')),
            'insulation_thickness': self.get_safe_value(supply_services.get('insulation_thickness')),
            'cladding_material': self.get_safe_value(supply_services.get('cladding_material')),
            'construction_type': self.get_safe_value(supply_services.get('construction_type')),
            'construction_support': self.get_safe_value(supply_services.get('construction_support')),
            'orientation': self.get_safe_value(supply_services.get('orientation')),
            'design_code': self.get_safe_value(supply_services.get('design_code')),
            'genset_count': self.get_safe_value(supply_services.get('genset_count', 1)),
        })
        
        # Genset data
        for i in range(1, 7):
            template_data.update({
                f'genset_make_{i}': self.get_safe_value(supply_services.get(f'genset_make_{i}')),
                f'genset_capacity_{i}': self.get_safe_value(supply_services.get(f'genset_capacity_{i}')),
                f'genset_fuel_{i}': self.get_safe_value(supply_services.get(f'genset_fuel_{i}')),
                f'genset_model_{i}': self.get_safe_value(supply_services.get(f'genset_model_{i}')),
                f'flue_gas_flow_{i}': self.get_safe_value(supply_services.get(f'flue_gas_flow_{i}')),
                f'flue_gas_temp_{i}': self.get_safe_value(supply_services.get(f'flue_gas_temp_{i}')),
                f'back_pressure_{i}': self.get_safe_value(supply_services.get(f'back_pressure_{i}')),
                f'genset_load_{i}': self.get_safe_value(supply_services.get(f'genset_load_{i}')),
            })
    
    def prepare_standard_data(self, template_data, supply_services):
        """Prepare Standard WSM data"""
        template_data.update({
            'boiler_capacity': self.get_safe_value(supply_services.get('boiler_capacity')),
            'design_pressure': self.get_safe_value(supply_services.get('design_pressure')),
            'boiler_quantity': self.get_safe_value(supply_services.get('boiler_quantity')),
            'boiler_fuel': self.get_safe_value(supply_services.get('boiler_fuel')),
            'boiler_configuration': self.get_safe_value(supply_services.get('boiler_configuration')),
            'non_standard_requirement': self.get_safe_value(supply_services.get('non_standard_requirement')),
            'pumps': self.get_safe_value(supply_services.get('pumps')),
            'motors': self.get_safe_value(supply_services.get('motors')),
            'valves': self.get_safe_value(supply_services.get('valves')),
            'flanges': self.get_safe_value(supply_services.get('flanges')),
            'insulation_density': self.get_safe_value(supply_services.get('insulation_density')),
            'insulation_thickness': self.get_safe_value(supply_services.get('insulation_thickness')),
            'cladding_material': self.get_safe_value(supply_services.get('cladding_material')),
            'orientation': self.get_safe_value(supply_services.get('orientation')),
            'boiler_design': self.get_safe_value(supply_services.get('boiler_design')),
            'specific_design_approvals': self.get_safe_value(supply_services.get('specific_design_approvals')),
            'emissions': self.get_safe_value(supply_services.get('emissions')),
            'boiler_other_requirements': self.get_safe_value(supply_services.get('boiler_other_requirements')),
        })
    
    def prepare_electrical_data(self, template_data, supply_services):
        """Prepare Electrical WSM data"""
        template_data.update({
            'boiler_capacity': self.get_safe_value(supply_services.get('boiler_capacity')),
            'design_pressure': self.get_safe_value(supply_services.get('design_pressure')),
            'boiler_quantity': self.get_safe_value(supply_services.get('boiler_quantity')),
            'heater_element': self.get_safe_value(supply_services.get('heater_element')),
            'boiler_configuration': self.get_safe_value(supply_services.get('boiler_configuration')),
            'pumps': self.get_safe_value(supply_services.get('pumps')),
            'pump_configuration': self.get_safe_value(supply_services.get('pump_configuration')),
            'motors': self.get_safe_value(supply_services.get('motors')),
            'valves': self.get_safe_value(supply_services.get('valves')),
            'flanges': self.get_safe_value(supply_services.get('flanges')),
            'insulation_cladding': self.get_safe_value(supply_services.get('insulation_cladding')),
            'insulation_density': self.get_safe_value(supply_services.get('insulation_density')),
            'insulation_thickness': self.get_safe_value(supply_services.get('insulation_thickness')),
            'cladding_material': self.get_safe_value(supply_services.get('cladding_material')),
            'orientation': self.get_safe_value(supply_services.get('orientation')),
            'boiler_design': self.get_safe_value(supply_services.get('boiler_design')),
            'specific_design_approvals': self.get_safe_value(supply_services.get('specific_design_approvals')),
            'emissions': self.get_safe_value(supply_services.get('emissions')),
        })
    
    def prepare_non_standard_data(self, template_data, supply_services):
        """Prepare Non-Standard WSM data"""
        template_data.update({
            'boiler_capacity': self.get_safe_value(supply_services.get('boiler_capacity')),
            'design_pressure': self.get_safe_value(supply_services.get('design_pressure')),
            'boiler_quantity': self.get_safe_value(supply_services.get('boiler_quantity')),
            'boiler_fuel': self.get_safe_value(supply_services.get('boiler_fuel')),
            'boiler_configuration': self.get_safe_value(supply_services.get('boiler_configuration')),
            'non_standard_requirement': self.get_safe_value(supply_services.get('non_standard_requirement')),
            'pumps': self.get_safe_value(supply_services.get('pumps')),
            'motors': self.get_safe_value(supply_services.get('motors')),
            'valves': self.get_safe_value(supply_services.get('valves')),
            'flanges': self.get_safe_value(supply_services.get('flanges')),
            'insulation_density': self.get_safe_value(supply_services.get('insulation_density')),
            'insulation_thickness': self.get_safe_value(supply_services.get('insulation_thickness')),
            'cladding_material': self.get_safe_value(supply_services.get('cladding_material')),
            'orientation': self.get_safe_value(supply_services.get('orientation')),
            'boiler_design': self.get_safe_value(supply_services.get('boiler_design')),
            'specific_design_approvals': self.get_safe_value(supply_services.get('specific_design_approvals')),
            'emissions': self.get_safe_value(supply_services.get('emissions')),
            'boiler_other_requirements': self.get_safe_value(supply_services.get('boiler_other_requirements')),
        })
    
    def prepare_custom_data(self, template_data, supply_services):
        """Prepare Custom WSM data"""
        template_data.update({
            'custom_boiler_type': self.get_safe_value(supply_services.get('custom_boiler_type')),
            'custom_capacity': self.get_safe_value(supply_services.get('custom_capacity')),
            'custom_design_pressure': self.get_safe_value(supply_services.get('custom_design_pressure')),
            'custom_fuel_type': self.get_safe_value(supply_services.get('custom_fuel_type')),
            'custom_quantity': self.get_safe_value(supply_services.get('custom_quantity')),
            'custom_configuration': self.get_safe_value(supply_services.get('custom_configuration')),
            'special_requirements': self.get_safe_value(supply_services.get('special_requirements')),
            'custom_pumps': self.get_safe_value(supply_services.get('custom_pumps')),
            'custom_motors': self.get_safe_value(supply_services.get('custom_motors')),
            'custom_valves': self.get_safe_value(supply_services.get('custom_valves')),
            'custom_control_system': self.get_safe_value(supply_services.get('custom_control_system')),
            'custom_electrical': self.get_safe_value(supply_services.get('custom_electrical')),
            'custom_insulation': self.get_safe_value(supply_services.get('custom_insulation')),
            'design_approvals': self.get_safe_value(supply_services.get('design_approvals')),
            'emissions_requirements': self.get_safe_value(supply_services.get('emissions_requirements')),
            'other_custom_requirements': self.get_safe_value(supply_services.get('other_custom_requirements')),
        })
    
    def get_html_template(self, wsm_type):
        """Get the appropriate HTML template based on WSM type"""
        # For now, use a generic template. You can create specific templates for each WSM type
        template_content = self.get_generic_template()
        return Template(template_content)
    
    def get_generic_template(self):
        """Return a generic HTML template for all WSM types"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
                .section { margin-bottom: 25px; }
                .section-title { background-color: #f0f0f0; padding: 8px; font-weight: bold; border-left: 4px solid #333; }
                .table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                .table th { background-color: #f5f5f5; font-weight: bold; }
                .info-row { margin: 5px 0; }
                .info-label { font-weight: bold; display: inline-block; width: 200px; }
                .page-break { page-break-after: always; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ wsm_type }} WORKSHEET FOR MANUFACTURING</h1>
                <p><strong>Project No:</strong> {{ project_no }} | <strong>Date:</strong> {{ date }} | <strong>Revision:</strong> {{ revision }}</p>
            </div>

            <div class="section">
                <div class="section-title">GENERAL INFORMATION</div>
                
                <div class="info-row"><span class="info-label">Client:</span> {{ client }}</div>
                <div class="info-row"><span class="info-label">Site:</span> {{ site }}</div>
                <div class="info-row"><span class="info-label">Consultant:</span> {{ consultant }}</div>
                <div class="info-row"><span class="info-label">Branch Engineer:</span> {{ branch_engineer }}</div>
                <div class="info-row"><span class="info-label">Division Engineer:</span> {{ division_engineer }}</div>
                <div class="info-row"><span class="info-label">Altitude:</span> {{ altitude }}</div>
                <div class="info-row"><span class="info-label">Temp Min/Max:</span> {{ temp_min_max }}</div>
                <div class="info-row"><span class="info-label">Power Voltage:</span> {{ power_voltage }}</div>
                <div class="info-row"><span class="info-label">Control Voltage:</span> {{ control_voltage }}</div>
                <div class="info-row"><span class="info-label">Frequency:</span> {{ frequency }}</div>
                <div class="info-row"><span class="info-label">Customer PO:</span> {{ customer_po }}</div>
                <div class="info-row"><span class="info-label">Delivery Date:</span> {{ delivery_date }}</div>
                <div class="info-row"><span class="info-label">PO Date:</span> {{ po_date }}</div>
                <div class="info-row"><span class="info-label">Boiler Type:</span> {{ boiler_type }}</div>
            </div>

            <div class="section">
                <div class="section-title">TERMS & CONDITIONS</div>
                
                <div class="info-row"><span class="info-label">Supply Payment Terms:</span> {{ supply_payment_terms }}</div>
                <div class="info-row"><span class="info-label">Service Payment Terms:</span> {{ service_payment_terms }}</div>
                <div class="info-row"><span class="info-label">Direct Orders:</span> {{ direct_orders }}</div>
                <div class="info-row"><span class="info-label">FM Role:</span> {{ fm_role }}</div>
                <div class="info-row"><span class="info-label">Inspection:</span> {{ inspection }}</div>
                <div class="info-row"><span class="info-label">Price Basis:</span> {{ price_basis }}</div>
                <div class="info-row"><span class="info-label">Commission:</span> {{ commission }}</div>
                <div class="info-row"><span class="info-label">Special Delivery:</span> {{ special_delivery }}</div>
                <div class="info-row"><span class="info-label">LD - Delivery Time:</span> {{ ld_delivery_time }}</div>
                <div class="info-row"><span class="info-label">LD - Performance:</span> {{ ld_performance }}</div>
            </div>

            <div class="section">
                <div class="section-title">SUPPLY/SERVICES DETAILS</div>
                
                {% if wsm_type == 'WHRB' %}
                    <!-- WHRB Specific Content -->
                    <table class="table">
                        <tr><th colspan="2">Waste Heat Recovery Steam Boiler</th></tr>
                        <tr><td>Boiler Capacity</td><td>{{ boiler_capacity }}</td></tr>
                        <tr><td>Design Pressure</td><td>{{ design_pressure }}</td></tr>
                        <tr><td>Boiler Type</td><td>{{ boiler_type_whrb }}</td></tr>
                        <tr><td>Flue Gas Pressure Drop</td><td>{{ flue_gas_pressure_drop }}</td></tr>
                        <tr><td>Flue Gas Pass Count</td><td>{{ flue_gas_pass_count }}</td></tr>
                        <tr><td>Quantity</td><td>{{ boiler_quantity }}</td></tr>
                    </table>
                    
                {% elif wsm_type == 'Standard' %}
                    <!-- Standard WSM Content -->
                    <table class="table">
                        <tr><th colspan="2">Boiler Details</th></tr>
                        <tr><td>Boiler Capacity</td><td>{{ boiler_capacity }}</td></tr>
                        <tr><td>Design Pressure</td><td>{{ design_pressure }}</td></tr>
                        <tr><td>Quantity</td><td>{{ boiler_quantity }}</td></tr>
                        <tr><td>Fuel</td><td>{{ boiler_fuel }}</td></tr>
                        <tr><td>Boiler Configuration</td><td>{{ boiler_configuration }}</td></tr>
                    </table>
                    
                {% elif wsm_type == 'Electrical' %}
                    <!-- Electrical WSM Content -->
                    <table class="table">
                        <tr><th colspan="2">Electrical Boiler Details</th></tr>
                        <tr><td>Boiler Capacity</td><td>{{ boiler_capacity }}</td></tr>
                        <tr><td>Design Pressure</td><td>{{ design_pressure }}</td></tr>
                        <tr><td>Quantity</td><td>{{ boiler_quantity }}</td></tr>
                        <tr><td>Heater Element</td><td>{{ heater_element }}</td></tr>
                        <tr><td>Boiler Configuration</td><td>{{ boiler_configuration }}</td></tr>
                    </table>
                    
                {% else %}
                    <!-- Generic Content for other types -->
                    <table class="table">
                        <tr><th colspan="2">Boiler Configuration</th></tr>
                        <tr><td>Boiler Capacity</td><td>{{ boiler_capacity }}</td></tr>
                        <tr><td>Design Pressure</td><td>{{ design_pressure }}</td></tr>
                        <tr><td>Quantity</td><td>{{ boiler_quantity }}</td></tr>
                    </table>
                {% endif %}
            </div>

            <div class="section">
                <div class="section-title">APPROVALS</div>
                <div class="info-row"><span class="info-label">Reviewed by:</span> {{ reviewed_by }}</div>
                <div class="info-row"><span class="info-label">Date:</span> {{ date }}</div>
            </div>
        </body>
        </html>
        """
    
    def convert_html_to_pdf(self, html_content):
        """Convert HTML content to PDF bytes"""
        try:
            buffer = BytesIO()
            
            # Create PDF with error handling
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=buffer,
                encoding='UTF-8'
            )
            
            if pisa_status.err:
                logger.error(f"PDF generation error: {pisa_status.err}")
                return None
            
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error converting HTML to PDF: {str(e)}")
            return None

# Create global instance
pdf_generator = PDFGenerator()