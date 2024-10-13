import logging
from collections import defaultdict
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# Configuração do logger
logging.basicConfig(level=logging.INFO)

class DataFrameToMarkdownPDF:
    def __init__(self, pdf_filename='report.pdf'):
        self.pdf_filename = pdf_filename

    def _group_and_sort_data(self, data):
        grouped_data = defaultdict(list)
        for item in data:
            grouped_data[item['grupo']].append(item)

        for grupo, items in grouped_data.items():
            grouped_data[grupo] = sorted(items, key=lambda x: x['date'], reverse=True)

        sorted_groups = sorted(grouped_data.items(), key=lambda x: len(x[1]), reverse=True)

        return sorted_groups

    def generate_pdf(self, data, links_df):
        sorted_groups = self._group_and_sort_data(data)

        doc = SimpleDocTemplate(self.pdf_filename, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'title_style',
            fontSize=16,
            spaceAfter=14,
            textColor=colors.darkblue,
            alignment=1 
        )
        description_style = ParagraphStyle(
            'description_style',
            fontSize=12,
            spaceAfter=10,
            textColor=colors.black,
        )
        group_style = ParagraphStyle(
            'group_style',
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkred,
        )
        item_style = ParagraphStyle(
            'item_style',
            fontSize=12,
            spaceAfter=6,
        )

        elements.append(Paragraph("Relatório de Dados Coletados", title_style))
        elements.append(Spacer(1, 0.5 * inch))

        total_links = len(links_df['links_online'])
        count_status_200 = (links_df['response_status_code'] == 200).sum()

        description = Paragraph(
            f"Foram encontrados <b>{total_links}</b> links online. Os links estão anexados no arquivo groups.json.",
            description_style
        )
        elements.append(description)
        elements.append(Spacer(1, 0.5 * inch))
        description = Paragraph(
            f"A partir dos links online, apenas <b>{count_status_200}</b> requests obtiveram status 200.",
            description_style
        )
        elements.append(description)
        elements.append(Spacer(1, 0.5 * inch))

        elements.append(Paragraph("Segue os dados coletados no intervalo de tempo solicitado, separados por grupos de forma decrescente:", description_style))
        elements.append(Spacer(1, 0.5 * inch))

        for grupo, items in sorted_groups:
            count_items = len(items)

            elements.append(Paragraph(f"Grupo: {grupo} - {count_items} resultados encontrados", group_style))
            elements.append(Spacer(1, 0.1 * inch))

            table_data = [['Title', 'Site', 'Date']]  
            for item in items:
                title = item.get('title', 'N/A')
                site = item.get('site', 'N/A')
                date = item.get('date', 'N/A')
                table_data.append([title, site, date])

            # Estilizar a tabela
            table = Table(table_data, colWidths=[2.5 * inch, 2 * inch, 1.5 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  
                ('FONTSIZE', (0, 0), (-1, 0), 12),  
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  
                ('GRID', (0, 0), (-1, -1), 1, colors.black), 
            ]))

            elements.append(table)
            elements.append(Spacer(1, 0.5 * inch))

        doc.build(elements)
        logging.info(f"PDF gerado e salvo como {self.pdf_filename}")
