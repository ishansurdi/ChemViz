"""
Data Processing Service for ChemViz
Handles CSV parsing and analytics using Pandas
"""
import pandas as pd
import numpy as np
import logging
from django.conf import settings
from django.db import transaction
from .models import Dataset, Equipment, EquipmentTypeDistribution
from .utils import validate_csv_columns, clean_numeric_value, calculate_percentage

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Service class for processing chemical equipment CSV data
    """
    
    REQUIRED_COLUMNS = [
        'Equipment Name',
        'Type',
        'Flowrate',
        'Pressure',
        'Temperature'
    ]
    
    COLUMN_MAPPING = {
        'equipment name': 'equipment_name',
        'name': 'equipment_name',
        'type': 'equipment_type',
        'equipment type': 'equipment_type',
        'flowrate': 'flowrate',
        'flow rate': 'flowrate',
        'flow': 'flowrate',
        'pressure': 'pressure',
        'temperature': 'temperature',
        'temp': 'temperature',
    }
    
    def __init__(self, dataset):
        """
        Initialize processor with a Dataset instance
        """
        self.dataset = dataset
        self.df = None
        self.errors = []
    
    def process(self):
        """
        Main processing method - orchestrates the entire data processing pipeline
        Returns: (success: bool, error_message: str or None)
        """
        try:
            # Update status
            self.dataset.processing_status = 'processing'
            self.dataset.save()
            
            # Step 1: Read CSV file
            if not self._read_csv():
                return False, "Failed to read CSV file"
            
            # Step 2: Validate columns
            if not self._validate_columns():
                return False, f"Column validation failed: {', '.join(self.errors)}"
            
            # Step 3: Clean and normalize data
            self._clean_data()
            
            # Step 4: Save equipment records to database
            with transaction.atomic():
                self._save_equipment_records()
                
                # Step 5: Calculate summary statistics
                self._calculate_summary_statistics()
                
                # Step 6: Calculate type distributions
                self._calculate_type_distribution()
            
            # Update status to completed
            self.dataset.processing_status = 'completed'
            self.dataset.save()
            
            logger.info(f"Successfully processed dataset {self.dataset.id}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error processing dataset {self.dataset.id}: {str(e)}", exc_info=True)
            self.dataset.processing_status = 'failed'
            self.dataset.error_message = str(e)
            self.dataset.save()
            return False, str(e)
    
    def _read_csv(self):
        """
        Read CSV file into pandas DataFrame
        """
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    self.df = pd.read_csv(
                        self.dataset.file.path,
                        encoding=encoding,
                        skipinitialspace=True
                    )
                    logger.info(f"Successfully read CSV with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if self.df is None:
                self.errors.append("Unable to decode CSV file with supported encodings")
                return False
            
            # Check if DataFrame is empty
            if self.df.empty:
                self.errors.append("CSV file is empty")
                return False
            
            logger.info(f"Read {len(self.df)} rows from CSV")
            return True
            
        except Exception as e:
            logger.error(f"Error reading CSV: {str(e)}")
            self.errors.append(f"Error reading CSV: {str(e)}")
            return False
    
    def _validate_columns(self):
        """
        Validate that required columns exist in the DataFrame
        """
        # Normalize column names
        self.df.columns = self.df.columns.str.strip()
        
        # Check for required columns (case-insensitive)
        df_columns_lower = [col.lower() for col in self.df.columns]
        required_columns_lower = [col.lower() for col in self.REQUIRED_COLUMNS]
        
        missing_columns = []
        for req_col in required_columns_lower:
            found = False
            for df_col in df_columns_lower:
                if req_col in df_col or df_col in req_col:
                    found = True
                    break
            if not found:
                missing_columns.append(req_col)
        
        if missing_columns:
            self.errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            return False
        
        return True
    
    def _normalize_column_names(self):
        """
        Normalize column names to standard format
        """
        new_columns = {}
        
        for col in self.df.columns:
            col_lower = col.lower().strip()
            mapped_name = self.COLUMN_MAPPING.get(col_lower, col_lower)
            new_columns[col] = mapped_name
        
        self.df.rename(columns=new_columns, inplace=True)
    
    def _clean_data(self):
        """
        Clean and normalize data in DataFrame
        """
        # Normalize column names
        self._normalize_column_names()
        
        # Ensure required columns exist with standard names
        column_mapping = {}
        for col in self.df.columns:
            col_lower = col.lower().strip()
            for key, value in self.COLUMN_MAPPING.items():
                if key in col_lower or col_lower in key:
                    column_mapping[col] = value
                    break
        
        if column_mapping:
            self.df.rename(columns=column_mapping, inplace=True)
        
        # Remove rows with missing critical values
        critical_columns = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']
        existing_critical = [col for col in critical_columns if col in self.df.columns]
        
        self.df.dropna(subset=existing_critical, how='any', inplace=True)
        
        # Clean numeric columns
        numeric_columns = ['flowrate', 'pressure', 'temperature']
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].apply(clean_numeric_value)
        
        # Remove rows with invalid numeric values
        self.df.dropna(subset=numeric_columns, inplace=True)
        
        # Convert types to string and strip whitespace
        if 'equipment_name' in self.df.columns:
            self.df['equipment_name'] = self.df['equipment_name'].astype(str).str.strip()
        if 'equipment_type' in self.df.columns:
            self.df['equipment_type'] = self.df['equipment_type'].astype(str).str.strip()
        
        # Reset index
        self.df.reset_index(drop=True, inplace=True)
        
        logger.info(f"After cleaning: {len(self.df)} valid rows")
    
    def _save_equipment_records(self):
        """
        Bulk create Equipment records from DataFrame
        """
        equipment_records = []
        
        for idx, row in self.df.iterrows():
            equipment = Equipment(
                dataset=self.dataset,
                equipment_name=row.get('equipment_name', ''),
                equipment_type=row.get('equipment_type', ''),
                flowrate=row.get('flowrate', 0),
                pressure=row.get('pressure', 0),
                temperature=row.get('temperature', 0),
                row_number=idx + 1
            )
            equipment_records.append(equipment)
        
        # Bulk create for performance
        Equipment.objects.bulk_create(equipment_records, batch_size=1000)
        
        self.dataset.row_count = len(equipment_records)
        self.dataset.save()
        
        logger.info(f"Created {len(equipment_records)} equipment records")
    
    def _calculate_summary_statistics(self):
        """
        Calculate and save summary statistics for the dataset
        """
        self.dataset.total_equipment = len(self.df)
        self.dataset.avg_flowrate = float(self.df['flowrate'].mean())
        self.dataset.avg_pressure = float(self.df['pressure'].mean())
        self.dataset.avg_temperature = float(self.df['temperature'].mean())
        self.dataset.save()
        
        logger.info("Calculated summary statistics")
    
    def _calculate_type_distribution(self):
        """
        Calculate equipment type distribution and save to database
        """
        # Group by equipment type
        type_groups = self.df.groupby('equipment_type').agg({
            'equipment_name': 'count',
            'flowrate': 'mean',
            'pressure': 'mean',
            'temperature': 'mean'
        }).reset_index()
        
        type_groups.columns = ['equipment_type', 'count', 'avg_flowrate', 'avg_pressure', 'avg_temperature']
        
        # Calculate percentages
        total_count = len(self.df)
        type_groups['percentage'] = type_groups['count'].apply(
            lambda x: calculate_percentage(x, total_count)
        )
        
        # Create distribution records
        distributions = []
        for _, row in type_groups.iterrows():
            dist = EquipmentTypeDistribution(
                dataset=self.dataset,
                equipment_type=row['equipment_type'],
                count=int(row['count']),
                percentage=float(row['percentage']),
                avg_flowrate=float(row['avg_flowrate']),
                avg_pressure=float(row['avg_pressure']),
                avg_temperature=float(row['avg_temperature'])
            )
            distributions.append(dist)
        
        # Bulk create
        EquipmentTypeDistribution.objects.bulk_create(distributions)
        
        logger.info(f"Created {len(distributions)} type distribution records")


def cleanup_old_datasets():
    """
    Maintain only the last MAX_DATASET_HISTORY datasets
    Delete older datasets and their associated records
    """
    max_history = getattr(settings, 'MAX_DATASET_HISTORY', 5)
    
    # Get all datasets ordered by upload date
    all_datasets = Dataset.objects.all().order_by('-uploaded_at')
    
    if all_datasets.count() > max_history:
        # Get datasets to delete
        datasets_to_delete = all_datasets[max_history:]
        delete_count = datasets_to_delete.count()
        
        # Delete (cascade will handle related records)
        for dataset in datasets_to_delete:
            try:
                # Delete file from filesystem
                if dataset.file:
                    dataset.file.delete(save=False)
                dataset.delete()
            except Exception as e:
                logger.error(f"Error deleting dataset {dataset.id}: {str(e)}")
        
        logger.info(f"Cleaned up {delete_count} old datasets")
        return delete_count
    
    return 0
