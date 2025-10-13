# app.py
import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime
import uuid
from database import init_db, get_db_connection, update_project_status, get_all_projects, get_project_by_number

from pdf_generator import generate_pdf_for_streamlit
from templates.template_manager import get_available_templates
import tempfile
import os
# In app.py - update the import section
from database import init_db, get_db_connection, update_project_status, get_all_projects, get_project_by_number
from pdf_generator import generate_pdf_for_streamlit  # Use this instead of generate_wsm_pdf

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="WSM Management System",
    page_icon="🏭",
    layout="wide"
)

# Session state management
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_project' not in st.session_state:
    st.session_state.current_project = None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
              (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user is not None

def login_page():
    st.title("🏭 WSM Management System")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if verify_login(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        st.info("Default credentials: admin / admin123")

def generate_project_no():
    return f"WSM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

def wsm_form_page():
    st.title("📝 New WSM Project")
    st.markdown("---")
    
    if st.session_state.current_project:
        st.info(f"Currently editing: {st.session_state.current_project}")
        if st.button("Clear Current Project"):
            st.session_state.current_project = None
            st.rerun()
    
    with st.form("wsm_form", clear_on_submit=False):
        # Page 1: Basic Information
        st.header("📄 Page 1: Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            available_templates = get_available_templates()
            wsm_type = st.selectbox("WSM Type*", list(available_templates.keys()), 
                                   format_func=lambda x: available_templates[x])
            revision = st.text_input("Revision*", placeholder="1.0")
            client = st.text_input("Client*", placeholder="Enter client name")
            consultant = st.text_input("Consultant", placeholder="Consultant name")
            branch_engineer = st.text_input("Branch Engineer", placeholder="Engineer name")
            division_engineer = st.text_input("Division Engineer", placeholder="Engineer name")
            
        with col2:
            site = st.text_input("Site*", placeholder="Site location")
            altitude = st.text_input("Altitude from MSL", placeholder="e.g., 100m")
            temp_min_max = st.text_input("Temp Min / Max", placeholder="e.g., 10°C / 35°C")
            power_voltage = st.text_input("Power Voltage", placeholder="415V")
            control_voltage = st.text_input("Control Voltage", placeholder="230V")
            frequency = st.text_input("Frequency", placeholder="50Hz")
        
        col1, col2 = st.columns(2)
        with col1:
            customer_po = st.text_input("Customer PO #", placeholder="PO number")
            po_date = st.date_input("PO Date")
            delivery_date = st.date_input("Delivery Date")
            special_delivery = st.selectbox("Special Delivery", ["No", "Yes"])
            
        with col2:
            ld_delivery_time = st.text_input("LD - Delivery time", placeholder="Delivery terms")
            ld_performance = st.text_input("LD - Performance", placeholder="Performance terms")
            supply_payment_terms = st.text_area("Supply Payment Terms", placeholder="Payment terms for supply")
            service_payment_terms = st.text_area("Service Payment Terms", placeholder="Payment terms for service")
        
        col1, col2 = st.columns(2)
        with col1:
            direct_orders = st.selectbox("Direct orders (Yes/No)", ["No", "Yes"])
            fm_role = st.text_input("FM Role", placeholder="FM role description")
            
        with col2:
            inspection = st.text_input("Inspection", placeholder="Inspection requirements")
            price_basis = st.selectbox("Price Basis", ["Ex works", "FOR", "CIF", "FOB"])
            commission = st.text_input("Commission - If any", placeholder="Commission details")

        # Page 2: Supply/Services - Boiler
        st.header("🔥 Page 2: Boiler Details")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Boiler Specifications")
            boiler_capacity = st.text_input("Boiler Capacity (F&A100 Deg C)*", placeholder="e.g., 1000 kg/hr")
            design_pressure = st.text_input("Design Pressure*", placeholder="e.g., 10.54 kg/cm²")
            boiler_quantity = st.text_input("Quantity*", placeholder="e.g., 1")
            boiler_fuel = st.selectbox("Fuel*", ["Natural Gas", "Diesel", "Fuel Oil", "LPG", "Biogas", "Coal"])
            boiler_type = st.selectbox("Boiler Type*", 
                ["Modular", "Non-Modular", "Combination M", "Floating Furnace", "Marshall BE", "Modular Marshall BE"])
            boiler_configuration = st.text_input("Boiler configuration", placeholder="e.g., 1 Working & 1 Stand by")
            
        with col2:
            st.subheader("Boiler Components")
            non_standard_requirement = st.text_area("Any non-standard requirement", placeholder="Special specifications or makes")
            pumps = st.text_input("Pumps", placeholder="Pump specifications")
            motors = st.text_input("Motors", placeholder="Motor specifications")
            valves = st.text_input("Valves", placeholder="Valve specifications")
            flanges = st.text_input("Flanges", placeholder="Flange specifications")
        
        st.subheader("Insulation & Cladding")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            insulation_cladding = st.selectbox("Insulation & Cladding", ["Yes", "No"])
        with col2:
            insulation_density = st.text_input("Insulation Density", placeholder="e.g., 128 kg/m³")
        with col3:
            insulation_thickness = st.text_input("Insulation thickness", placeholder="e.g., 75 mm")
        with col4:
            cladding_material = st.selectbox("Cladding Material", ["SS", "Aluminum", "GI"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            orientation = st.selectbox("Orientation", ["Std.", "Mirror"])
        with col2:
            boiler_design = st.selectbox("Boiler Design", ["IBR", "BS", "EN"])
        with col3:
            specific_design_approvals = st.text_input("Specific Design Approvals", placeholder="e.g., DOSH")
        
        emissions = st.selectbox("Emissions", ["Std.", "Non-Std."])
        boiler_other_requirements = st.text_area("Other Requirement/Special Instructions", placeholder="Additional boiler requirements")

        # Water Level Control
        st.header("💧 Water Level Control")
        col1, col2 = st.columns(2)
        with col1:
            wlc_type = st.selectbox("WLC type", ["Single", "Two element control", "Three element control"])
        with col2:
            water_level_control_type = st.selectbox("Type of water level control", 
                ["Std. WLC type", "VFD based", "Control valve"])
        wlc_other_requirements = st.text_area("Other Requirement/Special Instructions - WLC", placeholder="WLC special requirements")

        # Burner Details
        st.header("🔥 Burner Details")
        col1, col2 = st.columns(2)
        
        with col1:
            burner_type = st.text_input("Burner Type", placeholder="e.g., Rotary Cup, Pressure Jet")
            burner_make = st.text_input("Burner Make", placeholder="Manufacturer name")
            burner_model = st.text_input("Burner Model", placeholder="Model number")
            burner_quantity = st.text_input("Burner Quantity", placeholder="e.g., 1")
            
        with col2:
            burner_modulation = st.selectbox("Modulation", 
                ["On-Off", "High Low", "3 Stage", "Stepless"])
            fm_burner_regulation = st.selectbox("FM burner Regulation", 
                ["ECR-M", "ECR-P", "ECR-A", "MCR"])
            primary_fuel = st.selectbox("Primary Fuel", ["Natural Gas", "Diesel", "Fuel Oil", "LPG"])
            secondary_fuel = st.selectbox("Secondary fuel", ["None", "Natural Gas", "Diesel", "Fuel Oil", "LPG"])

        col1, col2 = st.columns(2)
        with col1:
            burner_bloc_type = st.selectbox("Type (Monobloc/Dual Bloc)", ["Monobloc", "Dual Bloc"])
            burner_fan = st.selectbox("Fan (Burner Mfg./Local)", ["Burner Mfg.", "Local"])
            lp_gas_train = st.selectbox("LP Gas train", ["Yes", "No"])
            
        with col2:
            o2_trimming = st.selectbox("O2 trimming (Yes/No)", ["No", "Yes"])
            vfd_details = st.selectbox("VFD (Yes/No)", ["No", "Yes"])
            special_makes = st.text_input("Mention Special Makes, if any", placeholder="Special manufacturer requirements")
        
        burner_other_requirements = st.text_area("Other Requirement/Special Instructions - Burner", placeholder="Burner special requirements")

        # Combustion Blower
        st.header("💨 Combustion Blower")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            combustion_blower_flow = st.text_input("Flow", placeholder="e.g., 1000 m³/hr")
        with col2:
            combustion_blower_head = st.text_input("Head", placeholder="e.g., 100 mmWC")
        with col3:
            vfd_suitable_motors = st.selectbox("Motors suitable for VFD", ["No", "Yes"])
        with col4:
            silencer = st.selectbox("Silencer", ["No", "Yes"])
        
        noise_level = st.selectbox("Noise level", ["Std.", "Non-Std."])
        combustion_blower_other_requirements = st.text_area("Other Requirement/Special Instructions - Combustion Blower", placeholder="Blower special requirements")

        # Control Panel
        st.header("⚡ Control Panel")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            control_panel_type = st.selectbox("Panel Type", ["Boiler mounted", "Floor Standing"])
        with col2:
            panel_configuration = st.selectbox("Panel Configuration", ["STD", "Compartmentalized"])
        with col3:
            plc = st.selectbox("PLC", ["No", "Yes"])
        with col4:
            plc_make = st.text_input("PLC Make", placeholder="e.g., Siemens, Allen Bradley")
        
        ip_rating = st.selectbox("IP Rating", ["IP54", "IP55", "IP65", "IP66"])
        control_panel_other_requirements = st.text_area("Other Requirement/Special Instructions - Control Panel", placeholder="Control panel special requirements")

        # Boiler Site Electricals
        st.header("🔌 Boiler Site Electricals")
        col1, col2 = st.columns(2)
        with col1:
            cabling_supply = st.selectbox("Cabling supply", ["FM Factory", "Drop shipment", "Not in scope"])
        with col2:
            cable_trays = st.selectbox("Cable trays", ["FM Factory", "Drop shipment", "Not in scope"])
        electricals_other_requirements = st.text_area("Other Requirement/Special Instructions - Electricals", placeholder="Electrical special requirements")

        # Page 4: Additional Systems
        st.header("🛠️ Page 4: Additional Systems")
        
        # Chemical Dosing System
        st.subheader("🧪 Chemical Dosing System")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            chemical_dosing_qty = st.text_input("Qty.", placeholder="e.g., 1")
        with col2:
            chemical_dosing_tank_capacity = st.text_input("Tank (Capacity)", placeholder="e.g., 100 L")
        with col3:
            dosing_pumps = st.selectbox("Dosing Pumps", ["1No", "2No"])
        with col4:
            chemical_dosing_control_type = st.selectbox("Type of control", ["Manual", "Auto"])
        chemical_dosing_other_requirements = st.text_area("Other Requirement/Special Instructions - Chemical Dosing", placeholder="Chemical dosing special requirements")

        # Ring Main system
        st.subheader("🔄 Ring Main system")
        ring_main_pump_qty = st.selectbox("Qty. of pumps", ["1W", "1W+1S"])
        ring_main_other_requirements = st.text_area("Other Requirement/Special Instructions - Ring Main", placeholder="Ring main special requirements")

        # Oil pumping & heating Station
        st.subheader("🛢️ Oil pumping & heating Station/Oil pumping station - OPS/OPH")
        utility_prs_prv = st.selectbox("Utility PRS/PRV for Steam", ["No", "Yes"])
        oil_station_other_requirements = st.text_area("Other Requirement/Special Instructions - Oil Station", placeholder="Oil station special requirements")

        # H.P. Gas Train
        st.subheader("🔥 H.P. Gas Train")
        col1, col2, col3 = st.columns(3)
        with col1:
            hp_gas_train_make = st.text_input("Make", placeholder="Manufacturer")
        with col2:
            gas_type = st.selectbox("Type of Gas", ["NG", "PNG", "Biogas"])
        with col3:
            ng_inlet_pressure = st.text_input("NG Inlet Pressure", placeholder="e.g., 200 mbar")
        hp_gas_train_other_requirements = st.text_area("Other Requirement/Special Instructions - HP Gas Train", placeholder="Gas train special requirements")

        # Heat recovery Unit
        st.subheader("♨️ Heat recovery Unit")
        col1, col2 = st.columns(2)
        with col1:
            heat_recovery_type = st.selectbox("Type", 
                ["Natural Circulation WPH", "Forced Circulation WPH", "Pressurized Economizer"])
            heat_recovery_integration = st.selectbox("Integral/Non-Integral/Integrated", 
                ["Integral", "Non-Integral", "Integrated (mounted on Boiler)"])
            heat_recovery_design_fuel = st.selectbox("Design fuel", 
                ["FQ", "NG", "hSD", "LPG"])
            heat_recovery_material_type = st.selectbox("Type (MS Finned/CI Gilled)", 
                ["MS Finned", "CI Gilled"])
            
        with col2:
            heat_recovery_quantity = st.text_input("Quantity", placeholder="e.g., 1")
            design_inlet_feed_water_temp = st.text_input("Design Inlet Feed Water Temperature", placeholder="e.g., 85°C")
            design_outlet_feed_water_temp = st.text_input("Design outlet Feed water Temperature", placeholder="e.g., 105°C")
            flue_gas_inlet_temp = st.text_input("Flue gas inlet temperature", placeholder="e.g., 250°C")
        
        flue_gas_outlet_temp = st.text_input("Flue Gas Outlet Temperature", placeholder="e.g., 150°C")
        heat_recovery_insulation = st.selectbox("Insulation & Cladding", ["Yes", "No"])
        motorized_dampers = st.selectbox("Motorized Dampers", ["Yes", "No"])
        water_side_control_valve = st.selectbox("Control valve on Water side", ["Yes", "No"])

        # Page 5: Continued Systems
        st.header("📋 Page 5: Continued Systems")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            manual_dampers = st.selectbox("Manual Dampers", ["Yes", "No"])
        with col2:
            soot_blowers = st.selectbox("Soot Blowers", 
                ["Motorized Steam type", "Sonic", "Not Required"])
        with col3:
            wph_makeup_pump = st.selectbox("WPH Makeup pump", ["No", "Yes"])
        
        heat_recovery_other_requirements = st.text_area("Other Requirement/Special Instructions - Heat Recovery", placeholder="Heat recovery special requirements")

        # Pressurized Deaerator/Pressurized Tank
        st.subheader("💧 Pressurized Deaerator/Pressurized Tank")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            deaerator_type = st.selectbox("Type", ["Pressurized Deaerator", "Pressurized Tank"])
        with col2:
            deaerator_quantity = st.text_input("Quantity", placeholder="e.g., 1")
        with col3:
            deaeration_capacity = st.text_input("Deaeration capacity", placeholder="e.g., 1000 kg/hr")
        with col4:
            storage_capacity = st.text_input("Storage capacity", placeholder="e.g., 5000 L")
        
        deaerator_insulation = st.selectbox("Insulation & Cladding", ["Yes", "No"])
        deaerator_other_requirements = st.text_area("Other Requirement/Special Instructions - Deaerator", placeholder="Deaerator special requirements")

        # Site Specific Requirements
        st.subheader("🏗️ Site Specific Requirements")
        col1, col2 = st.columns(2)
        with col1:
            safety_officer = st.text_input("Safety officer", placeholder="Officer name")
            site_supervisor = st.text_input("Site supervisor", placeholder="Supervisor name")
            construction_water = st.selectbox("Construction water", ["Available", "Not Available"])
            construction_power = st.selectbox("Construction Power", ["Available", "Not Available"])
            
        with col2:
            safety_requirements = st.text_area("Safety specific requirements", placeholder="Safety requirements")
            ehs_policy = st.selectbox("EHS Policy", ["No", "Yes"])
            drinking_water = st.selectbox("Drinking Water", ["Available", "Not Available"])
        
        site_other_requirements = st.text_area("Other Requirement/Special Instructions - Site", placeholder="Site special requirements")

        # Services
        st.subheader("🔧 Services")
        col1, col2 = st.columns(2)
        with col1:
            drawing_approval = st.selectbox("P&ID, BHL, GA Approval/Submission", ["No", "Yes"])
            control_panel_drawing_approval = st.selectbox("Control Panel Drawing Approval", ["No", "Yes"])
            special_documentation = st.text_input("Special Documentation, If any", placeholder="Documentation requirements")
            ibr_approval = st.selectbox("IBR Approval", ["PFO", "Steam Test", "only Folder"])
            
        with col2:
            site_services = st.selectbox("Site Services", ["Included", "Not Included"])
            unloading_leading = st.selectbox("Unloading & Leading", ["Included", "Not Included"])
            erection_commissioning = st.selectbox("Erection & Commissioning", ["Included", "Not Included"])
        
        # Page 6: Continued Services
        st.header("📋 Page 6: Continued Services")
        supervision = st.selectbox("Supervision", ["Included", "Not Included"])
        services_other_requirements = st.text_area("Other Requirement/Special Instructions - Services", placeholder="Services special requirements")

        # Page 7: Exclusions & Battery Limits
        st.header("🚫 Page 7: Exclusions & Battery Limits")
        st.info("""
        **Standard Exclusions (unless otherwise specified):**
        - All Civil and Structural work for Boiler installation
        - Feed Water Bulk Storage, Feed Water Transfer Pumps & Water treatment plant
        - Supporting Structural for items not in our scope
        - Boiler House Electricals for Balance of Plant Items
        - Fuel, water instrumentation and accessories required for performance testing
        - Steam, water, and fuel piping beyond terminal points
        - Any specific item not indicated in our scope of supply
        """)

        st.subheader("Battery Limits")
        col1, col2 = st.columns(2)
        with col1:
            battery_limits_boiler_feed_water = st.text_input("Boiler Feed Water", placeholder="Terminal point details")
            battery_limits_steam = st.text_input("Steam", placeholder="Terminal point details")
            battery_limits_fuel = st.text_input("Fuel FO / HSD", placeholder="Terminal point details")
            battery_limits_blow_down = st.text_input("Blow-down", placeholder="Terminal point details")
            
        with col2:
            battery_limits_safety_valve_exhaust = st.text_input("Safety Valve Exhaust", placeholder="Terminal point details")
            battery_limits_instrument_air = st.text_input("Instrument Air", placeholder="Terminal point details")
            battery_limits_power = st.text_input("Power", placeholder="Terminal point details")

        # Page 8: Documentation & Guarantees
        st.header("📄 Page 8: Documentation & Guarantees")
        
        st.subheader("DOCUMENTATION")
        col1, col2 = st.columns(2)
        with col1:
            ga_drawing = st.selectbox("General Arrangement Drawing (GA)", ["No", "Yes"])
            p_id_drawing = st.selectbox("Piping and Instrumentation Drawing (P & ID)", ["No", "Yes"])
            bhl_drawing = st.selectbox("Boiler House Layout (BHL)", ["No", "Yes"])
            piping_drawing = st.selectbox("Piping Drawing", ["No", "Yes"])
            qualification_documents = st.selectbox("Qualification Documents", ["No", "Yes"])
            
        with col2:
            chimney_drawing = st.selectbox("Chimney drawing", ["No", "Yes"])
            chimney_drawing_type = st.selectbox("Chimney drawing (Schematic/ Fabrication)", ["Schematic", "Fabrication"])
            feed_water_tank_drawing = st.selectbox("Feed water Tank drawing", ["No", "Yes"])
            feed_water_tank_capacity = st.text_input("Feed water Tank capacity", placeholder="e.g., 10000 L")
            day_oil_tank_drawing = st.selectbox("Day Oil Tank drawing", ["No", "Yes"])
        
        day_oil_tank_capacity = st.text_input("Day Oil Tank capacity", placeholder="e.g., 1000 L")
        documentation_other_requirements = st.text_area("Other Requirement/Special Instructions - Documentation", placeholder="Documentation special requirements")

        st.subheader("GUARANTEES")
        col1, col2 = st.columns(2)
        with col1:
            fuel_consumption_guarantee = st.selectbox("Fuel Consumption", ["No", "Yes"])
        with col2:
            efficiency_ncv_guarantee = st.selectbox("Efficiency on NCV Basis", ["No", "Yes"])
        guarantees_other_requirements = st.text_area("Other Requirement/Special Instructions - Guarantees", placeholder="Guarantee details")

        st.subheader("DOCUMENTS ENCLOSED")
        col1, col2, col3 = st.columns(3)
        with col1:
            customer_loi = st.selectbox("Customer LOI", ["No", "Yes"])
        with col2:
            customer_purchase_order = st.selectbox("Customer Purchase Order", ["No", "Yes"])
        with col3:
            customer_layout = st.selectbox("Customer's Layout", ["No", "Yes"])
        other_documents = st.text_area("Any other documents", placeholder="List any other documents")

        # Final Signature
        st.header("✍️ Final Approval")
        col1, col2 = st.columns(2)
        with col1:
            signature = st.text_input("Sign", value="LVK", placeholder="Authorized signature")
        with col2:
            signature_date = st.date_input("Date", value=datetime.now())

        submitted = st.form_submit_button("🚀 Submit WSM Project")
        
        if submitted:
            # Validate required fields
            required_fields = {
                "WSM Type": wsm_type,
                "Revision": revision,
                "Client": client,
                "Site": site,
                "Boiler Capacity": boiler_capacity,
                "Design Pressure": design_pressure,
                "Boiler Quantity": boiler_quantity,
                "Boiler Fuel": boiler_fuel,
                "Boiler Type": boiler_type
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            
            if missing_fields:
                st.error(f"❌ Please fill in the following required fields: {', '.join(missing_fields)}")
            else:
                project_no = generate_project_no()
                conn = get_db_connection()
                c = conn.cursor()
                
                try:
                    # Prepare all data for insertion
                    project_data = (
                        project_no, st.session_state.username, 'Submitted',
                        wsm_type, revision, client, consultant, branch_engineer, division_engineer,
                        site, altitude, temp_min_max, power_voltage, control_voltage, frequency,
                        customer_po, po_date.isoformat() if po_date else None, 
                        delivery_date.isoformat() if delivery_date else None, special_delivery, ld_delivery_time,
                        ld_performance, supply_payment_terms, service_payment_terms, direct_orders,
                        fm_role, inspection, price_basis, commission,
                        boiler_capacity, design_pressure, boiler_quantity, boiler_fuel, boiler_type,
                        boiler_configuration, non_standard_requirement, pumps, motors, valves, flanges,
                        insulation_cladding, insulation_density, insulation_thickness, cladding_material,
                        orientation, boiler_design, specific_design_approvals, emissions, boiler_other_requirements,
                        wlc_type, water_level_control_type, wlc_other_requirements,
                        burner_type, burner_make, burner_model, burner_quantity, burner_modulation, fm_burner_regulation,
                        primary_fuel, secondary_fuel, burner_bloc_type, burner_fan, lp_gas_train, o2_trimming,
                        vfd_details, burner_other_requirements, special_makes,
                        combustion_blower_flow, combustion_blower_head, vfd_suitable_motors, silencer, noise_level,
                        combustion_blower_other_requirements, control_panel_type, panel_configuration, plc, plc_make,
                        ip_rating, control_panel_other_requirements, cabling_supply, cable_trays, electricals_other_requirements,
                        chemical_dosing_qty, chemical_dosing_tank_capacity, dosing_pumps, chemical_dosing_control_type, chemical_dosing_other_requirements,
                        ring_main_pump_qty, ring_main_other_requirements, utility_prs_prv, oil_station_other_requirements,
                        hp_gas_train_make, gas_type, ng_inlet_pressure, hp_gas_train_other_requirements,
                        heat_recovery_type, heat_recovery_integration, heat_recovery_design_fuel, heat_recovery_material_type, heat_recovery_quantity,
                        design_inlet_feed_water_temp, design_outlet_feed_water_temp, flue_gas_inlet_temp, flue_gas_outlet_temp,
                        heat_recovery_insulation, motorized_dampers, water_side_control_valve, manual_dampers, soot_blowers,
                        wph_makeup_pump, heat_recovery_other_requirements, deaerator_type, deaerator_quantity, deaeration_capacity,
                        storage_capacity, deaerator_insulation, deaerator_other_requirements, safety_officer, site_supervisor,
                        construction_water, construction_power, safety_requirements, ehs_policy, drinking_water, site_other_requirements,
                        drawing_approval, control_panel_drawing_approval, special_documentation, ibr_approval, site_services,
                        unloading_leading, erection_commissioning, supervision, services_other_requirements,
                        battery_limits_boiler_feed_water, battery_limits_steam, battery_limits_fuel, battery_limits_blow_down,
                        battery_limits_safety_valve_exhaust, battery_limits_instrument_air, battery_limits_power,
                        ga_drawing, p_id_drawing, bhl_drawing, piping_drawing, qualification_documents, chimney_drawing,
                        chimney_drawing_type, feed_water_tank_drawing, feed_water_tank_capacity, day_oil_tank_drawing,
                        day_oil_tank_capacity, documentation_other_requirements, fuel_consumption_guarantee, efficiency_ncv_guarantee,
                        guarantees_other_requirements, customer_loi, customer_purchase_order, customer_layout, other_documents,
                        signature, signature_date.isoformat() if signature_date else None, wsm_type
                    )
                    
                    # Execute the insert with all fields
                    c.execute('''
                        INSERT INTO projects (
                            project_no, created_by, status,
                            wsm_type, revision, client, consultant, branch_engineer, division_engineer,
                            site, altitude, temp_min_max, power_voltage, control_voltage, frequency,
                            customer_po, po_date, delivery_date, special_delivery, ld_delivery_time,
                            ld_performance, supply_payment_terms, service_payment_terms, direct_orders,
                            fm_role, inspection, price_basis, commission,
                            boiler_capacity, design_pressure, boiler_quantity, boiler_fuel, boiler_type,
                            boiler_configuration, non_standard_requirement, pumps, motors, valves, flanges,
                            insulation_cladding, insulation_density, insulation_thickness, cladding_material,
                            orientation, boiler_design, specific_design_approvals, emissions, boiler_other_requirements,
                            wlc_type, water_level_control_type, wlc_other_requirements,
                            burner_type, burner_make, burner_model, burner_quantity, burner_modulation, fm_burner_regulation,
                            primary_fuel, secondary_fuel, burner_bloc_type, burner_fan, lp_gas_train, o2_trimming,
                            vfd_details, burner_other_requirements, special_makes,
                            combustion_blower_flow, combustion_blower_head, vfd_suitable_motors, silencer, noise_level,
                            combustion_blower_other_requirements, control_panel_type, panel_configuration, plc, plc_make,
                            ip_rating, control_panel_other_requirements, cabling_supply, cable_trays, electricals_other_requirements,
                            chemical_dosing_qty, chemical_dosing_tank_capacity, dosing_pumps, chemical_dosing_control_type, chemical_dosing_other_requirements,
                            ring_main_pump_qty, ring_main_other_requirements, utility_prs_prv, oil_station_other_requirements,
                            hp_gas_train_make, gas_type, ng_inlet_pressure, hp_gas_train_other_requirements,
                            heat_recovery_type, heat_recovery_integration, heat_recovery_design_fuel, heat_recovery_material_type, heat_recovery_quantity,
                            design_inlet_feed_water_temp, design_outlet_feed_water_temp, flue_gas_inlet_temp, flue_gas_outlet_temp,
                            heat_recovery_insulation, motorized_dampers, water_side_control_valve, manual_dampers, soot_blowers,
                            wph_makeup_pump, heat_recovery_other_requirements, deaerator_type, deaerator_quantity, deaeration_capacity,
                            storage_capacity, deaerator_insulation, deaerator_other_requirements, safety_officer, site_supervisor,
                            construction_water, construction_power, safety_requirements, ehs_policy, drinking_water, site_other_requirements,
                            drawing_approval, control_panel_drawing_approval, special_documentation, ibr_approval, site_services,
                            unloading_leading, erection_commissioning, supervision, services_other_requirements,
                            battery_limits_boiler_feed_water, battery_limits_steam, battery_limits_fuel, battery_limits_blow_down,
                            battery_limits_safety_valve_exhaust, battery_limits_instrument_air, battery_limits_power,
                            ga_drawing, p_id_drawing, bhl_drawing, piping_drawing, qualification_documents, chimney_drawing,
                            chimney_drawing_type, feed_water_tank_drawing, feed_water_tank_capacity, day_oil_tank_drawing,
                            day_oil_tank_capacity, documentation_other_requirements, fuel_consumption_guarantee, efficiency_ncv_guarantee,
                            guarantees_other_requirements, customer_loi, customer_purchase_order, customer_layout, other_documents,
                            signature, signature_date, template_type
                        ) VALUES (''' + ','.join(['?'] * len(project_data)) + ')', project_data)
                    
                    conn.commit()
                    st.success(f"✅ Project submitted successfully!")
                    st.info(f"**Project Number:** {project_no}")
                    st.session_state.current_project = project_no
                    
                    # Show next steps
                    st.balloons()
                    st.markdown("""
                    ### Next Steps:
                    1. Go to **Project Status** page to track your project
                    2. Download the PDF report once approved
                    3. Monitor project status updates
                    """)
                    
                except Exception as e:
                    st.error(f"❌ Error submitting project: {str(e)}")
                    import traceback
                    st.error(f"Detailed error: {traceback.format_exc()}")
                finally:
                    conn.close()

def status_page():
    st.title("📊 Project Status")
    st.markdown("---")
    
    conn = get_db_connection()
    
    # Get all projects
    projects = get_all_projects()
    
    if not projects.empty:
        st.subheader("Project Overview")
        
        # Status summary
        status_counts = projects['status'].value_counts()
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Submitted", status_counts.get('Submitted', 0))
        with col2:
            st.metric("Approved", status_counts.get('Approved', 0))
        with col3:
            st.metric("Waiting for MRO", status_counts.get('Waiting for MRO Confirmation', 0))
        with col4:
            st.metric("Rejected", status_counts.get('Rejected', 0))
        with col5:
            st.metric("Total Projects", len(projects))
        
        # Search and filter
        st.subheader("Project Details")
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            search_term = st.text_input("🔍 Search projects...", placeholder="Search by project no, client, or site")
        with col2:
            status_filter = st.selectbox("Filter by status", ["All", "Submitted", "Approved", "Waiting for MRO Confirmation", "Rejected", "Completed"])
        with col3:
            st.write("")
            if st.button("🔄 Refresh Data"):
                st.rerun()
        
        # Filter projects
        filtered_projects = projects
        if search_term:
            filtered_projects = filtered_projects[
                filtered_projects['project_no'].str.contains(search_term, case=False) |
                filtered_projects['client'].str.contains(search_term, case=False) |
                filtered_projects['site'].str.contains(search_term, case=False)
            ]
        if status_filter != "All":
            filtered_projects = filtered_projects[filtered_projects['status'] == status_filter]
        
        if not filtered_projects.empty:
            for _, project in filtered_projects.iterrows():
                with st.expander(f"**{project['project_no']}** - {project['client']} | {project['site']} | Status: **{project['status']}**"):
                    col1, col2, col3, col4 = st.columns([2,2,1,1])
                    
                    with col1:
                        st.write(f"**Client:** {project['client']}")
                        st.write(f"**Site:** {project['site']}")
                        st.write(f"**Created by:** {project['created_by']}")
                        st.write(f"**Created on:** {project['created_at'][:16]}")
                    
                    with col2:
                        new_status = st.selectbox(
                            "Update Status",
                            ["Submitted", "Approved", "Waiting for MRO Confirmation", "Rejected", "Completed"],
                            key=f"status_{project['project_no']}",
                            index=["Submitted", "Approved", "Waiting for MRO Confirmation", "Rejected", "Completed"].index(project['status'])
                        )
                    
                    with col3:
                        if st.button("Update", key=f"update_{project['project_no']}"):
                            update_project_status(project['project_no'], new_status)
                            st.success("Status updated!")
                            st.rerun()
                    with col4:
                        try:
                            with st.spinner("Generating PDF..."):
                                pdf_data = generate_pdf_for_streamlit(project['project_no'])
        
                            st.download_button(
                                label="📄 Download PDF",
                                data=pdf_data,
                                file_name=f"{project['project_no']}.pdf",
                                mime="application/pdf",
                                key=f"download_{project['project_no']}",
                                use_container_width=True
                            )
        
                        except Exception as e:
                            st.error(f"PDF generation failed: {str(e)}")
                            
                            if st.button("Retry", key=f"retry_{project['project_no']}"):
                                st.rerun()
                    
        else:
            st.warning("No projects match your search criteria.")
        
    else:
        st.info("No projects found. Create a new project in the WSM Form page.")
    
    conn.close()

def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}!")
        st.sidebar.markdown("---")
        
        page = st.sidebar.radio("Navigation", 
                               ["🏠 Dashboard", "📝 WSM Form", "📊 Project Status", "🚪 Logout"])
        
        if page == "🏠 Dashboard":
            st.title("Dashboard")
            st.markdown("---")
            st.info("""
            ### WSM Management System
            
            **Features:**
            - Create new WSM projects with complete 8-page forms
            - Track project status with workflow management
            - Generate professional PDF reports
            - Support for multiple WSM templates
            - Search and filter projects
            
            **Available Templates:**
            """ + "\n".join([f"- {name}" for name in get_available_templates().values()]) + """
            
            Use the navigation menu to get started.
            """)
            
        elif page == "📝 WSM Form":
            wsm_form_page()
        elif page == "📊 Project Status":
            status_page()
        elif page == "🚪 Logout":
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.current_project = None
            st.success("Logged out successfully!")
            st.rerun()

if __name__ == "__main__":
    main()