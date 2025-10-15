import streamlit as st
from database import init_db

def show_non_standard_form(project_no):
    st.header("Non-Standard WSM - Supply/Services Details")
    
    db = init_db()
    existing_data = db.get_project_data(project_no, 'supply_services') or {}
    
    with st.form("non_standard_supply_services"):
        st.subheader("1 Boiler - Non-Standard Requirements")
        
        col1, col2 = st.columns(2)
        
        with col1:
            boiler_capacity = st.text_input("Boiler Capacity (F&A100 Deg C)", 
                                          value=existing_data.get('boiler_capacity', ''),
                                          key="boiler_capacity_ns")
            design_pressure = st.text_input("Design Pressure", 
                                          value=existing_data.get('design_pressure', ''),
                                          key="design_pressure_ns")
            boiler_quantity = st.text_input("Quantity", 
                                          value=existing_data.get('boiler_quantity', ''),
                                          key="boiler_quantity_ns")
        
        with col2:
            boiler_fuel = st.text_input("Fuel", 
                                      value=existing_data.get('boiler_fuel', ''),
                                      key="boiler_fuel_ns")
            boiler_type = st.text_input("Boiler Type", 
                                      value=existing_data.get('boiler_type', ''),
                                      key="boiler_type_ns")
        
        boiler_configuration = st.text_input("Boiler configuration", 
                                           value=existing_data.get('boiler_configuration', ''),
                                           key="boiler_configuration_ns")
        non_standard_requirement = st.text_area("Any non-standard requirement (specification/ make etc.)", 
                                              value=existing_data.get('non_standard_requirement', ''),
                                              key="non_standard_requirement_ns")
        
        st.subheader("Components")
        col1, col2 = st.columns(2)
        
        with col1:
            pumps = st.text_input("Pumps", value=existing_data.get('pumps', ''), key="pumps_ns")
            motors = st.text_input("Motors", value=existing_data.get('motors', ''), key="motors_ns")
        
        with col2:
            valves = st.text_input("Valves", value=existing_data.get('valves', ''), key="valves_ns")
            flanges = st.text_input("Flanges", value=existing_data.get('flanges', ''), key="flanges_ns")
        
        st.subheader("Insulation & Cladding")
        col1, col2 = st.columns(2)
        
        with col1:
            insulation_density = st.text_input("Insulation Density", 
                                             value=existing_data.get('insulation_density', ''),
                                             key="insulation_density_ns")
            insulation_thickness = st.text_input("Insulation thickness", 
                                               value=existing_data.get('insulation_thickness', ''),
                                               key="insulation_thickness_ns")
        
        with col2:
            cladding_material = st.text_input("Cladding Material (SS/ Aluminum)", 
                                            value=existing_data.get('cladding_material', ''),
                                            key="cladding_material_ns")
            orientation = st.selectbox("Orientation (Std./Mirror)", 
                                     ["Std.", "Mirror"],
                                     index=0 if not existing_data.get('orientation') else 
                                     ["Std.", "Mirror"].index(existing_data.get('orientation')),
                                     key="orientation_ns")
        
        st.subheader("Design & Approvals")
        col1, col2 = st.columns(2)
        
        with col1:
            boiler_design = st.selectbox("Boiler Design (IBR/BS/EN)", 
                                       ["IBR", "BS", "EN"],
                                       index=0 if not existing_data.get('boiler_design') else 
                                       ["IBR", "BS", "EN"].index(existing_data.get('boiler_design')),
                                       key="boiler_design_ns")
        
        with col2:
            specific_design_approvals = st.text_input("Specific Design Approvals (DOSH etc.)", 
                                                    value=existing_data.get('specific_design_approvals', ''),
                                                    key="specific_design_approvals_ns")
        
        emissions = st.text_input("Emissions (Std./Non-Std.)", 
                                value=existing_data.get('emissions', ''),
                                key="emissions_ns")
        boiler_other_requirements = st.text_area("Other Requirement/Special Instructions", 
                                               value=existing_data.get('boiler_other_requirements', ''),
                                               key="boiler_other_requirements_ns")
        
        st.subheader("2 Water Level Control")
        wlc_type = st.text_input("Std. - WLC type /Single/Two element control",
                               value=existing_data.get('wlc_type', ''),
                               key="wlc_type_ns")
        water_level_control_type = st.text_input("Type of water level control (Std. WLC type /VFD based/Control valve)",
                                               value=existing_data.get('water_level_control_type', ''),
                                               key="water_level_control_type_ns")
        wlc_other_requirements = st.text_area("Other Requirement/Special Instructions",
                                            value=existing_data.get('wlc_other_requirements', ''),
                                            key="wlc_other_requirements_ns")
        
        submitted = st.form_submit_button("Save Supply/Services Details")
        
        if submitted:
            form_data = {
                'boiler_capacity': boiler_capacity,
                'design_pressure': design_pressure,
                'boiler_quantity': boiler_quantity,
                'boiler_fuel': boiler_fuel,
                'boiler_type': boiler_type,
                'boiler_configuration': boiler_configuration,
                'non_standard_requirement': non_standard_requirement,
                'pumps': pumps,
                'motors': motors,
                'valves': valves,
                'flanges': flanges,
                'insulation_density': insulation_density,
                'insulation_thickness': insulation_thickness,
                'cladding_material': cladding_material,
                'orientation': orientation,
                'boiler_design': boiler_design,
                'specific_design_approvals': specific_design_approvals,
                'emissions': emissions,
                'boiler_other_requirements': boiler_other_requirements,
                'wlc_type': wlc_type,
                'water_level_control_type': water_level_control_type,
                'wlc_other_requirements': wlc_other_requirements
            }
            
            if db.update_project_data(project_no, 'supply_services', form_data):
                st.success("Supply/Services details saved successfully!")
            else:
                st.error("Error saving data")