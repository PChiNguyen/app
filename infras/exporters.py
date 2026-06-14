import csv
import io 
from typing import List 


from schemas.student import ReportCardDTO



class FileExporter:
    @staticmethod 
    def generate_reportcard_csv(report_cards: List[ReportCardDTO]) -> bytes:

        output= io.StringIO()
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
        """Purpose: Generate a printable, formal PDF document with borders (Future addition)"""
        # Future step: use a library like ReportLab or FPDF here
        pass
    
    


        

