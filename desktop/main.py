"""
ChemViz Desktop Application - PyQt5 + Matplotlib
Complete desktop client connecting to Django REST API
Features: Authentication, CSV Upload, Data Tables, Charts, PDF Reports, History
"""

import sys
import os
import requests
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QTabWidget, QTextEdit, QProgressBar,
    QHeaderView, QComboBox, QGroupBox, QGridLayout, QScrollArea, QDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# API Configuration - Uses production backend by default
API_BASE_URL = os.getenv("CHEMVIZ_API_URL", "https://chemviz-backend-i9o3.onrender.com/api")

# For local development, set environment variable:
# Windows: $env:CHEMVIZ_API_URL="http://127.0.0.1:8000/api"
# Linux/Mac: export CHEMVIZ_API_URL="http://127.0.0.1:8000/api"


class MatplotlibCanvas(FigureCanvas):
    """Matplotlib canvas for embedding charts"""
    
    def __init__(self, parent=None, width=10, height=6, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.figure)
        self.setParent(parent)


class RegisterDialog(QDialog):
    """Registration dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register New Account")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Username
        layout.addWidget(QLabel("Username:"))
        self.username = QLineEdit()
        layout.addWidget(self.username)
        
        # Email
        layout.addWidget(QLabel("Email:"))
        self.email = QLineEdit()
        layout.addWidget(self.email)
        
        # Password
        layout.addWidget(QLabel("Password:"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)
        
        # Confirm password
        layout.addWidget(QLabel("Confirm Password:"))
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password)
        
        # Buttons
        btn_layout = QHBoxLayout()
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(register_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def register(self):
        username = self.username.text()
        email = self.email.text()
        password = self.password.text()
        confirm = self.confirm_password.text()
        
        if not all([username, email, password, confirm]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/register/",
                json={
                    "username": username,
                    "email": email,
                    "password": password
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                if data.get("success"):
                    QMessageBox.information(self, "Success", "Registration successful! You can now login.")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", data.get("error", {}).get("message", "Registration failed"))
            else:
                QMessageBox.warning(self, "Error", "Registration failed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")


class ChemVizApp(QMainWindow):
    """Main Application Window"""
    
    def __init__(self):
        super().__init__()
        self.access_token = None
        self.refresh_token = None
        self.user = None
        self.selected_file = None
        self.current_dataset = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("ChemViz - Chemical Equipment Analytics (Desktop)")
        self.setGeometry(50, 50, 1600, 1000)  # Larger window for better chart visibility
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)
        
        title = QLabel("ChemViz Desktop Application")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.user_label = QLabel("")
        self.user_label.setFont(QFont("Arial", 10))
        header_layout.addWidget(self.user_label)
        
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)
        self.logout_btn.hide()
        header_layout.addWidget(self.logout_btn)
        
        layout.addWidget(header)
        
        # Login section
        self.login_widget = self.create_login_widget()
        layout.addWidget(self.login_widget)
        
        # Main content (hidden until login)
        self.main_widget = QWidget()
        self.create_main_content()
        self.main_widget.hide()
        layout.addWidget(self.main_widget)
        
        # Status bar
        self.status_label = QLabel("Please login to continue")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.status_label)
    
    def create_login_widget(self):
        """Create login form"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        layout.addStretch()
        
        # Center login form
        form_widget = QWidget()
        form_widget.setMaximumWidth(400)
        form_layout = QVBoxLayout()
        form_widget.setLayout(form_layout)
        
        # Title
        login_title = QLabel("Login to ChemViz")
        login_title.setFont(QFont("Arial", 16, QFont.Bold))
        login_title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(login_title)
        
        # Username
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.returnPressed.connect(self.login)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet("padding: 10px; font-size: 14px; background-color: #4CAF50; color: white;")
        login_btn.clicked.connect(self.login)
        form_layout.addWidget(login_btn)
        
        # Register button
        register_btn = QPushButton("Register New Account")
        register_btn.setStyleSheet("padding: 10px; font-size: 12px;")
        register_btn.clicked.connect(self.show_register_dialog)
        form_layout.addWidget(register_btn)
        
        # Center the form
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(form_widget)
        center_layout.addStretch()
        layout.addLayout(center_layout)
        
        layout.addStretch()
        
        return widget
    
    def create_main_content(self):
        """Create main application content"""
        layout = QVBoxLayout()
        self.main_widget.setLayout(layout)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { padding: 10px 20px; font-size: 13px; }")
        
        # Dashboard tab
        dashboard_tab = self.create_dashboard_tab()
        self.tabs.addTab(dashboard_tab, "📊 Dashboard")
        
        # Upload tab
        upload_tab = self.create_upload_tab()
        self.tabs.addTab(upload_tab, "📤 Upload Dataset")
        
        # Summary Statistics tab (NEW)
        summary_tab = self.create_summary_tab()
        self.tabs.addTab(summary_tab, "📊 Summary Statistics")
        
        # Analytics Charts tab (CHARTS ONLY)
        analytics_tab = self.create_analytics_tab()
        self.tabs.addTab(analytics_tab, "📈 Charts & Graphs")
        
        # Data table tab
        data_tab = self.create_data_tab()
        self.tabs.addTab(data_tab, "📋 Data Table")
        
        # History tab
        history_tab = self.create_history_tab()
        self.tabs.addTab(history_tab, "🕒 History")
        
        layout.addWidget(self.tabs)
    
    def create_dashboard_tab(self):
        """Create dashboard overview tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Welcome message
        welcome = QLabel("Welcome to ChemViz Desktop Application")
        welcome.setFont(QFont("Arial", 16, QFont.Bold))
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)
        
        # Stats cards
        stats_widget = QWidget()
        stats_layout = QGridLayout()
        stats_widget.setLayout(stats_layout)
        
        self.stat_total = QLabel("0")
        self.stat_total.setFont(QFont("Arial", 24, QFont.Bold))
        self.stat_total.setAlignment(Qt.AlignCenter)
        
        self.stat_datasets = QLabel("0")
        self.stat_datasets.setFont(QFont("Arial", 24, QFont.Bold))
        self.stat_datasets.setAlignment(Qt.AlignCenter)
        
        self.stat_types = QLabel("0")
        self.stat_types.setFont(QFont("Arial", 24, QFont.Bold))
        self.stat_types.setAlignment(Qt.AlignCenter)
        
        # Create stat boxes
        stats_layout.addWidget(self.create_stat_box("Total Equipment", self.stat_total), 0, 0)
        stats_layout.addWidget(self.create_stat_box("Datasets", self.stat_datasets), 0, 1)
        stats_layout.addWidget(self.create_stat_box("Equipment Types", self.stat_types), 0, 2)
        
        layout.addWidget(stats_widget)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        actions_group.setLayout(actions_layout)
        
        upload_action = QPushButton("📤 Upload New Dataset")
        upload_action.setStyleSheet("padding: 15px; font-size: 14px; background-color: #2196F3; color: white;")
        upload_action.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        actions_layout.addWidget(upload_action)
        
        analytics_action = QPushButton("📈 View Analytics")
        analytics_action.setStyleSheet("padding: 15px; font-size: 14px; background-color: #4CAF50; color: white;")
        analytics_action.clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        actions_layout.addWidget(analytics_action)
        
        history_action = QPushButton("🕒 View History")
        history_action.setStyleSheet("padding: 15px; font-size: 14px; background-color: #FF9800; color: white;")
        history_action.clicked.connect(lambda: self.tabs.setCurrentIndex(4))
        actions_layout.addWidget(history_action)
        
        layout.addWidget(actions_group)
        
        # Recent activity
        self.dashboard_info = QTextEdit()
        self.dashboard_info.setReadOnly(True)
        self.dashboard_info.setMaximumHeight(300)
        layout.addWidget(QLabel("System Information:"))
        layout.addWidget(self.dashboard_info)
        
        layout.addStretch()
        
        return widget
    
    def create_stat_box(self, title, value_label):
        """Create a stat box widget"""
        box = QGroupBox(title)
        box.setStyleSheet("QGroupBox { font-weight: bold; padding: 10px; }")
        layout = QVBoxLayout()
        box.setLayout(layout)
        layout.addWidget(value_label)
        return box
    
    def create_upload_tab(self):
        """Create upload tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Instructions
        instructions = QLabel("Upload a CSV file containing equipment data (Equipment Name, Type, Flowrate, Pressure, Temperature)")
        instructions.setFont(QFont("Arial", 11))
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # File selection
        file_group = QGroupBox("Select File")
        file_layout = QVBoxLayout()
        file_group.setLayout(file_layout)
        
        file_btn_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("padding: 10px; background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 3px;")
        select_btn = QPushButton("Browse...")
        select_btn.setStyleSheet("padding: 10px; font-size: 12px;")
        select_btn.clicked.connect(self.select_file)
        file_btn_layout.addWidget(self.file_path_label, 1)
        file_btn_layout.addWidget(select_btn)
        file_layout.addLayout(file_btn_layout)
        
        layout.addWidget(file_group)
        
        # Dataset name
        name_group = QGroupBox("Dataset Information")
        name_layout = QVBoxLayout()
        name_group.setLayout(name_layout)
        
        name_label = QLabel("Dataset Name:")
        self.dataset_name_input = QLineEdit()
        self.dataset_name_input.setPlaceholderText("Enter a name for this dataset")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.dataset_name_input)
        
        layout.addWidget(name_group)
        
        # Upload button
        upload_btn = QPushButton("📤 Upload & Process Dataset")
        upload_btn.setStyleSheet("padding: 15px; font-size: 14px; background-color: #4CAF50; color: white;")
        upload_btn.clicked.connect(self.upload_dataset)
        layout.addWidget(upload_btn)
        
        # Progress bar
        self.upload_progress = QProgressBar()
        self.upload_progress.hide()
        layout.addWidget(self.upload_progress)
        
        # Result area
        result_label = QLabel("Upload Result:")
        layout.addWidget(result_label)
        self.upload_result = QTextEdit()
        self.upload_result.setReadOnly(True)
        self.upload_result.setMaximumHeight(200)
        layout.addWidget(self.upload_result)
        
        layout.addStretch()
        
        return widget
    
    def create_summary_tab(self):
        """Create summary statistics tab (text only)"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Summary Statistics")
        refresh_btn.setStyleSheet("padding: 12px; font-size: 13px; background-color: #2196F3; color: white;")
        refresh_btn.clicked.connect(self.load_analytics)
        layout.addWidget(refresh_btn)
        
        # Summary statistics display
        summary_group = QGroupBox("📊 Equipment Summary & Statistics")
        summary_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; padding: 15px; }")
        summary_layout = QVBoxLayout()
        
        self.analytics_text = QTextEdit()
        self.analytics_text.setReadOnly(True)
        self.analytics_text.setStyleSheet("""
            background-color: #f9f9f9; 
            font-family: 'Courier New', monospace; 
            font-size: 13px; 
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 5px;
        """)
        summary_layout.addWidget(self.analytics_text)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        return widget
    
    def create_analytics_tab(self):
        """Create analytics tab with LARGE matplotlib charts only (no text summary)"""
        widget = QWidget()
        main_layout = QVBoxLayout()
        widget.setLayout(main_layout)
        
        # Top buttons
        buttons_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh Charts")
        refresh_btn.setStyleSheet("padding: 12px; font-size: 13px; background-color: #4CAF50; color: white; font-weight: bold;")
        refresh_btn.clicked.connect(self.load_analytics)
        buttons_layout.addWidget(refresh_btn)
        
        pdf_btn = QPushButton("📄 Download PDF Report")
        pdf_btn.setStyleSheet("padding: 12px; font-size: 13px; background-color: #f44336; color: white; font-weight: bold;")
        pdf_btn.clicked.connect(self.download_pdf_report)
        buttons_layout.addWidget(pdf_btn)
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        # Scrollable charts container
        charts_scroll = QScrollArea()
        charts_scroll.setWidgetResizable(True)
        charts_widget = QWidget()
        charts_main_layout = QVBoxLayout()
        charts_widget.setLayout(charts_main_layout)
        
        # Chart 1: Bar Chart Section - EXTRA LARGE, WIDE
        bar_chart_group = QGroupBox("📊 Equipment Type Distribution (Bar Chart)")
        bar_chart_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 15px; padding: 15px; background-color: #f5f5f5; }")
        bar_layout = QVBoxLayout()
        bar_layout.setContentsMargins(5, 5, 5, 5)
        self.chart_canvas_1 = MatplotlibCanvas(bar_chart_group, width=18, height=8, dpi=100)
        self.chart_canvas_1.setMinimumHeight(650)
        bar_layout.addWidget(self.chart_canvas_1)
        bar_chart_group.setLayout(bar_layout)
        charts_main_layout.addWidget(bar_chart_group)
        
        # Chart 2: Line Chart Section - EXTRA LARGE, WIDE
        line_chart_group = QGroupBox("📈 Average Parameters by Equipment Type (Line Chart)")
        line_chart_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 15px; padding: 15px; background-color: #f5f5f5; }")
        line_layout = QVBoxLayout()
        line_layout.setContentsMargins(5, 5, 5, 5)
        self.chart_canvas_2 = MatplotlibCanvas(line_chart_group, width=18, height=8, dpi=100)
        self.chart_canvas_2.setMinimumHeight(650)
        line_layout.addWidget(self.chart_canvas_2)
        line_chart_group.setLayout(line_layout)
        charts_main_layout.addWidget(line_chart_group)
        
        # Chart 3: Pie Chart Section - LARGE SQUARE
        pie_chart_group = QGroupBox("🥧 Equipment Type Distribution (Pie Chart)")
        pie_chart_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 15px; padding: 15px; background-color: #f5f5f5; }")
        pie_layout = QVBoxLayout()
        pie_layout.setContentsMargins(5, 5, 5, 5)
        self.chart_canvas_3 = MatplotlibCanvas(pie_chart_group, width=12, height=10, dpi=100)
        self.chart_canvas_3.setMinimumHeight(750)
        pie_layout.addWidget(self.chart_canvas_3)
        pie_chart_group.setLayout(pie_layout)
        charts_main_layout.addWidget(pie_chart_group)
        
        charts_scroll.setWidget(charts_widget)
        main_layout.addWidget(charts_scroll)
        
        return widget
    
    def create_data_tab(self):
        """Create data table tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Load Data")
        refresh_btn.setStyleSheet("padding: 10px; font-size: 12px;")
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addWidget(QLabel("Page Size:"))
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["10", "25", "50", "100"])
        self.page_size_combo.setCurrentText("50")
        self.page_size_combo.currentTextChanged.connect(self.load_data)
        controls_layout.addWidget(self.page_size_combo)
        
        controls_layout.addStretch()
        
        self.data_info_label = QLabel("No data loaded")
        controls_layout.addWidget(self.data_info_label)
        
        layout.addLayout(controls_layout)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(6)
        self.data_table.setHorizontalHeaderLabels([
            "Equipment Name", "Type", "Flowrate (L/min)", "Pressure (Bar)", "Temperature (°C)", "ID"
        ])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setAlternatingRowColors(True)
        layout.addWidget(self.data_table)
        
        return widget
    
    def create_history_tab(self):
        """Create history tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh History")
        refresh_btn.setStyleSheet("padding: 10px; font-size: 12px;")
        refresh_btn.clicked.connect(self.load_history)
        layout.addWidget(refresh_btn)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Dataset Name", "Total Equipment", "Upload Date", "Status", "Action"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setAlternatingRowColors(True)
        layout.addWidget(self.history_table)
        
        return widget
    
    # Event Handlers
    
    def show_register_dialog(self):
        """Show registration dialog"""
        dialog = RegisterDialog(self)
        dialog.exec_()
    
    def login(self):
        """Login to the API"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login/",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.access_token = data["data"]["tokens"]["access"]
                    self.refresh_token = data["data"]["tokens"]["refresh"]
                    self.user = data["data"]["user"]
                    
                    # Hide login, show main content
                    self.login_widget.hide()
                    self.main_widget.show()
                    self.logout_btn.show()
                    
                    self.user_label.setText(f"👤 {self.user['username']}")
                    self.status_label.setText(f"Logged in as: {self.user['username']}")
                    
                    # Load dashboard data
                    self.refresh_dashboard()
                    
                    QMessageBox.information(self, "Success", "Login successful!")
                else:
                    QMessageBox.warning(self, "Error", data.get("error", {}).get("message", "Login failed"))
            else:
                QMessageBox.warning(self, "Error", "Invalid credentials")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
    
    def logout(self):
        """Logout from the application"""
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            requests.post(f"{API_BASE_URL}/auth/logout/", headers=headers)
        except:
            pass
        
        self.access_token = None
        self.refresh_token = None
        self.user = None
        
        self.main_widget.hide()
        self.login_widget.show()
        self.logout_btn.hide()
        self.user_label.setText("")
        self.status_label.setText("Please login to continue")
        
        self.username_input.clear()
        self.password_input.clear()
    
    def select_file(self):
        """Select CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.file_path_label.setText(file_path)
            self.selected_file = file_path
            
            # Auto-fill dataset name
            filename = os.path.basename(file_path).replace('.csv', '')
            self.dataset_name_input.setText(filename)
    
    def upload_dataset(self):
        """Upload dataset to API"""
        if not self.selected_file:
            QMessageBox.warning(self, "Error", "Please select a file first")
            return
        
        dataset_name = self.dataset_name_input.text()
        if not dataset_name:
            QMessageBox.warning(self, "Error", "Please enter a dataset name")
            return
        
        try:
            self.upload_progress.show()
            self.upload_progress.setRange(0, 0)  # Indeterminate
            self.status_label.setText("Uploading dataset...")
            
            with open(self.selected_file, 'rb') as f:
                files = {'file': f}
                data = {'name': dataset_name}
                headers = {'Authorization': f'Bearer {self.access_token}'}
                
                response = requests.post(
                    f"{API_BASE_URL}/datasets/upload/",
                    files=files,
                    data=data,
                    headers=headers
                )
            
            self.upload_progress.hide()
            
            if response.status_code == 201:
                result = response.json()
                if result.get("success"):
                    data = result['data']
                    self.upload_result.setText(
                        f"✅ Upload successful!\n\n"
                        f"Dataset: {data['name']}\n"
                        f"Total Equipment: {data['total_equipment']}\n"
                        f"Status: {data['processing_status']}\n"
                        f"Uploaded: {data['uploaded_at']}"
                    )
                    self.status_label.setText("Dataset uploaded successfully!")
                    self.refresh_dashboard()
                    QMessageBox.information(self, "Success", "Dataset uploaded and processed successfully!")
                else:
                    error_msg = result.get("error", {}).get("message", "Upload failed")
                    self.upload_result.setText(f"❌ Error: {error_msg}")
                    QMessageBox.warning(self, "Error", error_msg)
            else:
                QMessageBox.warning(self, "Error", "Upload failed. Please check your file format.")
        except Exception as e:
            self.upload_progress.hide()
            self.status_label.setText("Upload failed")
            QMessageBox.critical(self, "Error", f"Upload error: {str(e)}")
    
    def refresh_dashboard(self):
        """Refresh dashboard statistics"""
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            # Get summary
            response = requests.get(f"{API_BASE_URL}/summary/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    summary = data.get("data", {})
                    
                    # Safely get total equipment
                    if isinstance(summary, dict):
                        self.stat_total.setText(str(summary.get('total_equipment', 0)))
                        distribution = summary.get('equipment_type_distribution', [])
                        if isinstance(distribution, list):
                            self.stat_types.setText(str(len(distribution)))
                        else:
                            self.stat_types.setText("0")
                    else:
                        self.stat_total.setText("0")
                        self.stat_types.setText("0")
            
            # Get history count
            history_response = requests.get(f"{API_BASE_URL}/datasets/history/", headers=headers)
            if history_response.status_code == 200:
                hist_data = history_response.json()
                if hist_data.get("success"):
                    datasets_data = hist_data.get('data', {})
                    if isinstance(datasets_data, dict):
                        self.stat_datasets.setText(str(datasets_data.get('total_datasets', 0)))
                    else:
                        self.stat_datasets.setText("0")
            
            # Update dashboard info - SAFE ACCESS
            info_text = f"API Connection: ✅ Connected\n"
            info_text += f"Backend: {API_BASE_URL}\n"
            
            # Safely access user object
            if self.user is not None and isinstance(self.user, dict):
                username = self.user.get('username', 'N/A')
                email = self.user.get('email', 'N/A')
                info_text += f"User: {username} ({email})\n"
            elif self.user is not None:
                # If user is not a dict, convert to string
                info_text += f"User: {str(self.user)}\n"
            else:
                info_text += f"User: Not logged in\n"
                
            info_text += f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.dashboard_info.setText(info_text)
            
        except Exception as e:
            error_msg = f"Error loading dashboard: {str(e)}\nType: {type(e).__name__}"
            self.dashboard_info.setText(error_msg)
            print(f"Dashboard error details: {e}")  # Debug print
    
    def load_analytics(self):
        """Load analytics data and draw charts"""
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(f"{API_BASE_URL}/summary/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    summary = data["data"]
                    
                    # Display text summary
                    analytics_text = f"""
