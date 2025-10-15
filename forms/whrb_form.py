import streamlit as st
from database import init_db

def show_whrb_form(project_no):
    st.header("WHRB WSM - Supply/Services Details")
    
    db = init_db()
    existing_data = db.get_project_data(project_no, 'supply_services') or {}
    
    with st.form("whrb_supply_services"):
        st.subheader("1 Waste Heat Recovery Steam Boiler")
        
        col1, col2 = st.columns(2)
        
        with col1:
            boiler_capacity = st.text_input("Boiler Capacity with Economizer (F&A100)",
                                          value=existing_data.get('boiler_capacity', ''),
                                          key="boiler_capacity_whrb")
            design_pressure = st.text_input("Design Pressure",
                                          value=existing_data.get('design_pressure', ''),
                                          key="design_pressure_whrb")
            boiler_type = st.text_input("Type", value=existing_data.get('boiler_type', ''), key="boiler_type_whrb")
        
        with col2:
            flue_gas_pressure_drop = st.text_input("Allowable Flue gas side pressure drop (Boiler + economizer + damper)",
                                                 value=existing_data.get('flue_gas_pressure_drop', ''),
                                                 key="flue_gas_pressure_drop_whrb")
            flue_gas_pass_count = st.text_input("Number of flue gas pass",
                                              value=existing_data.get('flue_gas_pass_count', ''),
                                              key="flue_gas_pass_count_whrb")
            boiler_quantity = st.text_input("Qty of boiler", value=existing_data.get('boiler_quantity', ''), key="boiler_quantity_whrb")
        
        st.subheader("Components")
        col1, col2 = st.columns(2)
        
        with col1:
            level_controller = st.text_input("Level controller", value=existing_data.get('level_controller', ''), key="level_controller_whrb")
            pumps = st.text_input("Pumps", value=existing_data.get('pumps', ''), key="pumps_whrb")
            motors = st.text_input("Motor", value=existing_data.get('motors', ''), key="motors_whrb")
        
        with col2:
            valves = st.text_input("Valves", value=existing_data.get('valves', ''), key="valves_whrb")
            flanges = st.text_input("Flanges", value=existing_data.get('flanges', ''), key="flanges_whrb")
        
        st.subheader("Insulation & Cladding")
        col1, col2 = st.columns(2)
        
        with col1:
            insulation_density = st.text_input("Insulation Density", 
                                             value=existing_data.get('insulation_density', ''),
                                             key="insulation_density_whrb")
            insulation_thickness = st.text_input("Insulation thickness", 
                                               value=existing_data.get('insulation_thickness', ''),
                                               key="insulation_thickness_whrb")
            cladding_material = st.selectbox("Cladding Material (SS/ Al / Gl)", 
                                           ["SS", "Al", "Gl"],
                                           index=0 if not existing_data.get('cladding_material') else 
                                           ["SS", "Al", "Gl"].index(existing_data.get('cladding_material')),
                                           key="cladding_material_whrb")
        
        with col2:
            construction_type = st.selectbox("Construction (Box/Round)", 
                                           ["Box", "Round"],
                                           index=0 if not existing_data.get('construction_type') else 
                                           ["Box", "Round"].index(existing_data.get('construction_type')),
                                           key="construction_type_whrb")
            construction_support = st.selectbox("Construction (Saddle/ Skid)", 
                                              ["Saddle", "Skid"],
                                              index=0 if not existing_data.get('construction_support') else 
                                              ["Saddle", "Skid"].index(existing_data.get('construction_support')),
                                              key="construction_support_whrb")
            orientation = st.selectbox("Orientation (Horizontal/Std/Mirror)", 
                                     ["Horizontal", "Std", "Mirror"],
                                     index=0 if not existing_data.get('orientation') else 
                                     ["Horizontal", "Std", "Mirror"].index(existing_data.get('orientation')),
                                     key="orientation_whrb")
        
        design_code = st.text_input("Design code", value=existing_data.get('design_code', ''), key="design_code_whrb")
        
        st.subheader("Genset Information")
        genset_count = st.number_input("Number of Gensets", min_value=1, max_value=6, 
                                     value=existing_data.get('genset_count', 1),
                                     key="genset_count_whrb")
        
        gensets_data = {}
        for i in range(1, genset_count + 1):
            st.write(f"### Genset {i}")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                gensets_data[f'genset_make_{i}'] = st.text_input(f"Genset Make {i}", 
                                                               value=existing_data.get(f'genset_make_{i}', ''),
                                                               key=f"make_{i}_whrb")
                gensets_data[f'genset_capacity_{i}'] = st.text_input(f"Genset Capacity {i}",
                                                                   value=existing_data.get(f'genset_capacity_{i}', ''),
                                                                   key=f"capacity_{i}_whrb")
            
            with col2:
                gensets_data[f'genset_fuel_{i}'] = st.text_input(f"Genset Fuel {i}",
                                                               value=existing_data.get(f'genset_fuel_{i}', ''),
                                                               key=f"fuel_{i}_whrb")
                gensets_data[f'genset_model_{i}'] = st.text_input(f"Genset Model {i}",
                                                                value=existing_data.get(f'genset_model_{i}', ''),
                                                                key=f"model_{i}_whrb")
            
            with col3:
                gensets_data[f'flue_gas_flow_{i}'] = st.text_input(f"Genset Flue Gas Flow Rate {i}",
                                                                 value=existing_data.get(f'flue_gas_flow_{i}', ''),
                                                                 key=f"flow_{i}_whrb")
                gensets_data[f'flue_gas_temp_{i}'] = st.text_input(f"Flue Gas Temp {i}",
                                                                 value=existing_data.get(f'flue_gas_temp_{i}', ''),
                                                                 key=f"temp_{i}_whrb")
            
            gensets_data[f'back_pressure_{i}'] = st.text_input(f"Allowable Back Pressure {i}",
                                                             value=existing_data.get(f'back_pressure_{i}', ''),
                                                             key=f"pressure_{i}_whrb")
            gensets_data[f'genset_load_{i}'] = st.text_input(f"Load on Genset {i} (%)",
                                                           value=existing_data.get(f'genset_load_{i}', '100'),
                                                           key=f"load_{i}_whrb")
        
        st.subheader("2 Three Way Electrically Actuated Dampers")
        col1, col2 = st.columns(2)
        
        with col1:
            damper_type = st.text_input("Type", value=existing_data.get('damper_type', ''), key="damper_type_whrb")
            damper_make = st.text_input("Make", value=existing_data.get('damper_make', ''), key="damper_make_whrb")
            damper_size = st.text_input("Size (As per design)", value=existing_data.get('damper_size', ''), key="damper_size_whrb")
        
        with col2:
            flue_gas_max_temp = st.text_input("Flue gas max temp", value=existing_data.get('flue_gas_max_temp', ''), key="flue_gas_max_temp_whrb")
            damper_moc = st.text_input("MOC", value=existing_data.get('damper_moc', ''), key="damper_moc_whrb")
            damper_orientation = st.text_input("Damper orientation for dampers", 
                                             value=existing_data.get('damper_orientation', ''),
                                             key="damper_orientation_whrb")
        
        st.subheader("3 Expansion Bellows")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Before Expansion**")
            bellow_before_location = st.text_input("Location", 
                                                 value=existing_data.get('bellow_before_location', 'Inlet of boiler'),
                                                 key="bellow_before_location_whrb")
            bellow_before_suitable = st.text_input("Suitable", 
                                                 value=existing_data.get('bellow_before_suitable', 'For flue gas inlet temp.'),
                                                 key="bellow_before_suitable_whrb")
        
        with col2:
            st.write("**After Expansion**")
            bellow_after_location = st.text_input("Location After", 
                                                value=existing_data.get('bellow_after_location', ''),
                                                key="bellow_after_location_whrb")
            bellow_after_suitable = st.text_input("Suitable After", 
                                                value=existing_data.get('bellow_after_suitable', ''),
                                                key="bellow_after_suitable_whrb")
        
        st.subheader("4 Economizer")
        col1, col2 = st.columns(2)
        
        with col1:
            economizer_type = st.text_input("Type", value=existing_data.get('economizer_type', ''), key="economizer_type_whrb")
            economizer_quantity = st.text_input("Quantity", value=existing_data.get('economizer_quantity', ''), key="economizer_quantity_whrb")
            water_inlet_temp = st.text_input("Water inlet temp", value=existing_data.get('water_inlet_temp', ''), key="water_inlet_temp_whrb")
        
        with col2:
            flue_gas_outlet_temp_max = st.text_input("Flue gas outlet temp max", 
                                                   value=existing_data.get('flue_gas_outlet_temp_max', 'NA'),
                                                   key="flue_gas_outlet_temp_max_whrb")
            economizer_insulation = st.text_input("Insulation", value=existing_data.get('economizer_insulation', ''), key="economizer_insulation_whrb")
            economizer_cladding = st.text_input("Cladding", value=existing_data.get('economizer_cladding', ''), key="economizer_cladding_whrb")
        
        economizer_pressure_drop = st.text_input("Flue Gas side Pressure Drop", 
                                               value=existing_data.get('economizer_pressure_drop', ''),
                                               key="economizer_pressure_drop_whrb")
        isolation_valves = st.text_input("Isolation valves, Drain, Vent", 
                                       value=existing_data.get('isolation_valves', 'NA'),
                                       key="isolation_valves_whrb")
        
        submitted = st.form_submit_button("Save Supply/Services Details")
        
        if submitted:
            form_data = {
                'boiler_capacity': boiler_capacity,
                'design_pressure': design_pressure,
                'boiler_type': boiler_type,
                'flue_gas_pressure_drop': flue_gas_pressure_drop,
                'flue_gas_pass_count': flue_gas_pass_count,
                'boiler_quantity': boiler_quantity,
                'level_controller': level_controller,
                'pumps': pumps,
                'motors': motors,
                'valves': valves,
                'flanges': flanges,
                'insulation_density': insulation_density,
                'insulation_thickness': insulation_thickness,
                'cladding_material': cladding_material,
                'construction_type': construction_type,
                'construction_support': construction_support,
                'orientation': orientation,
                'design_code': design_code,
                'genset_count': genset_count,
                'damper_type': damper_type,
                'damper_make': damper_make,
                'damper_size': damper_size,
                'flue_gas_max_temp': flue_gas_max_temp,
                'damper_moc': damper_moc,
                'damper_orientation': damper_orientation,
                'bellow_before_location': bellow_before_location,
                'bellow_before_suitable': bellow_before_suitable,
                'bellow_after_location': bellow_after_location,
                'bellow_after_suitable': bellow_after_suitable,
                'economizer_type': economizer_type,
                'economizer_quantity': economizer_quantity,
                'water_inlet_temp': water_inlet_temp,
                'flue_gas_outlet_temp_max': flue_gas_outlet_temp_max,
                'economizer_insulation': economizer_insulation,
                'economizer_cladding': economizer_cladding,
                'economizer_pressure_drop': economizer_pressure_drop,
                'isolation_valves': isolation_valves,
                **gensets_data
            }
            
            if db.update_project_data(project_no, 'supply_services', form_data):
                st.success("Supply/Services details saved successfully!")
            else:
                st.error("Error saving data")