import streamlit as st
from database import init_db

def show_standard_form(project_no):
    st.header("Standard WSM - Supply/Services Details")
    
    db = init_db()
    
    # Load existing data if any
    existing_data = db.get_project_data(project_no, 'supply_services') or {}
    
    with st.form("standard_supply_services"):
        st.subheader("1 Boiler")
        col1, col2 = st.columns(2)
        
        with col1:
            boiler_capacity = st.text_input("Boiler Capacity (F&A100 Deg C)", 
                                          value=existing_data.get('boiler_capacity', ''),
                                          key="boiler_capacity_std")
            design_pressure = st.text_input("Design Pressure", 
                                          value=existing_data.get('design_pressure', ''),
                                          key="design_pressure_std")
            boiler_quantity = st.text_input("Quantity", 
                                          value=existing_data.get('boiler_quantity', ''),
                                          key="boiler_quantity_std")
            boiler_fuel = st.text_input("Fuel", 
                                      value=existing_data.get('boiler_fuel', ''),
                                      key="boiler_fuel_std")
        
        with col2:
            boiler_type = st.selectbox("Boiler Type", 
                                     ["Modular", "Non-Modular", "Combination M/Floating Furnace", 
                                      "Marshall BE", "Modular Marshall BE"],
                                     index=0 if not existing_data.get('boiler_type') else 
                                     ["Modular", "Non-Modular", "Combination M/Floating Furnace", 
                                      "Marshall BE", "Modular Marshall BE"].index(existing_data.get('boiler_type')),
                                     key="boiler_type_std")
            boiler_configuration = st.text_input("Boiler configuration", 
                                               value=existing_data.get('boiler_configuration', ''),
                                               key="boiler_configuration_std")
            non_standard_requirement = st.text_area("Any non-standard requirement", 
                                                  value=existing_data.get('non_standard_requirement', ''),
                                                  key="non_standard_requirement_std")
        
        st.subheader("Components")
        col1, col2 = st.columns(2)
        
        with col1:
            pumps = st.text_input("Pumps", value=existing_data.get('pumps', ''), key="pumps_std")
            motors = st.text_input("Motors", value=existing_data.get('motors', ''), key="motors_std")
            valves = st.text_input("Valves", value=existing_data.get('valves', ''), key="valves_std")
        
        with col2:
            flanges = st.text_input("Flanges", value=existing_data.get('flanges', ''), key="flanges_std")
            insulation_cladding = st.text_input("Insulation & Cladding", 
                                              value=existing_data.get('insulation_cladding', ''),
                                              key="insulation_cladding_std")
        
        st.subheader("Insulation Details")
        col1, col2 = st.columns(2)
        
        with col1:
            insulation_density = st.text_input("Insulation Density", 
                                             value=existing_data.get('insulation_density', ''),
                                             key="insulation_density_std")
            insulation_thickness = st.text_input("Insulation thickness", 
                                               value=existing_data.get('insulation_thickness', ''),
                                               key="insulation_thickness_std")
        
        with col2:
            cladding_material = st.text_input("Cladding Material", 
                                            value=existing_data.get('cladding_material', ''),
                                            key="cladding_material_std")
            orientation = st.selectbox("Orientation", 
                                     ["Std.", "Mirror"],
                                     index=0 if not existing_data.get('orientation') else 
                                     ["Std.", "Mirror"].index(existing_data.get('orientation')),
                                     key="orientation_std")
        
        st.subheader("Design & Approvals")
        col1, col2 = st.columns(2)
        
        with col1:
            boiler_design = st.selectbox("Boiler Design", 
                                       ["IBR", "BS", "EN"],
                                       index=0 if not existing_data.get('boiler_design') else 
                                       ["IBR", "BS", "EN"].index(existing_data.get('boiler_design')),
                                       key="boiler_design_std")
            specific_design_approvals = st.text_input("Specific Design Approvals", 
                                                    value=existing_data.get('specific_design_approvals', ''),
                                                    key="specific_design_approvals_std")
        
        with col2:
            emissions = st.selectbox("Emissions", 
                                   ["Std.", "Non-Std."],
                                   index=0 if not existing_data.get('emissions') else 
                                   ["Std.", "Non-Std."].index(existing_data.get('emissions')),
                                   key="emissions_std")
            boiler_other_requirements = st.text_area("Other Requirement/Special Instructions", 
                                                   value=existing_data.get('boiler_other_requirements', ''),
                                                   key="boiler_other_requirements_std")
        
        st.subheader("2 Water Level Control")
        wlc_type = st.text_input("Std. - WLC type /Single/Two element control",
                               value=existing_data.get('wlc_type', ''),
                               key="wlc_type_std")
        water_level_control_type = st.text_input("Type of water level control",
                                               value=existing_data.get('water_level_control_type', ''),
                                               key="water_level_control_type_std")
        wlc_other_requirements = st.text_area("Other Requirement/Special Instructions - WLC",
                                            value=existing_data.get('wlc_other_requirements', ''),
                                            key="wlc_other_requirements_std")
        
        st.subheader("3 Burner")
        col1, col2 = st.columns(2)
        
        with col1:
            burner_type = st.text_input("Type", value=existing_data.get('burner_type', ''), key="burner_type_std")
            burner_make = st.text_input("Make", value=existing_data.get('burner_make', ''), key="burner_make_std")
            burner_model = st.text_input("Model", value=existing_data.get('burner_model', ''), key="burner_model_std")
        
        with col2:
            burner_quantity = st.text_input("Quantity", value=existing_data.get('burner_quantity', ''), key="burner_quantity_b_std")
            burner_modulation = st.selectbox("Modulation", 
                                           ["On-Off", "High Low", "3 Stage", "Stepless"],
                                           index=0 if not existing_data.get('burner_modulation') else 
                                           ["On-Off", "High Low", "3 Stage", "Stepless"].index(existing_data.get('burner_modulation')),
                                           key="burner_modulation_std")
            fm_burner_regulation = st.selectbox("FM burner Regulation", 
                                              ["ECR-M", "ECR-P", "ECR-A", "MCR"],
                                              index=0 if not existing_data.get('fm_burner_regulation') else 
                                              ["ECR-M", "ECR-P", "ECR-A", "MCR"].index(existing_data.get('fm_burner_regulation')),
                                              key="fm_burner_regulation_std")
        
        st.subheader("Burner Details (Continued)")
        col1, col2 = st.columns(2)
        
        with col1:
            primary_fuel = st.text_input("Primary Fuel", value=existing_data.get('primary_fuel', ''), key="primary_fuel_std")
            secondary_fuel = st.text_input("Secondary fuel", value=existing_data.get('secondary_fuel', ''), key="secondary_fuel_std")
            burner_bloc_type = st.selectbox("Type (Monobloc/ Dual Bloc)", 
                                          ["Monobloc", "Dual Bloc"],
                                          index=0 if not existing_data.get('burner_bloc_type') else 
                                          ["Monobloc", "Dual Bloc"].index(existing_data.get('burner_bloc_type')),
                                          key="burner_bloc_type_std")
        
        with col2:
            burner_fan = st.selectbox("Fan (Burner Mfg./Local)", 
                                    ["Burner Mfg.", "Local"],
                                    index=0 if not existing_data.get('burner_fan') else 
                                    ["Burner Mfg.", "Local"].index(existing_data.get('burner_fan')),
                                    key="burner_fan_std")
            lp_gas_train = st.text_input("LP Gas train", value=existing_data.get('lp_gas_train', ''), key="lp_gas_train_std")
            o2_trimming = st.text_input("O2 trimming (Yes/No) and Details", 
                                      value=existing_data.get('o2_trimming', ''),
                                      key="o2_trimming_std")
        
        vfd_details = st.text_input("VFD (Yes/No) and Details", 
                                  value=existing_data.get('vfd_details', ''),
                                  key="vfd_details_std")
        burner_other_requirements = st.text_area("Other Requirement/Special Instructions - Burner",
                                               value=existing_data.get('burner_other_requirements', ''),
                                               key="burner_other_requirements_b_std")
        special_makes = st.text_area("Mention Special Makes, if any",
                                   value=existing_data.get('special_makes', ''),
                                   key="special_makes_std")
        
        st.subheader("4 Combustion Blower")
        col1, col2 = st.columns(2)
        
        with col1:
            combustion_blower_flow = st.text_input("Flow", value=existing_data.get('combustion_blower_flow', ''), key="combustion_blower_flow_std")
            combustion_blower_head = st.text_input("Head", value=existing_data.get('combustion_blower_head', ''), key="combustion_blower_head_std")
        
        with col2:
            vfd_suitable_motors = st.selectbox("Motors suitable for VFD (Yes/No)", 
                                             ["Yes", "No"],
                                             index=0 if not existing_data.get('vfd_suitable_motors') else 
                                             ["Yes", "No"].index(existing_data.get('vfd_suitable_motors')),
                                             key="vfd_suitable_motors_std")
            silencer = st.selectbox("Silencer (Yes/No)", 
                                  ["Yes", "No"],
                                  index=0 if not existing_data.get('silencer') else 
                                  ["Yes", "No"].index(existing_data.get('silencer')),
                                  key="silencer_std")
        
        noise_level = st.selectbox("Noise level (Std. /Non-Std.)", 
                                 ["Std.", "Non-Std."],
                                 index=0 if not existing_data.get('noise_level') else 
                                 ["Std.", "Non-Std."].index(existing_data.get('noise_level')),
                                 key="noise_level_std")
        combustion_blower_other_requirements = st.text_area("Other Requirement/Special Instructions - Combustion Blower",
                                                          value=existing_data.get('combustion_blower_other_requirements', ''),
                                                          key="combustion_blower_other_requirements_std")
        
        st.subheader("5 Control Panel")
        col1, col2 = st.columns(2)
        
        with col1:
            control_panel_type = st.selectbox("Panel (Boiler mounted/Floor Standing)", 
                                            ["Boiler mounted", "Floor Standing"],
                                            index=0 if not existing_data.get('control_panel_type') else 
                                            ["Boiler mounted", "Floor Standing"].index(existing_data.get('control_panel_type')),
                                            key="control_panel_type_std")
            panel_configuration = st.selectbox("Panel (STD/ Compartmentalized)", 
                                            ["STD", "Compartmentalized"],
                                            index=0 if not existing_data.get('panel_configuration') else 
                                            ["STD", "Compartmentalized"].index(existing_data.get('panel_configuration')),
                                            key="panel_configuration_std")
        
        with col2:
            plc = st.selectbox("PLC - Yes/No", 
                             ["Yes", "No"],
                             index=0 if not existing_data.get('plc') else 
                             ["Yes", "No"].index(existing_data.get('plc')),
                             key="plc_std")
            plc_make = st.text_input("PLC Make", value=existing_data.get('plc_make', ''), key="plc_make_std")
        
        ip_rating = st.text_input("IP Rating", value=existing_data.get('ip_rating', ''), key="ip_rating_std")
        control_panel_other_requirements = st.text_area("Other Requirement/Special Instructions - Control Panel",
                                                      value=existing_data.get('control_panel_other_requirements', ''),
                                                      key="control_panel_other_requirements_std")
        
        st.subheader("6 Boiler Site Electricals")
        cabling_supply = st.selectbox("Cabling supply", 
                                    ["FM Factory", "Drop shipment", "Not in scope"],
                                    index=0 if not existing_data.get('cabling_supply') else 
                                    ["FM Factory", "Drop shipment", "Not in scope"].index(existing_data.get('cabling_supply')),
                                    key="cabling_supply_std")
        cable_trays = st.selectbox("Cable trays", 
                                 ["FM Factory", "Drop shipment", "Not in scope"],
                                 index=0 if not existing_data.get('cable_trays') else 
                                 ["FM Factory", "Drop shipment", "Not in scope"].index(existing_data.get('cable_trays')),
                                 key="cable_trays_std")
        electricals_other_requirements = st.text_area("Other Requirement/Special Instructions - Electricals",
                                                    value=existing_data.get('electricals_other_requirements', ''),
                                                    key="electricals_other_requirements_std")
        
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
                'insulation_cladding': insulation_cladding,
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
                'wlc_other_requirements': wlc_other_requirements,
                'burner_type': burner_type,
                'burner_make': burner_make,
                'burner_model': burner_model,
                'burner_quantity': burner_quantity,
                'burner_modulation': burner_modulation,
                'fm_burner_regulation': fm_burner_regulation,
                'primary_fuel': primary_fuel,
                'secondary_fuel': secondary_fuel,
                'burner_bloc_type': burner_bloc_type,
                'burner_fan': burner_fan,
                'lp_gas_train': lp_gas_train,
                'o2_trimming': o2_trimming,
                'vfd_details': vfd_details,
                'burner_other_requirements': burner_other_requirements,
                'special_makes': special_makes,
                'combustion_blower_flow': combustion_blower_flow,
                'combustion_blower_head': combustion_blower_head,
                'vfd_suitable_motors': vfd_suitable_motors,
                'silencer': silencer,
                'noise_level': noise_level,
                'combustion_blower_other_requirements': combustion_blower_other_requirements,
                'control_panel_type': control_panel_type,
                'panel_configuration': panel_configuration,
                'plc': plc,
                'plc_make': plc_make,
                'ip_rating': ip_rating,
                'control_panel_other_requirements': control_panel_other_requirements,
                'cabling_supply': cabling_supply,
                'cable_trays': cable_trays,
                'electricals_other_requirements': electricals_other_requirements
            }
            
            if db.update_project_data(project_no, 'supply_services', form_data):
                st.success("Supply/Services details saved successfully!")
            else:
                st.error("Error saving data")