=== Summary Statistics ===

Total Equipment: {summary['total_equipment']}
Average Flowrate: {summary['avg_flowrate']:.2f} L/min
Average Pressure: {summary['avg_pressure']:.2f} Bar
Average Temperature: {summary['avg_temperature']:.2f} °C

=== Equipment Type Distribution ===
"""
                    for dist in summary['equipment_type_distribution']:
                        analytics_text += f"\n{dist['equipment_type']}: {dist['count']} units ({dist['percentage']:.1f}%)"
                    
                    self.analytics_text.setText(analytics_text)
                    
                    # Draw charts
                    self.draw_charts(summary)
                    
                    self.status_label.setText("Analytics loaded successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load analytics: {str(e)}")
    
    def draw_charts(self, summary):
        """Draw matplotlib charts"""
        distribution = summary['equipment_type_distribution']
        
        # Extract data
        types = [d['equipment_type'] for d in distribution]
        counts = [d['count'] for d in distribution]
        avg_flowrate = [d['avg_flowrate'] for d in distribution]
        avg_pressure = [d['avg_pressure'] for d in distribution]
        avg_temp = [d['avg_temperature'] for d in distribution]
        
        # Chart 1: Bar chart for equipment counts - OPTIMIZED FOR WIDTH
        self.chart_canvas_1.figure.clear()
        ax1 = self.chart_canvas_1.figure.add_subplot(111)
        ax1.bar(types, counts, color='#2196F3', alpha=0.8, edgecolor='black', width=0.6)
        ax1.set_xlabel('Equipment Type', fontsize=14, fontweight='bold', labelpad=10)
        ax1.set_ylabel('Count', fontsize=14, fontweight='bold', labelpad=10)
        ax1.set_title('Equipment Type Distribution', fontsize=16, fontweight='bold', pad=20)
        ax1.tick_params(axis='x', rotation=45, labelsize=11)
        ax1.tick_params(axis='y', labelsize=11)
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        # Maximize horizontal space
        self.chart_canvas_1.figure.subplots_adjust(bottom=0.25, left=0.08, right=0.97, top=0.93)
        self.chart_canvas_1.draw()
        
        # Chart 2: Line chart for averages - OPTIMIZED FOR WIDTH
        self.chart_canvas_2.figure.clear()
        ax2 = self.chart_canvas_2.figure.add_subplot(111)
        x_pos = range(len(types))
        ax2.plot(x_pos, avg_flowrate, marker='o', label='Flowrate (L/min)', linewidth=3, markersize=10)
        ax2.plot(x_pos, avg_pressure, marker='s', label='Pressure (Bar)', linewidth=3, markersize=10)
        ax2.plot(x_pos, avg_temp, marker='^', label='Temperature (°C)', linewidth=3, markersize=10)
        ax2.set_xlabel('Equipment Type', fontsize=14, fontweight='bold', labelpad=10)
        ax2.set_ylabel('Average Value', fontsize=14, fontweight='bold', labelpad=10)
        ax2.set_title('Average Parameters by Equipment Type', fontsize=16, fontweight='bold', pad=20)
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(types, rotation=45, ha='right', fontsize=11)
        ax2.tick_params(axis='y', labelsize=11)
        ax2.legend(fontsize=12, loc='best', frameon=True, shadow=True)
        ax2.grid(True, alpha=0.3, linestyle='--')
        # Maximize horizontal space
        self.chart_canvas_2.figure.subplots_adjust(bottom=0.25, left=0.08, right=0.97, top=0.93)
        self.chart_canvas_2.draw()
        
        # Chart 3: Pie chart - LARGE AND CLEAR
        self.chart_canvas_3.figure.clear()
        ax3 = self.chart_canvas_3.figure.add_subplot(111)
        colors = plt.cm.Set3(range(len(types)))
        wedges, texts, autotexts = ax3.pie(
            counts, labels=types, autopct='%1.1f%%', startangle=90, 
            colors=colors, textprops={'fontsize': 11, 'weight': 'bold'}
        )
        # Make percentage text bold and larger
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')
        # Make labels larger
        for text in texts:
            text.set_fontsize(11)
        ax3.set_title('Equipment Type Distribution', fontsize=16, fontweight='bold', pad=20)
        self.chart_canvas_3.draw()
    
    def load_data(self):
        """Load equipment data"""
        try:
            page_size = int(self.page_size_combo.currentText())
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(
                f"{API_BASE_URL}/data/",
                headers=headers,
                params={'page_size': page_size}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    equipment_list = data["data"]["equipment"]
                    total = data["data"]["total_equipment"]
                    
                    self.data_info_label.setText(f"Showing {len(equipment_list)} of {total} records")
                    
                    self.data_table.setRowCount(len(equipment_list))
                    for i, eq in enumerate(equipment_list):
                        self.data_table.setItem(i, 0, QTableWidgetItem(eq['equipment_name']))
                        self.data_table.setItem(i, 1, QTableWidgetItem(eq['equipment_type']))
                        self.data_table.setItem(i, 2, QTableWidgetItem(f"{eq['flowrate']:.2f}"))
                        self.data_table.setItem(i, 3, QTableWidgetItem(f"{eq['pressure']:.2f}"))
                        self.data_table.setItem(i, 4, QTableWidgetItem(f"{eq['temperature']:.2f}"))
                        self.data_table.setItem(i, 5, QTableWidgetItem(str(eq['id'])))
                    
                    self.status_label.setText(f"Loaded {len(equipment_list)} equipment records")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")
    
    def load_history(self):
        """Load dataset history"""
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(f"{API_BASE_URL}/datasets/history/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Safely extract datasets - handle both dict and direct list responses
                    data_content = data.get("data", {})
                    
                    if isinstance(data_content, dict):
                        datasets = data_content.get("datasets", [])
                    elif isinstance(data_content, list):
                        # If data is already a list, use it directly
                        datasets = data_content
                    else:
                        datasets = []
                    
                    self.history_table.setRowCount(len(datasets))
                    if len(datasets) == 0:
                        self.status_label.setText("No datasets found in history. Upload a dataset first!")
                    else:
                        for i, ds in enumerate(datasets):
                            # Ensure ds is a dict
                            if not isinstance(ds, dict):
                                continue
                                
                            self.history_table.setItem(i, 0, QTableWidgetItem(ds.get('name', 'N/A')))
                            self.history_table.setItem(i, 1, QTableWidgetItem(str(ds.get('total_equipment', 0))))
                            self.history_table.setItem(i, 2, QTableWidgetItem(ds.get('uploaded_at', 'N/A')))
                            self.history_table.setItem(i, 3, QTableWidgetItem(ds.get('processing_status', 'N/A')))
                            
                            # Action button
                            view_btn = QPushButton("View Details")
                            view_btn.clicked.connect(lambda checked, d=ds: self.show_dataset_details(d))
                            self.history_table.setCellWidget(i, 4, view_btn)
                        
                        self.status_label.setText(f"Loaded {len(datasets)} datasets from history")
                else:
                    error_msg = data.get("error", {}).get("message", "Unknown error")
                    self.status_label.setText(f"Error: {error_msg}")
                    QMessageBox.warning(self, "Error", f"Failed to load history: {error_msg}")
            else:
                error_text = response.text[:200] if response.text else "No response"
                self.status_label.setText(f"Error: Server returned {response.status_code}")
                QMessageBox.warning(self, "Error", f"Server error ({response.status_code}): {error_text}")
        except Exception as e:
            self.status_label.setText(f"Error loading history")
            error_details = f"Error loading History: {str(e)}\nType: {type(e).__name__}"
            QMessageBox.critical(self, "Error", error_details)
            print(f"History loading error: {e}")  # Debug print
    
    def show_dataset_details(self, dataset):
        """Show dataset details"""
        if not isinstance(dataset, dict):
            QMessageBox.warning(self, "Error", "Invalid dataset format")
            return
            
        details = f"""
Dataset Details:

Name: {dataset.get('name', 'N/A')}
Total Equipment: {dataset.get('total_equipment', 0)}
Upload Date: {dataset.get('uploaded_at', 'N/A')}
Status: {dataset.get('processing_status', 'N/A')}
Dataset ID: {dataset.get('id', 'N/A')}
"""
        QMessageBox.information(self, "Dataset Details", details)
    
    def download_pdf_report(self):
        """Download PDF report"""
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(f"{API_BASE_URL}/report/", headers=headers)
            
            if response.status_code == 200:
                # Save file dialog
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Save PDF Report", "equipment_report.pdf", "PDF Files (*.pdf)"
                )
                
                if file_path:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    QMessageBox.information(self, "Success", f"PDF report saved to:\n{file_path}")
                    self.status_label.setText("PDF report downloaded successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to generate PDF report")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download PDF: {str(e)}")


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = ChemVizApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
