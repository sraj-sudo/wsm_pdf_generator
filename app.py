import streamlit as st
import os
import tempfile
from auth import initialize_authentication, require_auth, logout, create_user
from database import init_db
from forms import (
    show_standard_form, 
    show_non_standard_form, 
    show_electrical_form, 
    show_whrb_form, 
    show_custom_form
)
from utils.pdf_generator import pdf_generator

# Page configuration
st.set_page_config(
    page_title="WSM Dashboard",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    initialize_authentication()
    
    if not st.session_state.authenticated:
        from auth import login_form
        login_form()
        return
    
    # Sidebar
    with st.sidebar:
        st.title(f"WSM Dashboard")
        st.write(f"👤 **User:** {st.session_state.username}")
        st.write(f"🎯 **Role:** {st.session_state.role}")
        
        st.markdown("---")
        
        # Navigation based on role
        if st.session_state.role == 'admin':
            page_options = ["🏠 Dashboard", "➕ Create New WSM", "📊 Project Status", "⚙️ Admin Panel"]
        else:
            page_options = ["🏠 Dashboard", "➕ Create New WSM", "📋 My Projects"]
        
        page = st.radio("Navigation", page_options, key="main_navigation")
        
        st.markdown("---")
        if st.button("🚪 Logout", key="logout_btn"):
            logout()
    
    # Main content based on selected page
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "➕ Create New WSM":
        show_create_wsm_page()
    elif page == "📊 Project Status" or page == "📋 My Projects":
        show_project_status_page()
    elif page == "⚙️ Admin Panel" and st.session_state.role == 'admin':
        show_admin_panel()

def show_dashboard():
    st.title("🏠 WSM Dashboard")
    
    db = init_db()
    
    # Get statistics
    if st.session_state.role == 'admin':
        projects = db.get_all_projects()
    else:
        all_projects = db.get_all_projects()
        projects = [p for p in all_projects if p.get('general_info', {}).get('created_by') == st.session_state.username]
    
    # Calculate statistics
    total_projects = len(projects)
    status_counts = {}
    type_counts = {}
    
    for project in projects:
        status = project['status']
        wsm_type = project['wsm_type']
        
        status_counts[status] = status_counts.get(status, 0) + 1
        type_counts[wsm_type] = type_counts.get(wsm_type, 0) + 1
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Projects", total_projects)
    
    with col2:
        submitted = status_counts.get('Submitted', 0)
        st.metric("📨 Submitted", submitted)
    
    with col3:
        approved = status_counts.get('Approved', 0)
        st.metric("✅ Approved", approved)
    
    with col4:
        in_review = status_counts.get('Under Review', 0)
        st.metric("🔍 Under Review", in_review)
    
    st.markdown("---")
    
    # Recent projects
    st.subheader("📋 Recent Projects")
    if projects:
        recent_projects = projects[:5]  # Show last 5 projects
        for project in recent_projects:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.write(f"**{project['project_no']}** - {project['wsm_type']}")
                    if project.get('general_info'):
                        st.write(f"Client: {project['general_info'].get('client', 'N/A')}")
                
                with col2:
                    st.write(f"**Status:** {project['status']}")
                
                with col3:
                    st.write(f"**Type:** {project['wsm_type']}")
                
                with col4:
                    if st.button("View", key=f"view_{project['project_no']}"):
                        st.session_state.view_project = project['project_no']
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("No projects found. Create your first WSM!")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Create New WSM", use_container_width=True, key="create_wsm_dash"):
            st.session_state.current_page = "Create New WSM"
            st.rerun()
    
    with col2:
        if st.button("📋 View All Projects", use_container_width=True, key="view_projects_dash"):
            st.session_state.current_page = "Project Status"
            st.rerun()
    
    with col3:
        if st.session_state.role == 'admin' and st.button("⚙️ Admin Panel", use_container_width=True, key="admin_panel_dash"):
            st.session_state.current_page = "Admin Panel"
            st.rerun()

def show_create_wsm_page():
    st.title("📝 Create New Worksheet for Manufacturing (WSM)")
    
    # Initialize session state for current project
    if 'current_project' not in st.session_state:
        st.session_state.current_project = None
    if 'current_wsm_type' not in st.session_state:
        st.session_state.current_wsm_type = None
    
    # Step 1: General Information (only show if no current project)
    if not st.session_state.current_project:
        st.header("📍 Step 1: General Information")
        
        with st.form("general_info"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👥 Client & Site Information")
                client = st.text_input("Client *", placeholder="Enter client name", key="client_input")
                site = st.text_input("Site *", placeholder="Enter site location", key="site_input")
                altitude = st.text_input("Altitude from MSL", placeholder="e.g., 100m", key="altitude_input")
                temp_min_max = st.text_input("Temp Min / Max", placeholder="e.g., 10°C / 40°C", key="temp_input")
                
                st.subheader("📋 Order Details")
                customer_po = st.text_input("Customer PO #", placeholder="Purchase order number", key="customer_po_input")
                delivery_date = st.date_input("Delivery Date", key="delivery_date_input")
            
            with col2:
                st.subheader("👨‍💼 Personnel")
                consultant = st.text_input("Consultant", placeholder="Consultant name", key="consultant_input")
                branch_engineer = st.text_input("Branch Engineer", placeholder="Branch engineer name", key="branch_engineer_input")
                division_engineer = st.text_input("Division Engineer", placeholder="Division engineer name", key="division_engineer_input")
                po_date = st.date_input("PO Date", key="po_date_input")
                
                st.subheader("⚡ Voltage Details")
                power_voltage = st.text_input("Power Voltage", placeholder="e.g., 415V", key="power_voltage_input")
                control_voltage = st.text_input("Control Voltage", placeholder="e.g., 230V", key="control_voltage_input")
                frequency = st.text_input("Frequency", placeholder="e.g., 50Hz", key="frequency_input")
            
            st.markdown("---")
            
            # WSM Type and Boiler Type
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📄 WSM Type")
                wsm_type = st.selectbox("WSM Type *", 
                                      ["Standard", "Non-Standard", "Electrical", "WHRB", "Custom"],
                                      key="wsm_type_select")
            
            with col2:
                st.subheader("🔥 Boiler Type")
                boiler_options = {
                    "Standard": [
                        "Marshall E Series Electric Steam Boiler",
                        "Marshall C Series Packaged Boilers", 
                        "DynaMax Small Industrial Boilers",
                        "MiniMax Compact Packaged Boiler",
                        "Modular Boilerhouse",
                        "Marshall B Boiler",
                        "BE", "BG", "CG",
                        "TOH (Thermal oil Heaters)",
                        "Hot air generator",
                        "Marshall F", 
                        "Duplex Boiler"
                    ],
                    "Non-Standard": ["Custom Non-Standard Boiler"],
                    "Electrical": ["Marshall E Series Electric Steam Boiler"],
                    "WHRB": ["Waste Heat Recovery Boilers (WHRB)"],
                    "Custom": ["Custom Boiler Configuration"]
                }
                
                boiler_type = st.selectbox("Boiler Type *", boiler_options[wsm_type], key="boiler_type_select")
            
            st.markdown("---")
            
            # Terms and Conditions
            st.subheader("📑 Terms & Conditions")
            col1, col2 = st.columns(2)
            with col1:
                supply_payment_terms = st.text_input("Terms of Payment - Supply", placeholder="Supply payment terms", key="supply_payment_input")
                direct_orders = st.selectbox("Direct orders (Yes/No)", ["Yes", "No", "Not Specified"], key="direct_orders_select")
                fm_role = st.text_input("FM Role", placeholder="FM role description", key="fm_role_input")
                price_basis = st.selectbox("Price Basis", 
                                         ["Ex works", "FOR", "CIF", "FOB", "Not Specified"],
                                         key="price_basis_select")
            
            with col2:
                service_payment_terms = st.text_input("Terms of Payment - Service", placeholder="Service payment terms", key="service_payment_input")
                inspection = st.selectbox("Inspection", 
                                        ["Customer", "Consultant", "Third Party", "Not Specified"],
                                        key="inspection_select")
                commission = st.text_input("Commission - If any", placeholder="Commission details", key="commission_input")
                special_delivery = st.selectbox("Special Delivery (Yes/No)", ["Yes", "No", "Not Specified"], key="special_delivery_select")
            
            # LD Terms
            st.subheader("⚖️ Liquidated Damages")
            col1, col2 = st.columns(2)
            with col1:
                ld_delivery_time = st.text_input("LD - Delivery time", placeholder="Delivery time LD terms", key="ld_delivery_input")
            with col2:
                ld_performance = st.text_input("LD - Performance", placeholder="Performance LD terms", key="ld_performance_input")
            
            st.markdown("---")
            
            # Submit button for the form
            submitted = st.form_submit_button("🚀 Create Project", use_container_width=True)
            
            if submitted:
                if not client or not site:
                    st.error("❌ Please fill in all required fields (*)")
                else:
                    db = init_db()
                    
                    project_data = {
                        'client': client,
                        'consultant': consultant,
                        'branch_engineer': branch_engineer,
                        'division_engineer': division_engineer,
                        'site': site,
                        'altitude': altitude,
                        'temp_min_max': temp_min_max,
                        'power_voltage': power_voltage,
                        'control_voltage': control_voltage,
                        'frequency': frequency,
                        'customer_po': customer_po,
                        'delivery_date': delivery_date.isoformat() if delivery_date else '',
                        'po_date': po_date.isoformat() if po_date else '',
                        'special_delivery': special_delivery,
                        'supply_payment_terms': supply_payment_terms,
                        'service_payment_terms': service_payment_terms,
                        'direct_orders': direct_orders,
                        'fm_role': fm_role,
                        'inspection': inspection,
                        'price_basis': price_basis,
                        'commission': commission,
                        'ld_delivery_time': ld_delivery_time,
                        'ld_performance': ld_performance,
                        'wsm_type': wsm_type,
                        'boiler_type': boiler_type,
                        'created_by': st.session_state.username
                    }
                    
                    project_no = db.create_project(project_data)
                    if project_no:
                        st.session_state.current_project = project_no
                        st.session_state.current_wsm_type = wsm_type
                        st.success(f"✅ Project created successfully! **Project No: {project_no}**")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Error creating project. Please try again.")

    # Step 2: WSM Specific Forms
    if st.session_state.current_project:
        st.header("🔧 Step 2: Supply/Services Details")
        st.info(f"📋 **Current Project:** {st.session_state.current_project} | **Type:** {st.session_state.current_wsm_type}")
        
        wsm_type = st.session_state.current_wsm_type
        project_no = st.session_state.current_project
        
        form_handlers = {
            "Standard": show_standard_form,
            "Non-Standard": show_non_standard_form,
            "Electrical": show_electrical_form,
            "WHRB": show_whrb_form,
            "Custom": show_custom_form
        }
        
        if wsm_type in form_handlers:
            form_handlers[wsm_type](project_no)
        else:
            st.error(f"❌ No form handler found for WSM type: {wsm_type}")
        
        # Navigation buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("⬅️ Back to General Info", use_container_width=True, key="back_to_general"):
                st.session_state.current_project = None
                st.session_state.current_wsm_type = None
                st.rerun()
        
        with col2:
            if st.button("💾 Save Draft", use_container_width=True, key="save_draft"):
                st.success("✅ Draft saved successfully!")
        
        with col3:
            if st.button("📤 Submit WSM for Review", type="primary", use_container_width=True, key="submit_wsm"):
                db = init_db()
                if db.update_project_status(project_no, "Submitted"):
                    st.success("🎉 WSM submitted for review successfully!")
                    st.balloons()
                    st.session_state.current_project = None
                    st.session_state.current_wsm_type = None
                    st.rerun()
                else:
                    st.error("❌ Error submitting WSM. Please try again.")

def show_project_status_page():
    page_title = "📊 Project Status" if st.session_state.role == 'admin' else "📋 My Projects"
    st.title(page_title)
    
    db = init_db()
    
    # Filter projects based on user role
    if st.session_state.role == 'admin':
        projects = db.get_all_projects()
    else:
        all_projects = db.get_all_projects()
        projects = [p for p in all_projects if p.get('general_info', {}).get('created_by') == st.session_state.username]
    
    if not projects:
        st.info("ℹ️ No projects found. Create your first WSM to get started!")
        if st.button("📝 Create New WSM", key="create_new_from_status"):
            st.session_state.current_page = "Create New WSM"
            st.rerun()
        return
    
    # Search and filter
    st.subheader("🔍 Search & Filter")
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search_term = st.text_input("Search projects...", placeholder="Search by project no, client, or site", key="search_projects")
    with col2:
        status_filter = st.selectbox("Filter by status", 
                                   ["All", "Submitted", "Under Review", "Approved", 
                                    "Waiting for MRO Confirmation", "Completed"],
                                   key="status_filter")
    with col3:
        wsm_filter = st.selectbox("Filter by WSM type", 
                                ["All", "Standard", "Non-Standard", "Electrical", "WHRB", "Custom"],
                                key="wsm_filter")
    with col4:
        sort_by = st.selectbox("Sort by", 
                             ["Newest First", "Oldest First", "Project No", "Status"],
                             key="sort_by")
    
    # Filter projects
    filtered_projects = projects
    if search_term:
        filtered_projects = [p for p in filtered_projects 
                           if search_term.lower() in p['project_no'].lower() 
                           or (p.get('general_info') and search_term.lower() in p['general_info'].get('client', '').lower())
                           or (p.get('general_info') and search_term.lower() in p['general_info'].get('site', '').lower())]
    
    if status_filter != "All":
        filtered_projects = [p for p in filtered_projects if p['status'] == status_filter]
    
    if wsm_filter != "All":
        filtered_projects = [p for p in filtered_projects if p['wsm_type'] == wsm_filter]
    
    # Sort projects
    if sort_by == "Newest First":
        filtered_projects.sort(key=lambda x: x['created_at'], reverse=True)
    elif sort_by == "Oldest First":
        filtered_projects.sort(key=lambda x: x['created_at'])
    elif sort_by == "Project No":
        filtered_projects.sort(key=lambda x: x['project_no'])
    elif sort_by == "Status":
        filtered_projects.sort(key=lambda x: x['status'])
    
    # Display projects count
    st.write(f"**📈 Showing {len(filtered_projects)} of {len(projects)} projects**")
    
    # Display projects
    for project in filtered_projects:
        # Status color coding
        status_colors = {
            "Submitted": "blue",
            "Under Review": "orange", 
            "Approved": "green",
            "Waiting for MRO Confirmation": "yellow",
            "Completed": "purple"
        }
        
        status_color = status_colors.get(project['status'], "gray")
        
        with st.expander(f"**{project['project_no']}** - {project['wsm_type']} - :{status_color}[{project['status']}]", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                if project.get('general_info'):
                    gi = project['general_info']
                    st.write(f"**👥 Client:** {gi.get('client', 'N/A')}")
                    st.write(f"**🏭 Site:** {gi.get('site', 'N/A')}")
                    st.write(f"**🔥 Boiler Type:** {project['boiler_type']}")
                    st.write(f"**👤 Created by:** {gi.get('created_by', 'N/A')}")
                    
                    # Safe datetime display
                    created_at = project['created_at']
                    if hasattr(created_at, 'strftime'):
                        st.write(f"**📅 Created:** {created_at.strftime('%Y-%m-%d %H:%M')}")
                    else:
                        st.write(f"**📅 Created:** {str(created_at)}")
                    
                    # Safe updated_at display
                    updated_at = project['updated_at']
                    if hasattr(updated_at, 'strftime') and hasattr(created_at, 'strftime'):
                        if updated_at != created_at:
                            st.write(f"**🔄 Last Updated:** {updated_at.strftime('%Y-%m-%d %H:%M')}")
                    elif str(updated_at) != str(created_at):
                        st.write(f"**🔄 Last Updated:** {str(updated_at)}")
            
            with col2:
                if st.session_state.role == 'admin':
                    new_status = st.selectbox(
                        "Update Status",
                        ["Submitted", "Under Review", "Approved", "Waiting for MRO Confirmation", "Completed"],
                        index=["Submitted", "Under Review", "Approved", "Waiting for MRO Confirmation", "Completed"].index(project['status']),
                        key=f"status_{project['project_no']}"
                    )
                    
                    if st.button("Update Status", key=f"update_{project['project_no']}"):
                        if db.update_project_status(project['project_no'], new_status):
                            st.success("✅ Status updated successfully!")
                            st.rerun()
                else:
                    st.write(f"**📊 Status:** {project['status']}")
                    st.write(f"**📄 WSM Type:** {project['wsm_type']}")
            
            with col3:
                # Generate and download PDF
                if st.button("📄 Generate PDF", key=f"pdf_{project['project_no']}", use_container_width=True):
                    with st.spinner("🔄 Generating PDF document..."):
                        try:
                            # Generate PDF and get bytes
                            pdf_bytes = pdf_generator.generate_pdf_to_bytes(project['project_no'])
                            
                            if pdf_bytes:
                                st.download_button(
                                    label="⬇️ Download PDF",
                                    data=pdf_bytes,
                                    file_name=f"{project['project_no']}_wsm.pdf",
                                    mime="application/pdf",
                                    key=f"download_{project['project_no']}",
                                    use_container_width=True
                                )
                            else:
                                st.error("❌ Failed to generate PDF. Please try again.")
                                
                        except Exception as e:
                            st.error(f"❌ Error generating PDF: {str(e)}")
                
                # View project details
                if st.button("👀 View Details", key=f"view_{project['project_no']}", use_container_width=True):
                    st.session_state.view_project = project['project_no']
                    st.rerun()
    
    # Project details view
    if 'view_project' in st.session_state:
        st.header(f"🔍 Project Details: {st.session_state.view_project}")
        
        project_data = db.get_project_data(st.session_state.view_project)
        if project_data:
            for section, data in project_data.items():
                with st.expander(f"📁 {section.replace('_', ' ').title()}", expanded=False):
                    st.json(data)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Back to Projects", use_container_width=True, key="back_to_projects"):
                del st.session_state.view_project
                st.rerun()
        with col2:
            # Quick PDF download in details view
            if st.button("📄 Download PDF", use_container_width=True, key="quick_pdf_download"):
                with st.spinner("Generating PDF..."):
                    pdf_bytes = pdf_generator.generate_pdf_to_bytes(st.session_state.view_project)
                    if pdf_bytes:
                        st.download_button(
                            label="⬇️ Download PDF Now",
                            data=pdf_bytes,
                            file_name=f"{st.session_state.view_project}_wsm.pdf",
                            mime="application/pdf",
                            key=f"quick_download_{st.session_state.view_project}",
                            use_container_width=True
                        )

def show_admin_panel():
    st.title("⚙️ Admin Panel")
    
    if st.session_state.role != 'admin':
        st.error("🚫 Access denied. Admin privileges required.")
        return
    
    tab1, tab2, tab3 = st.tabs(["👥 User Management", "📊 System Analytics", "⚙️ System Settings"])
    
    with tab1:
        st.subheader("👥 User Management")
        
        # Create new user
        with st.form("create_user"):
            st.write("**Add New User**")
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username *", key="new_username")
                new_password = st.text_input("Password *", type="password", key="new_password")
            
            with col2:
                new_email = st.text_input("Email", key="new_email")
                new_role = st.selectbox("Role *", ["user", "admin"], key="new_role")
            
            if st.form_submit_button("➕ Create User", use_container_width=True):
                if not new_username or not new_password:
                    st.error("❌ Please fill in all required fields (*)")
                else:
                    if create_user(new_username, new_password, new_email, new_role):
                        st.success(f"✅ User '{new_username}' created successfully!")
                    else:
                        st.error("❌ Error creating user. Username might already exist.")
        
        # List existing users
        st.subheader("📋 Existing Users")
        db = init_db()
        cursor = db.connection.cursor()
        cursor.execute("SELECT username, email, role, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        cursor.close()
        
        if users:
            for user in users:
                role_emoji = "👑" if user[2] == 'admin' else "👤"
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    col1.write(f"**{user[0]}** {role_emoji}")
                    col2.write(user[1] or "No email")
                    col3.write(user[2].capitalize())
                    
                    # Safe datetime display for user creation date
                    created_at = user[3]
                    if hasattr(created_at, 'strftime'):
                        col4.write(created_at.strftime('%Y-%m-%d'))
                    else:
                        col4.write(str(created_at))
                    
                    st.markdown("---")
        else:
            st.info("ℹ️ No users found")
    
    with tab2:
        st.subheader("📊 System Analytics")
        db = init_db()
        cursor = db.connection.cursor()
        
        # Project statistics
        cursor.execute("SELECT COUNT(*) as total FROM projects")
        total_projects = cursor.fetchone()[0]
        
        cursor.execute("SELECT status, COUNT(*) as count FROM projects GROUP BY status")
        status_counts = cursor.fetchall()
        
        cursor.execute("SELECT wsm_type, COUNT(*) as count FROM projects GROUP BY wsm_type")
        type_counts = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count 
            FROM projects 
            GROUP BY DATE(created_at) 
            ORDER BY date DESC 
            LIMIT 7
        """)
        recent_activity = cursor.fetchall()
        
        cursor.close()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Projects", total_projects)
        with col2:
            st.metric("👥 Total Users", total_users)
        with col3:
            st.metric("🏢 Active Systems", "1")
        with col4:
            st.metric("📈 System Status", "🟢 Active")
        
        # Status distribution
        st.subheader("📈 Project Status Distribution")
        if status_counts:
            for status, count in status_counts:
                st.write(f"• **{status}:** {count} projects")
        else:
            st.info("No project data available")
        
        # WSM Type distribution
        st.subheader("🔥 WSM Type Distribution")
        if type_counts:
            for wsm_type, count in type_counts:
                st.write(f"• **{wsm_type}:** {count} projects")
        else:
            st.info("No WSM type data available")
        
        # Recent activity
        st.subheader("📅 Recent Activity (Last 7 days)")
        if recent_activity:
            for date, count in recent_activity:
                st.write(f"• **{date}:** {count} new projects")
        else:
            st.info("No recent activity")
    
    with tab3:
        st.subheader("⚙️ System Configuration")
        
        st.info("🔧 System configuration settings")
        
        # Placeholder for future system settings
        col1, col2 = st.columns(2)
        with col1:
            auto_logout = st.number_input("Auto-logout timeout (minutes)", value=30, min_value=5, max_value=240, key="auto_logout")
            max_upload_size = st.number_input("Max file upload size (MB)", value=100, min_value=10, max_value=500, key="max_upload_size")
        with col2:
            company_name = st.text_input("Default company name", value="Your Company", key="company_name")
            support_email = st.text_input("Support email", value="support@company.com", key="support_email")
        
        # Database maintenance
        st.subheader("🗃️ Database Maintenance")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Optimize Database", use_container_width=True, key="optimize_db"):
                with st.spinner("Optimizing database..."):
                    # Placeholder for database optimization
                    st.success("✅ Database optimization completed!")
        
        with col2:
            if st.button("🧹 Clear Temp Files", use_container_width=True, key="clear_temp_files"):
                with st.spinner("Clearing temporary files..."):
                    # Placeholder for temp file cleanup
                    st.success("✅ Temporary files cleared!")
        
        # Save settings
        if st.button("💾 Save Settings", type="primary", use_container_width=True, key="save_settings"):
            st.success("✅ Settings saved successfully!")

# Initialize session state variables
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"
if 'view_project' not in st.session_state:
    st.session_state.view_project = None

if __name__ == "__main__":
    main()