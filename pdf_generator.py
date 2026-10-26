"""
pdf_generator.py - Professional Offline Travel Guide PDF Generation using ReportLab.
Produces a clean, print-ready travel itinerary document with emergency contacts and checklists.
"""

import io
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)

def generate_itinerary_pdf(trip_data: Dict[str, Any]) -> bytes:
    """
    Generates a production-quality, styled offline PDF travel itinerary guide.
    Returns bytes buffer for Streamlit download button.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=6
    )

    day_title_style = ParagraphStyle(
        'DayTitle',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#2563EB'),
        spaceBefore=6,
        spaceAfter=3
    )

    slot_time_style = ParagraphStyle(
        'SlotTime',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0F766E')
    )

    body_cell = ParagraphStyle(
        'BodyCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155')
    )

    bold_cell = ParagraphStyle(
        'BoldCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0F172A')
    )

    elements = []

    # 1. Header Banner
    destination = trip_data.get("destination", "Global Voyage")
    title = trip_data.get("trip_title", f"Personalized Itinerary - {destination}")
    duration = trip_data.get("duration_days", 3)
    budget_lvl = trip_data.get("budget_level", "Moderate")
    travel_party = trip_data.get("travel_party", "Solo")
    total_cost_usd = trip_data.get("total_cost_usd", 0)
    total_cost_inr = trip_data.get("total_cost_inr", 0)

    elements.append(Paragraph("VOYAGE AI &bull; INTELLIGENT TRAVEL ITINERARY", subtitle_style))
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(f"Optimized day-by-day travel roadmap with geographic clustering & expense auditing", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=10))

    # 2. Executive Trip Summary Table
    summary_data = [
        [
            Paragraph("<b>Destination</b>", bold_cell),
            Paragraph(str(destination), body_cell),
            Paragraph("<b>Duration</b>", bold_cell),
            Paragraph(f"{duration} Days", body_cell)
        ],
        [
            Paragraph("<b>Budget Tier</b>", bold_cell),
            Paragraph(str(budget_lvl), body_cell),
            Paragraph("<b>Travel Party</b>", bold_cell),
            Paragraph(str(travel_party), body_cell)
        ],
        [
            Paragraph("<b>Est. Total (USD)</b>", bold_cell),
            Paragraph(f"${total_cost_usd:,.2f}", body_cell),
            Paragraph("<b>Est. Total (INR)</b>", bold_cell),
            Paragraph(f"₹{total_cost_inr:,.2f}", body_cell)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[1.3*inch, 2.2*inch, 1.3*inch, 2.2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 14))

    # 3. Day-by-Day Schedule
    days = trip_data.get("days", [])
    if days:
        elements.append(Paragraph("Day-by-Day Clustered Itinerary", section_heading))
        elements.append(Spacer(1, 4))

        for d in days:
            day_num = d.get("day_number", 1)
            day_theme = d.get("theme", f"Day {day_num} Highlights")
            cluster = d.get("geographic_cluster", "Central Zone")
            day_cost_usd = d.get("day_cost_usd", 0)
            day_cost_inr = d.get("day_cost_inr", 0)

            day_header_text = f"Day {day_num}: {day_theme} &nbsp;|&nbsp; <i>Cluster: {cluster}</i> &nbsp;|&nbsp; <b>Daily Est: ${day_cost_usd:.0f} (₹{day_cost_inr:,.0f})</b>"
            day_content = [
                Paragraph(day_header_text, day_title_style),
                Spacer(1, 3)
            ]

            # Slots table
            slots = d.get("slots", [])
            table_rows = [
                [
                    Paragraph("Time Slot", bold_cell),
                    Paragraph("Activity & Venue", bold_cell),
                    Paragraph("Transit / Cluster Note", bold_cell),
                    Paragraph("Est. Cost", bold_cell)
                ]
            ]

            for s in slots:
                time_slot = s.get("slot_name", "Slot")
                timing = s.get("timing", "")
                activity = s.get("activity", "Sightseeing")
                venue = s.get("venue", "City Center")
                transit = s.get("transit_tip", "Walking distance")
                cost_usd = s.get("cost_usd", 0)
                cost_inr = s.get("cost_inr", 0)

                table_rows.append([
                    Paragraph(f"<b>{time_slot}</b><br/>{timing}", slot_time_style),
                    Paragraph(f"<b>{activity}</b><br/>{venue}", body_cell),
                    Paragraph(f"{transit}", body_cell),
                    Paragraph(f"${cost_usd} / ₹{cost_inr}", body_cell)
                ])

            slot_table = Table(table_rows, colWidths=[1.4*inch, 2.7*inch, 2.0*inch, 0.9*inch])
            slot_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EEF2FF')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1E293B')),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))

            day_content.append(slot_table)
            day_content.append(Spacer(1, 10))
            elements.append(KeepTogether(day_content))

    # 4. Emergency Contacts & Travel Safety Checklist
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("Emergency Contacts & Safety Checklist", section_heading))
    
    emergency_data = [
        [
            Paragraph("<b>Service</b>", bold_cell),
            Paragraph("<b>Contact / Protocol</b>", bold_cell),
            Paragraph("<b>Operational Guidelines</b>", bold_cell)
        ],
        [
            Paragraph("Police / Security", body_cell),
            Paragraph("112 / 911 / Local Emergency", body_cell),
            Paragraph("Keep digital copy of passport and visa on secure cloud.", body_cell)
        ],
        [
            Paragraph("Medical & Ambulance", body_cell),
            Paragraph("102 / 108 / Local Paramedic", body_cell),
            Paragraph("Verify travel insurance policy number & coverage.", body_cell)
        ],
        [
            Paragraph("Tourist Assistance", body_cell),
            Paragraph("24/7 International Tourist Hotline", body_cell),
            Paragraph("Store local embassy address and taxi dispatch numbers.", body_cell)
        ]
    ]
    em_table = Table(emergency_data, colWidths=[1.8*inch, 2.3*inch, 2.9*inch])
    em_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FEF2F2')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#FCA5A5')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#FEE2E2')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(em_table)

    # 5. Smart Packing Essentials
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("Essential Traveler Packing Checklist", section_heading))
    checklist_data = [
        [
            Paragraph("&bull; Universal power adapter & high-capacity power bank", body_cell),
            Paragraph("&bull; Weather-appropriate layered apparel & walking shoes", body_cell)
        ],
        [
            Paragraph("&bull; Essential prescription medication & basic first aid", body_cell),
            Paragraph("&bull; Offline downloaded maps & offline translation tools", body_cell)
        ],
        [
            Paragraph("&bull; Dual debit/credit cards with international tx enabled", body_cell),
            Paragraph("&bull; Physical hard-copy printout of this itinerary guide", body_cell)
        ]
    ]
    check_table = Table(checklist_data, colWidths=[3.5*inch, 3.5*inch])
    check_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(check_table)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
