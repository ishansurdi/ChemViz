"""
PDF Report Generation Service
Uses ReportLab to generate professional equipment analysis reports
"""
import logging
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from django.conf import settings
from .models import Dataset, Equipment, EquipmentTypeDistribution

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """
    Generate comprehensive PDF reports for chemical equipment analysis
    """
    
    def __init__(self, dataset):
        """
        Initialize generator with a Dataset instance
        """
        self.dataset = dataset
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """
        Define custom paragraph styles for the report
        """
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1F2933'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#365F8B'),
            spaceAfter=20,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#1F2933'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Info text
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4B5563'),
            spaceAfter=6
        ))
    
    def generate(self):
        """
        Generate the complete PDF report
        Returns: BytesIO buffer containing PDF data
        """
        try:
            # Create document
            doc = SimpleDocTemplate(
                self.buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )
            
            # Build content
            story = []
            
            # Add header
            story.extend(self._build_header())
            
            # Add dataset information
            story.extend(self._build_dataset_info())
            
            # Add summary statistics
            story.extend(self._build_summary_statistics())
            
            # Add type distribution
            story.extend(self._build_type_distribution())
            
            # Add equipment table (first 50 records)
            story.extend(self._build_equipment_table())
            
            # Add footer info
            story.extend(self._build_footer())
            
            # Build PDF
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
            
            # Reset buffer position
            self.buffer.seek(0)
            
            logger.info(f"Generated PDF report for dataset {self.dataset.id}")
            return self.buffer
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
            raise
    
    def _build_header(self):
        """Build report header"""
        elements = []
        
        # Title
        title = Paragraph("Chemical Equipment Analysis Report", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Subtitle
        subtitle = Paragraph(
            f"ChemViz Analytics Platform • Industrial Intelligence Suite",
            self.styles['InfoText']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Horizontal line
        elements.append(self._create_line())
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements
    
    def _build_dataset_info(self):
        """Build dataset information section"""
        elements = []
        
        elements.append(Paragraph("Dataset Information", self.styles['CustomSubtitle']))
        
        info_data = [
            ['Dataset Name:', self.dataset.name],
            ['Upload Date:', self.dataset.uploaded_at.strftime('%Y-%m-%d %H:%M:%S UTC')],
            ['Uploaded By:', self.dataset.uploaded_by.username if self.dataset.uploaded_by else 'System'],
            ['Total Records:', str(self.dataset.row_count)],
            ['Processing Status:', self.dataset.processing_status.upper()],
            ['File Size:', self._format_file_size(self.dataset.file_size)],
        ]
        
        table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONT', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4B5563')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1F2933')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _build_summary_statistics(self):
        """Build summary statistics section"""
        elements = []
        
        elements.append(Paragraph("Summary Statistics", self.styles['CustomSubtitle']))
        
        stats_data = [
            ['Metric', 'Value', 'Unit'],
            ['Total Equipment Count', str(self.dataset.total_equipment), 'items'],
            ['Average Flowrate', f"{self.dataset.avg_flowrate:.2f}", 'L/min'],
            ['Average Pressure', f"{self.dataset.avg_pressure:.2f}", 'Bar'],
            ['Average Temperature', f"{self.dataset.avg_temperature:.2f}", '°C'],
        ]
        
        table = Table(stats_data, colWidths=[2.5 * inch, 2 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#365F8B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONT', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONT', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1F2933')),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _build_type_distribution(self):
        """Build equipment type distribution section"""
        elements = []
        
        elements.append(Paragraph("Equipment Type Distribution", self.styles['CustomSubtitle']))
        
        # Get distributions
        distributions = EquipmentTypeDistribution.objects.filter(
            dataset=self.dataset
        ).order_by('-count')
        
        if distributions.exists():
            dist_data = [['Equipment Type', 'Count', 'Percentage', 'Avg Flowrate', 'Avg Pressure', 'Avg Temp']]
            
            for dist in distributions:
                dist_data.append([
                    dist.equipment_type,
                    str(dist.count),
                    f"{dist.percentage:.1f}%",
                    f"{dist.avg_flowrate:.2f}",
                    f"{dist.avg_pressure:.2f}",
                    f"{dist.avg_temperature:.2f}"
                ])
            
            table = Table(dist_data, colWidths=[1.5*inch, 0.8*inch, 0.9*inch, 1*inch, 1*inch, 0.8*inch])
            table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#365F8B')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Data rows
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('FONT', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1F2933')),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(table)
        else:
            elements.append(Paragraph("No distribution data available.", self.styles['InfoText']))
        
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _build_equipment_table(self):
        """Build equipment records table (limited to first 50)"""
        elements = []
        
        elements.append(Paragraph("Equipment Records (First 50)", self.styles['CustomSubtitle']))
        
        # Get first 50 equipment records
        equipment = Equipment.objects.filter(dataset=self.dataset)[:50]
        
        if equipment.exists():
            table_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
            
            for eq in equipment:
                table_data.append([
                    eq.equipment_name[:30],  # Truncate long names
                    eq.equipment_type[:20],
                    f"{eq.flowrate:.2f}",
                    f"{eq.pressure:.2f}",
                    f"{eq.temperature:.2f}"
                ])
            
            table = Table(table_data, colWidths=[1.8*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#365F8B')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Data rows
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('FONT', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1F2933')),
                ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(table)
            
            if Equipment.objects.filter(dataset=self.dataset).count() > 50:
                note = Paragraph(
                    f"<i>Note: Showing first 50 of {Equipment.objects.filter(dataset=self.dataset).count()} total records.</i>",
                    self.styles['InfoText']
                )
                elements.append(Spacer(1, 0.1 * inch))
                elements.append(note)
        else:
            elements.append(Paragraph("No equipment records available.", self.styles['InfoText']))
        
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _build_footer(self):
        """Build report footer"""
        elements = []
        
        elements.append(self._create_line())
        elements.append(Spacer(1, 0.1 * inch))
        
        footer_text = f"""
        <para align=center>
        <font size=8 color='#6B7280'>
        Generated by ChemViz Analytics Platform • {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}<br/>
        Industrial Intelligence Suite v1.0 • Confidential Report
        </font>
        </para>
        """
        
        elements.append(Paragraph(footer_text, self.styles['Normal']))
        
        return elements
    
    def _create_line(self):
        """Create a horizontal line"""
        from reportlab.platypus import HRFlowable
        return HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#D1D5DB'),
            spaceBefore=0,
            spaceAfter=0
        )
    
    def _add_page_number(self, canvas, doc):
        """Add page numbers to each page"""
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#6B7280'))
        canvas.drawRightString(7.5 * inch, 0.5 * inch, text)
    
    def _format_file_size(self, size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
