import streamlit as st
from database import init_db

def show_electrical_form(project_no):
    st.header("Electrical Boiler WSM - Supply/Services Details")
    
    db = init_db()
    existing_data = db.get_project_data(project_no, 'supply_services') or {}
    
    with st.form("electrical_supply_services"):
        st.subheader("1 Boiler --- 1no")
        
        col1, col2 = st.columns(2)
        
        with col1:
            boiler_capacity = st.text_input("Boiler Capacity (F&A100 Deg C)",
                                          value=existing_data.get('boiler_capacity', ''),
                                          key="boiler_capacity_elec")
            design_pressure = st.text_input("Design Pressure",
                                          value=existing_data.get('design_pressure', ''),
                                          key="design_pressure_elec")
            boiler_quantity = st.text_input("Quantity",
                                          value=existing_data.get('boiler_quantity', ''),
                                          key="boiler_quantity_elec")
        
        with col2:
            heater_element = st.text_input("Heater Element",
                                         value=existing_data.get('heater_element', ''),
                                         key="heater_element_elec")
            boiler_type = st.selectbox("Boiler Type (Modular/Non Modular)", 
                                     ["Modular", "Non Modular"],
                                     index=0 if not existing_data.get('boiler_type') else 
                                     ["Modular", "Non Modular"].index(existing_data.get('boiler_type')),
                                     key="boiler_type_elec")
        
        boiler_configuration = st.text_input("Boiler configuration (..Nos Working & ...No Stand by)",
                                           value=existing_data.get('boiler_configuration', ''),
                                           key="boiler_configuration_elec")
        
        st.subheader("Components")
        col1, col2 = st.columns(2)
        
        with col1:
            pumps = st.text_input("Pumps", value=existing_data.get('pumps', ''), key="pumps_elec")
            pump_configuration = st.text_input("Pump Configuration", value=existing_data.get('pump_configuration', ''), key="pump_configuration_elec")
            motors = st.text_input("Motors", value=existing_data.get('motors', ''), key="motors_elec")
        
        with col2:
            valves = st.text_input("Valves", value=existing_data.get('valves', ''), key="valves_elec")
            flanges = st.text_input("Flanges", value=existing_data.get('flanges', ''), key="flanges_elec")
            insulation_cladding = st.text_input("Insulation & Cladding", value=existing_data.get('insulation_cladding', ''), key="insulation_cladding_elec")
        
        st.subheader("Insulation Details")
        col1, col2 = st.columns(2)
        
        with col1:
            insulation_density = st.text_input("Insulation Density", 
                                             value=existing_data.get('insulation_density', ''),
                                             key="insulation_density_elec")
            insulation_thickness = st.text_input("Insulation thickness", 
                                               value=existing_data.get('insulation_thickness', ''),
                                               key="insulation_thickness_elec")
        
        with col2:
            cladding_material = st.text_input("Cladding Material", 
                                            value=existing_data.get('cladding_material', ''),
                                            key="cladding_material_elec")
            orientation = st.selectbox("Orientation (Std./Mirror)", 
                                     ["Std.", "Mirror"],
                                     index=0 if not existing_data.get('orientation') else 
                                     ["Std.", "Mirror"].index(existing_data.get('orientation')),
                                     key="orientation_elec")
        
        st.subheader("Design & Approvals")
        col1, col2 = st.columns(2)
        
        with col1:
            boiler_design = st.selectbox("Boiler Design (IBR/BS/EN)", 
                                       ["IBR", "BS", "EN"],
                                       index=0 if not existing_data.get('boiler_design') else 
                                       ["IBR", "BS", "EN"].index(existing_data.get('boiler_design')),
                                       key="boiler_design_elec")
        
        with col2:
            specific_design_approvals = st.text_input("Specific Design Approvals (DOSH etc.)", 
                                                    value=existing_data.get('specific_design_approvals', ''),
                                                    key="specific_design_approvals_elec")
        
        emissions = st.text_input("Emissions (Std./Non-Std.)", 
                                value=existing_data.get('emissions', ''),
                                key="emissions_elec")
        
        st.subheader("2 Water Level Control --- 1 Set")
        wlc_type = st.text_input("Std. - WLC type /Single/Two element control",
                               value=existing_data.get('wlc_type', ''),
                               key="wlc_type_elec")
        water_level_control_type = st.text_input("Type of water level control (Std. WLC type /VFD based/Control valve)",
                                               value=existing_data.get('water_level_control_type', ''),
                                               key="water_level_control_type_elec")
        
        st.subheader("3 Electric Heater --- 1 set")
        col1, col2 = st.columns(2)
        
        with col1:
            electric_heater_type = st.text_input("Type", value=existing_data.get('electric_heater_type', ''), key="electric_heater_type_elec")
            electric_heater_make = st.text_input("Make", value=existing_data.get('electric_heater_make', ''), key="electric_heater_make_elec")
            electric_heater_model = st.text_input("Model", value=existing_data.get('electric_heater_model', ''), key="electric_heater_model_elec")
        
        with col2:
            electric_heater_quantity = st.text_input("Quantity", value=existing_data.get('electric_heater_quantity', ''), key="electric_heater_quantity_elec")
            electric_heater_modulation = st.selectbox("Modulation (On-Off/ High Low/ 3 Stage/ Stepless)", 
                                                    ["On-Off", "High Low", "3 Stage", "Stepless"],
                                                    index=0 if not existing_data.get('electric_heater_modulation') else 
                                                    ["On-Off", "High Low", "3 Stage", "Stepless"].index(existing_data.get('electric_heater_modulation')),
                                                    key="electric_heater_modulation_elec")
        
        electric_heater_vfd = st.text_input("VFD (Yes/No) and Details", 
                                          value=existing_data.get('electric_heater_vfd', ''),
                                          key="electric_heater_vfd_elec")
        
        st.subheader("4 Control Panel --- 1no")
        col1, col2 = st.columns(2)
        
        with col1:
            control_panel_type = st.selectbox("Panel (Boiler mounted/Floor Standing)", 
                                            ["Boiler mounted", "Floor Standing"],
                                            index=0 if not existing_data.get('control_panel_type') else 
                                            ["Boiler mounted", "Floor Standing"].index(existing_data.get('control_panel_type')),
                                            key="control_panel_type_elec")
            panel_configuration = st.selectbox("Panel (STD/ Compartmentalized)", 
                                            ["STD", "Compartmentalized"],
                                            index=0 if not existing_data.get('panel_configuration') else 
                                            ["STD", "Compartmentalized"].index(existing_data.get('panel_configuration')),
                                            key="panel_configuration_elec")
        
        with col2:
            plc = st.selectbox("PLC - Yes/No", 
                             ["Yes", "No"],
                             index=0 if not existing_data.get('plc') else 
                             ["Yes", "No"].index(existing_data.get('plc')),
                             key="plc_elec")
            plc_make = st.text_input("PLC Make", value=existing_data.get('plc_make', ''), key="plc_make_elec")
        
        ip_rating = st.text_input("IP Rating", value=existing_data.get('ip_rating', ''), key="ip_rating_elec")
        
        st.subheader("6 Electrical")
        cabling_supply = st.selectbox("Cabling supply - FM Factory/Drop shipment/Not in scope", 
                                    ["FM Factory", "Drop shipment", "Not in scope"],
                                    index=0 if not existing_data.get('cabling_supply') else 
                                    ["FM Factory", "Drop shipment", "Not in scope"].index(existing_data.get('cabling_supply')),
                                    key="cabling_supply_elec")
        cable_trays = st.selectbox("Cable trays - FM Factory/Drop shipment/Not in scope", 
                                 ["FM Factory", "Drop shipment", "Not in scope"],
                                 index=0 if not existing_data.get('cable_trays') else 
                                 ["FM Factory", "Drop shipment", "Not in scope"].index(existing_data.get('cable_trays')),
                                 key="cable_trays_elec")
        electrical_other_requirements = st.text_area("Other Requirement/Special Instructions",
                                                   value=existing_data.get('electrical_other_requirements', ''),
                                                   key="electrical_other_requirements_elec")
        
        submitted = st.form_submit_button("Save Supply/Services Details")
        
        if submitted:
            form_data = {
                'boiler_capacity': boiler_capacity,
                'design_pressure': design_pressure,
                'boiler_quantity': boiler_quantity,
                'heater_element': heater_element,
                'boiler_type': boiler_type,
                'boiler_configuration': boiler_configuration,
                'pumps': pumps,
                'pump_configuration': pump_configuration,
                'motors': motors,
                'valves': valves,
                'flanges': flanges,
                'insulation_cladding': insulation_cladding,
                'insulation_density': insulation_density,
                'insulation_thickness': insulation_thickness,
                'cladding_material': cladding_material,
                'orientation': orientation,
                'boiler_design': boiler_design,
                'specific_design_approvals': specific_design_approvals,
                'emissions': emissions,
                'wlc_type': wlc_type,
                'water_level_control_type': water_level_control_type,
                'electric_heater_type': electric_heater_type,
                'electric_heater_make': electric_heater_make,
                'electric_heater_model': electric_heater_model,
                'electric_heater_quantity': electric_heater_quantity,
                'electric_heater_modulation': electric_heater_modulation,
                'electric_heater_vfd': electric_heater_vfd,
                'control_panel_type': control_panel_type,
                'panel_configuration': panel_configuration,
                'plc': plc,
                'plc_make': plc_make,
                'ip_rating': ip_rating,
                'cabling_supply': cabling_supply,
                'cable_trays': cable_trays,
                'electrical_other_requirements': electrical_other_requirements
            }
            
            if db.update_project_data(project_no, 'supply_services', form_data):
                st.success("Supply/Services details saved successfully!")
            else:
                st.error("Error saving data")