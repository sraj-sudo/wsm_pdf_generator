import sqlite3
import json
import streamlit as st
from datetime import datetime

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('wsms_dashboard.db', check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        cursor = self.connection.cursor()
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_no TEXT UNIQUE,
                wsm_type TEXT CHECK(wsm_type IN ('Standard', 'Non-Standard', 'Electrical', 'WHRB', 'Custom')),
                boiler_type TEXT,
                status TEXT DEFAULT 'Submitted' CHECK(status IN ('Submitted', 'Under Review', 'Approved', 'Waiting for MRO Confirmation', 'Completed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT
            )
        """)
        
        # Project data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_no TEXT,
                section_name TEXT,
                form_data TEXT,
                FOREIGN KEY (project_no) REFERENCES projects(project_no) ON DELETE CASCADE
            )
        """)
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                email TEXT,
                role TEXT DEFAULT 'user' CHECK(role IN ('admin', 'user')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create default admin user if not exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            import hashlib
            hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute(
                "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                ('admin', hashed_password, 'admin@company.com', 'admin')
            )
        
        self.connection.commit()
        cursor.close()
    
    def create_project(self, project_data):
        try:
            cursor = self.connection.cursor()
            
            # Generate project number
            cursor.execute("SELECT COUNT(*) FROM projects WHERE wsm_type = ?", (project_data['wsm_type'],))
            count = cursor.fetchone()[0] + 1
            project_no = f"{project_data['wsm_type'][:3].upper()}-{count:04d}"
            
            # Insert project
            cursor.execute("""
                INSERT INTO projects (project_no, wsm_type, boiler_type, created_by)
                VALUES (?, ?, ?, ?)
            """, (project_no, project_data['wsm_type'], project_data['boiler_type'], project_data['created_by']))
            
            # Insert general information
            cursor.execute("""
                INSERT INTO project_data (project_no, section_name, form_data)
                VALUES (?, ?, ?)
            """, (project_no, 'general_info', json.dumps(project_data)))
            
            self.connection.commit()
            cursor.close()
            return project_no
            
        except Exception as e:
            st.error(f"Error creating project: {e}")
            return None
    
    def update_project_data(self, project_no, section_name, form_data):
        try:
            cursor = self.connection.cursor()
            
            # Check if section exists
            cursor.execute("""
                SELECT id FROM project_data WHERE project_no = ? AND section_name = ?
            """, (project_no, section_name))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing
                cursor.execute("""
                    UPDATE project_data SET form_data = ? 
                    WHERE project_no = ? AND section_name = ?
                """, (json.dumps(form_data), project_no, section_name))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO project_data (project_no, section_name, form_data)
                    VALUES (?, ?, ?)
                """, (project_no, section_name, json.dumps(form_data)))
            
            self.connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            st.error(f"Error updating project data: {e}")
            return False
    
    def get_project_data(self, project_no, section_name=None):
        try:
            cursor = self.connection.cursor()
            
            if section_name:
                cursor.execute("""
                    SELECT form_data FROM project_data 
                    WHERE project_no = ? AND section_name = ?
                """, (project_no, section_name))
                result = cursor.fetchone()
                return json.loads(result[0]) if result else None
            else:
                cursor.execute("""
                    SELECT section_name, form_data FROM project_data 
                    WHERE project_no = ?
                """, (project_no,))
                results = cursor.fetchall()
                return {row[0]: json.loads(row[1]) for row in results}
                
        except Exception as e:
            st.error(f"Error getting project data: {e}")
            return None
    
    def get_all_projects(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT p.*, 
                       (SELECT form_data FROM project_data pd 
                        WHERE pd.project_no = p.project_no AND pd.section_name = 'general_info' 
                        LIMIT 1) as general_info
                FROM projects p 
                ORDER BY p.created_at DESC
            """)
            projects = cursor.fetchall()
            
            # Convert to list of dictionaries with proper datetime handling
            result = []
            for project in projects:
                project_dict = dict(project)
                
                # Convert string timestamps to datetime objects
                if isinstance(project_dict['created_at'], str):
                    try:
                        project_dict['created_at'] = datetime.fromisoformat(project_dict['created_at'].replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        project_dict['created_at'] = datetime.now()
                
                if isinstance(project_dict['updated_at'], str):
                    try:
                        project_dict['updated_at'] = datetime.fromisoformat(project_dict['updated_at'].replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        project_dict['updated_at'] = project_dict['created_at']
                
                if project_dict['general_info']:
                    project_dict['general_info'] = json.loads(project_dict['general_info'])
                result.append(project_dict)
            
            cursor.close()
            return result
            
        except Exception as e:
            st.error(f"Error getting projects: {e}")
            return []
    
    def update_project_status(self, project_no, status):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE projects SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE project_no = ?
            """, (status, project_no))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error updating project status: {e}")
            return False

# Initialize database
def init_db():
    db = Database()
    return db