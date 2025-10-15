import streamlit as st
from database import init_db

def show_custom_form(project_no):
    st.header("Custom WSM - Supply/Services Details")
    
    db = init_db()
    existing_data = db.get_project_data(project_no, 'supply_services') or {}
    
    with st.form("custom_supply_services"):
        st.subheader("Custom Boiler Configuration")
        
        st.write("Please provide details for your custom boiler configuration:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            custom_boiler_type = st.text_input("Custom Boiler Type", 
                                             value=existing_data.get('custom_boiler_type', ''),
                                             key="custom_boiler_type_cust")
            custom_capacity = st.text_input("Custom Capacity Specification", 
                                          value=existing_data.get('custom_capacity', ''),
                                          key="custom_capacity_cust")
            custom_design_pressure = st.text_input("Design Pressure Requirements", 
                                                 value=existing_data.get('custom_design_pressure', ''),
                                                 key="custom_design_pressure_cust")
        
        with col2:
            custom_fuel_type = st.text_input("Fuel Type/Configuration", 
                                           value=existing_data.get('custom_fuel_type', ''),
                                           key="custom_fuel_type_cust")
            custom_quantity = st.text_input("Quantity", 
                                          value=existing_data.get('custom_quantity', ''),
                                          key="custom_quantity_cust")
        
        st.subheader("Special Requirements")
        custom_configuration = st.text_area("Custom Configuration Details",
                                          value=existing_data.get('custom_configuration', ''),
                                          key="custom_configuration_cust")
        special_requirements = st.text_area("Special Requirements/Specifications",
                                          value=existing_data.get('special_requirements', ''),
                                          key="special_requirements_cust")
        
        st.subheader("Components & Systems")
        col1, col2 = st.columns(2)
        
        with col1:
            custom_pumps = st.text_input("Pump Requirements", value=existing_data.get('custom_pumps', ''), key="custom_pumps_cust")
            custom_motors = st.text_input("Motor Specifications", value=existing_data.get('custom_motors', ''), key="custom_motors_cust")
            custom_valves = st.text_input("Valve Requirements", value=existing_data.get('custom_valves', ''), key="custom_valves_cust")
        
        with col2:
            custom_control_system = st.text_input("Control System", value=existing_data.get('custom_control_system', ''), key="custom_control_system_cust")
            custom_electrical = st.text_input("Electrical Requirements", value=existing_data.get('custom_electrical', ''), key="custom_electrical_cust")
            custom_insulation = st.text_input("Insulation Specifications", value=existing_data.get('custom_insulation', ''), key="custom_insulation_cust")
        
        st.subheader("Additional Specifications")
        design_approvals = st.text_area("Design Approvals/Standards Required",
                                      value=existing_data.get('design_approvals', ''),
                                      key="design_approvals_cust")
        emissions_requirements = st.text_area("Emissions Requirements",
                                            value=existing_data.get('emissions_requirements', ''),
                                            key="emissions_requirements_cust")
        other_custom_requirements = st.text_area("Other Custom Requirements/Special Instructions",
                                               value=existing_data.get('other_custom_requirements', ''),
                                               key="other_custom_requirements_cust")
        
        submitted = st.form_submit_button("Save Custom Configuration Details")
        
        if submitted:
            form_data = {
                'custom_boiler_type': custom_boiler_type,
                'custom_capacity': custom_capacity,
                'custom_design_pressure': custom_design_pressure,
                'custom_fuel_type': custom_fuel_type,
                'custom_quantity': custom_quantity,
                'custom_configuration': custom_configuration,
                'special_requirements': special_requirements,
                'custom_pumps': custom_pumps,
                'custom_motors': custom_motors,
                'custom_valves': custom_valves,
                'custom_control_system': custom_control_system,
                'custom_electrical': custom_electrical,
                'custom_insulation': custom_insulation,
                'design_approvals': design_approvals,
                'emissions_requirements': emissions_requirements,
                'other_custom_requirements': other_custom_requirements
            }
            
            if db.update_project_data(project_no, 'supply_services', form_data):
                st.success("Custom configuration details saved successfully!")
            else:
                st.error("Error saving data")