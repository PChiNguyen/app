import csv
import io 
from typing import List 
from fpdf import FPDF 
from pathlib import Path

from schemas.student import ReportCardDTO

# 1. Automatically calculate the absolute path to your root folder and fonts
PROJECT_ROOT = Path(__file__).parent.parent
FONTS_DIR = PROJECT_ROOT / "fonts"

# ONLY ONE CLASS DEFINITION!
class FileExporter:
    
    @staticmethod 
    def generate_reportcard_csv(report_cards: List[ReportCardDTO]) -> bytes:
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(["Rank", "Student ID", "Student Name", "GPA"]) 
        
        for record in report_cards:
            writer.writerow([record.class_rank, str(record.student_id), record.student_name, f'{record.gpa:.2f}'])

        csv_data = output.getvalue()
        output.close()
        return csv_data.encode('utf-8')  
    
    @staticmethod
    def generate_student_roster_txt(student_names: List[str]) -> bytes:
        """Purpose: Create a raw text file list for printable attendance roll calls"""
        output = io.StringIO()
        output.write("=== OFFICIAL CLASS ATTENDANCE ROSTER ===\n\n")
        
        for index, name in enumerate(student_names, 1):
            output.write(f"{index}. [ ] {name}\n")
            
        txt_data = output.getvalue()
        output.close() # Crucial: Clears the RAM
        return txt_data.encode("utf-8")

    @staticmethod
    def generate_report_card_pdf(report_card: ReportCardDTO) -> bytes:
        """Purpose: Generate a printable, formal PDF document."""
        pdf = FPDF()
        pdf.add_page()
        
        # 2. Construct the absolute paths for the font files
        regular_font_path = str(FONTS_DIR / "Roboto-Regular.ttf")
        bold_font_path = str(FONTS_DIR / "Roboto-Bold.ttf")
        
        # 3. Load the fonts into the printer's memory
        pdf.add_font("Roboto", "", regular_font_path)
        pdf.add_font("Roboto", "B", bold_font_path)
        
        # 4. Swap to the new Unicode font
        pdf.set_font("Roboto", "B", 16)
        pdf.cell(0, 10, "THPT AN PHUOC - Official Report Card", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(0, 10, "", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("Roboto", "", 12)
        pdf.cell(0, 10, f"Student ID: {report_card.student_id}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 10, f"Name: {report_card.student_name}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 10, f"Class Rank: #{report_card.class_rank}", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("Roboto", "B", 12)
        pdf.cell(0, 10, f"Final GPA: {f'{report_card.gpa:.2f}' if report_card.gpa is not None else 'N/A'}", new_x="LMARGIN", new_y="NEXT")
        
        pdf_bytes = bytes(pdf.output())
        return pdf_bytes

    @staticmethod
    def generate_batch_report_cards_pdf(report_cards: List[ReportCardDTO]) -> bytes:
        """Purpose: Generate a single PDF containing multiple report cards, one per page."""
        pdf = FPDF()
        
        # You only need to load the fonts ONCE per document, outside the loop
        regular_font_path = str(FONTS_DIR / "Roboto-Regular.ttf")
        bold_font_path = str(FONTS_DIR / "Roboto-Bold.ttf")
        
        pdf.add_font("Roboto", "", regular_font_path)
        pdf.add_font("Roboto", "B", bold_font_path)
        
        for report_card in report_cards:
            pdf.add_page()
            
            pdf.set_font("Roboto", "B", 16)
            pdf.cell(0, 10, "THPT AN PHUOC - Official Report Card", new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.cell(0, 10, "", new_x="LMARGIN", new_y="NEXT") 
            
            pdf.set_font("Roboto", "", 12)
            pdf.cell(0, 10, f"Student ID: {report_card.student_id}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"Name: {report_card.student_name}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"Class Rank: #{report_card.class_rank}", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("Roboto", "B", 12)
            pdf.cell(0, 10, f"Final GPA: {f'{report_card.gpa:.2f}' if report_card.gpa is not None else 'N/A'}", new_x="LMARGIN", new_y="NEXT")
            
        pdf_bytes = bytes(pdf.output())
        return pdf_bytes