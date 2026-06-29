# create_timetable_from_data.py
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import simpleSplit
from pathlib import Path
import os

# Define the timetable data from your image
timetable_data = {
    "Monday": {
        "Batch": "Bhaat Singh",
        "Room": "BS-503",
        "Floor": "4th Floor",
        "Schedule": [
            "Communication (C5)",
            "Technical (T41)",
            "Break",
            "Technical (T41)"
        ]
    },
    "Tuesday": {
        "Batch": "Bhaat Singh",
        "Room": "BS-503",
        "Floor": "4th Floor",
        "Schedule": [
            "Aptitude (A11)",
            "Technical (T41)",
            "Break",
            "Technical (T41)"
        ]
    },
    "Wednesday": {
        "Batch": "Bhaat Singh",
        "Room": "BS-503",
        "Floor": "4th Floor",
        "Schedule": [
            "Technical (T41)",
            "Technical (T41)",
            "Break",
            "Communication (C5)"
        ]
    },
    "Thursday": {
        "Batch": "Bhaat Singh",
        "Room": "BS-503",
        "Floor": "4th Floor",
        "Schedule": [
            "Technical (T41)",
            "Technical (T41)",
            "Break",
            "Aptitude (A11)"
        ]
    },
    "Friday": {
        "Batch": "Bhaat Singh",
        "Room": "BS-503",
        "Floor": "4th Floor",
        "Schedule": [
            "Technical (T41)",
            "Technical (T41)",
            "Break",
            "Aptitude (A11)"
        ]
    }
}

# Set path
project_root = Path(r"C:\Users\vaidehi koranne\OneDrive\Desktop\multilingual university chatbot")
output_path = project_root / "study_materials" / "impact_timetable.pdf"

# Create PDF with better formatting
def create_timetable_pdf():
    # Use landscape for better table layout
    c = canvas.Canvas(str(output_path), pagesize=landscape(letter))
    width, height = landscape(letter)
    
    # Title
    c.setFont("Helvetica-Bold", 18)
    title = "WEEKLY TIMETABLE - Bhaat Singh (Batch BS-503, 4th Floor)"
    c.drawString(0.5*inch, height - 0.5*inch, title)
    
    # Subtitle
    c.setFont("Helvetica", 10)
    c.drawString(0.5*inch, height - 0.8*inch, f"Room: BS-503 | Floor: 4th Floor")
    
    # Draw the timetable table
    start_y = height - 1.3*inch
    row_height = 0.4*inch
    
    # Column headers
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.5*inch, start_y, "Day")
    c.drawString(1.3*inch, start_y, "Period 1 (9:00-10:30)")
    c.drawString(3.0*inch, start_y, "Period 2 (10:30-12:00)")
    c.drawString(4.7*inch, start_y, "Break (12:00-1:00)")
    c.drawString(5.7*inch, start_y, "Period 3 (1:00-2:30)")
    
    # Draw line under headers
    c.line(0.4*inch, start_y - 0.1*inch, width - 0.4*inch, start_y - 0.1*inch)
    
    # Days and schedule
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    y_pos = start_y - row_height
    
    c.setFont("Helvetica", 10)
    for i, day in enumerate(days):
        day_data = timetable_data[day]
        schedule = day_data["Schedule"]
        
        # Day name
        c.setFont("Helvetica-Bold", 11)
        c.drawString(0.5*inch, y_pos, day)
        
        # Schedule items
        c.setFont("Helvetica", 10)
        if len(schedule) >= 4:
            c.drawString(1.3*inch, y_pos, schedule[0])
            c.drawString(3.0*inch, y_pos, schedule[1])
            c.drawString(4.7*inch, y_pos, schedule[2])
            c.drawString(5.7*inch, y_pos, schedule[3])
        
        # Draw line between rows
        c.line(0.4*inch, y_pos - 0.1*inch, width - 0.4*inch, y_pos - 0.1*inch)
        
        y_pos -= row_height
    
    # Add detailed schedule text for better searchability
    c.showPage()  # New page for detailed text
    
    # Second page: Detailed schedule in text format (easy for chatbot to read)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.5*inch, height - 0.5*inch, "DETAILED TIMETABLE INFORMATION")
    
    y = height - 1*inch
    c.setFont("Helvetica", 11)
    
    for day in days:
        day_data = timetable_data[day]
        schedule = day_data["Schedule"]
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0.5*inch, y, f"{day}")
        y -= 0.25*inch
        
        c.setFont("Helvetica", 10)
        c.drawString(0.5*inch, y, f"Batch: {day_data['Batch']}")
        y -= 0.2*inch
        c.drawString(0.5*inch, y, f"Room: {day_data['Room']} ({day_data['Floor']})")
        y -= 0.25*inch
        
        c.drawString(0.5*inch, y, f"Period 1 (9:00-10:30): {schedule[0]}")
        y -= 0.2*inch
        c.drawString(0.5*inch, y, f"Period 2 (10:30-12:00): {schedule[1]}")
        y -= 0.2*inch
        c.drawString(0.5*inch, y, f"Break (12:00-1:00): {schedule[2]}")
        y -= 0.2*inch
        c.drawString(0.5*inch, y, f"Period 3 (1:00-2:30): {schedule[3]}")
        y -= 0.3*inch
        
        c.line(0.5*inch, y + 0.1*inch, width - 0.5*inch, y + 0.1*inch)
        y -= 0.2*inch
        
        if y < 1*inch:
            c.showPage()
            y = height - 0.5*inch
            c.setFont("Helvetica", 11)
    
    c.save()
    print(f"✅ Created text-based timetable PDF at: {output_path}")
    print(f"📄 File size: {output_path.stat().st_size} bytes")
    print(f"\n📅 Timetable includes:")
    for day in days:
        print(f"  • {day}: {timetable_data[day]['Schedule'][0]}, {timetable_data[day]['Schedule'][1]}, Break, {timetable_data[day]['Schedule'][3]}")

