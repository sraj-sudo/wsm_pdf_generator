# database.py
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd

def init_db():
    conn = sqlite3.connect('wsm_projects.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Projects table with all fields from the form
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_no TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'Submitted',
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Page 1: Basic Information
            wsm_type TEXT,
            revision TEXT,
            client TEXT,
            consultant TEXT,
            branch_engineer TEXT,
            division_engineer TEXT,
            site TEXT,
            altitude TEXT,
            temp_min_max TEXT,
            power_voltage TEXT,
            control_voltage TEXT,
            frequency TEXT,
            customer_po TEXT,
            po_date TEXT,
            delivery_date TEXT,
            special_delivery TEXT,
            ld_delivery_time TEXT,
            ld_performance TEXT,
            supply_payment_terms TEXT,
            service_payment_terms TEXT,
            direct_orders TEXT,
            fm_role TEXT,
            inspection TEXT,
            price_basis TEXT,
            commission TEXT,
            
            -- Page 2: Boiler Details
            boiler_capacity TEXT,
            design_pressure TEXT,
            boiler_quantity TEXT,
            boiler_fuel TEXT,
            boiler_type TEXT,
            boiler_configuration TEXT,
            non_standard_requirement TEXT,
            pumps TEXT,
            motors TEXT,
            valves TEXT,
            flanges TEXT,
            insulation_cladding TEXT,
            insulation_density TEXT,
            insulation_thickness TEXT,
            cladding_material TEXT,
            orientation TEXT,
            boiler_design TEXT,
            specific_design_approvals TEXT,
            emissions TEXT,
            boiler_other_requirements TEXT,
            wlc_type TEXT,
            water_level_control_type TEXT,
            wlc_other_requirements TEXT,
            burner_type TEXT,
            burner_make TEXT,
            burner_model TEXT,
            burner_quantity TEXT,
            burner_modulation TEXT,
            fm_burner_regulation TEXT,
            primary_fuel TEXT,
            secondary_fuel TEXT,
            burner_bloc_type TEXT,
            burner_fan TEXT,
            lp_gas_train TEXT,
            o2_trimming TEXT,
            vfd_details TEXT,
            burner_other_requirements TEXT,
            special_makes TEXT,
            
            -- Page 3: Combustion Blower & Control Panel
            combustion_blower_flow TEXT,
            combustion_blower_head TEXT,
            vfd_suitable_motors TEXT,
            silencer TEXT,
            noise_level TEXT,
            combustion_blower_other_requirements TEXT,
            control_panel_type TEXT,
            panel_configuration TEXT,
            plc TEXT,
            plc_make TEXT,
            ip_rating TEXT,
            control_panel_other_requirements TEXT,
            cabling_supply TEXT,
            cable_trays TEXT,
            electricals_other_requirements TEXT,
            
            -- Page 4: Additional Systems
            chemical_dosing_qty TEXT,
            chemical_dosing_tank_capacity TEXT,
            dosing_pumps TEXT,
            chemical_dosing_control_type TEXT,
            chemical_dosing_other_requirements TEXT,
            ring_main_pump_qty TEXT,
            ring_main_other_requirements TEXT,
            utility_prs_prv TEXT,
            oil_station_other_requirements TEXT,
            hp_gas_train_make TEXT,
            gas_type TEXT,
            ng_inlet_pressure TEXT,
            hp_gas_train_other_requirements TEXT,
            heat_recovery_type TEXT,
            heat_recovery_integration TEXT,
            heat_recovery_design_fuel TEXT,
            heat_recovery_material_type TEXT,
            heat_recovery_quantity TEXT,
            design_inlet_feed_water_temp TEXT,
            design_outlet_feed_water_temp TEXT,
            flue_gas_inlet_temp TEXT,
            flue_gas_outlet_temp TEXT,
            heat_recovery_insulation TEXT,
            motorized_dampers TEXT,
            water_side_control_valve TEXT,
            
            -- Page 5: Continued Systems
            manual_dampers TEXT,
            soot_blowers TEXT,
            wph_makeup_pump TEXT,
            heat_recovery_other_requirements TEXT,
            deaerator_type TEXT,
            deaerator_quantity TEXT,
            deaeration_capacity TEXT,
            storage_capacity TEXT,
            deaerator_insulation TEXT,
            deaerator_other_requirements TEXT,
            safety_officer TEXT,
            site_supervisor TEXT,
            construction_water TEXT,
            construction_power TEXT,
            safety_requirements TEXT,
            ehs_policy TEXT,
            drinking_water TEXT,
            site_other_requirements TEXT,
            drawing_approval TEXT,
            control_panel_drawing_approval TEXT,
            special_documentation TEXT,
            ibr_approval TEXT,
            site_services TEXT,
            unloading_leading TEXT,
            erection_commissioning TEXT,
            
            -- Page 6: Continued Services
            supervision TEXT,
            services_other_requirements TEXT,
            
            -- Page 7: Battery Limits
            battery_limits_boiler_feed_water TEXT,
            battery_limits_steam TEXT,
            battery_limits_fuel TEXT,
            battery_limits_blow_down TEXT,
            battery_limits_safety_valve_exhaust TEXT,
            battery_limits_instrument_air TEXT,
            battery_limits_power TEXT,
            
            -- Page 8: Documentation & Guarantees
            ga_drawing TEXT,
            p_id_drawing TEXT,
            bhl_drawing TEXT,
            piping_drawing TEXT,
            qualification_documents TEXT,
            chimney_drawing TEXT,
            chimney_drawing_type TEXT,
            feed_water_tank_drawing TEXT,
            feed_water_tank_capacity TEXT,
            day_oil_tank_drawing TEXT,
            day_oil_tank_capacity TEXT,
            documentation_other_requirements TEXT,
            fuel_consumption_guarantee TEXT,
            efficiency_ncv_guarantee TEXT,
            guarantees_other_requirements TEXT,
            customer_loi TEXT,
            customer_purchase_order TEXT,
            customer_layout TEXT,
            other_documents TEXT,
            signature TEXT,
            signature_date TEXT,
            template_type TEXT DEFAULT 'STD_WSM'
        )
    ''')
    
    # Insert default user
    try:
        hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                 ('admin', hashed_password, 'admin@company.com'))
    except sqlite3.IntegrityError:
        pass  # User already exists
    
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect('wsm_projects.db')

def get_project_by_number(project_no):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM projects WHERE project_no = ?', (project_no,))
    project = c.fetchone()
    conn.close()
    return project

def get_all_projects():
    conn = get_db_connection()
    projects = pd.read_sql('SELECT project_no, status, created_by, created_at, client, site FROM projects ORDER BY created_at DESC', conn)
    conn.close()
    return projects

def update_project_status(project_no, status):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE projects SET status = ?, updated_at = ? WHERE project_no = ?',
             (status, datetime.now().isoformat(), project_no))
    conn.commit()
    conn.close()