# Alternative: Create a simple text file that's even easier for the chatbot
def create_text_file():
    text_path = project_root / "study_materials" / "timetable_data.txt"
    
    with open(text_path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("WEEKLY TIMETABLE - Bhaat Singh\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("Batch: BS-503\n")
        f.write("Room: 4th Floor\n\n")
        
        f.write("-" * 60 + "\n")
        f.write("MONDAY SCHEDULE:\n")
        f.write("-" * 60 + "\n")
        f.write("• 9:00-10:30: Communication (C5)\n")
        f.write("• 10:30-12:00: Technical (T41)\n")
        f.write("• 12:00-1:00: Break\n")
        f.write("• 1:00-2:30: Technical (T41)\n\n")
        
        f.write("-" * 60 + "\n")
        f.write("TUESDAY SCHEDULE:\n")
        f.write("-" * 60 + "\n")
        f.write("• 9:00-10:30: Aptitude (A11)\n")
        f.write("• 10:30-12:00: Technical (T41)\n")
        f.write("• 12:00-1:00: Break\n")
        f.write("• 1:00-2:30: Technical (T41)\n\n")
        
        f.write("-" * 60 + "\n")
        f.write("WEDNESDAY SCHEDULE:\n")
        f.write("-" * 60 + "\n")
        f.write("• 9:00-10:30: Technical (T41)\n")
        f.write("• 10:30-12:00: Technical (T41)\n")
        f.write("• 12:00-1:00: Break\n")
        f.write("• 1:00-2:30: Communication (C5)\n\n")
        
        f.write("-" * 60 + "\n")
        f.write("THURSDAY SCHEDULE:\n")
        f.write("-" * 60 + "\n")
        f.write("• 9:00-10:30: Technical (T41)\n")
        f.write("• 10:30-12:00: Technical (T41)\n")
        f.write("• 12:00-1:00: Break\n")
        f.write("• 1:00-2:30: Aptitude (A11)\n\n")
        
        f.write("-" * 60 + "\n")
        f.write("FRIDAY SCHEDULE:\n")
        f.write("-" * 60 + "\n")
        f.write("• 9:00-10:30: Technical (T41)\n")
        f.write("• 10:30-12:00: Technical (T41)\n")
        f.write("• 12:00-1:00: Break\n")
        f.write("• 1:00-2:30: Aptitude (A11)\n\n")
    
    print(f"✅ Created text file at: {text_path}")
    return text_path

# Create both PDF and text file for best results
if __name__ == "__main__":
    # Install reportlab if not already installed
    try:
        from reportlab.lib.pagesizes import letter
    except ImportError:
        print("Installing reportlab...")
        os.system("pip install reportlab")
        from reportlab.lib.pagesizes import letter
    
    # Create the PDF
    create_timetable_pdf()
    
    # Create a text file (even better for the chatbot)
    text_file = create_text_file()
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Files created:")
    print(f"  • PDF: {project_root / 'study_materials' / 'impact_timetable.pdf'}")
    print(f"  • Text: {text_file}")
    print("\n📝 NEXT STEPS:")
    print("  1. Restart your chatbot: Press Ctrl+C then run 'py main.py'")
    print("  2. Try asking: 'what is the schedule for Monday'")
    print("  3. Try asking: 'what classes are on Tuesday morning'")
    print("  4. Try asking: 'provide me timetable pdf'")
    print("=" * 60)