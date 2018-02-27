# -*- coding: utf-8 -*-
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.lineplots import ScatterPlot
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, String
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import red,green,blue,pink,grey,white,cyan,magenta
from reportlab.platypus import SimpleDocTemplate,PageBreak,Table,TableStyle,Paragraph,Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm,mm,inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.pagesizes import A4

from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin
from reportlab.lib.colors import Color, magenta, cyan

from reportlab.lib.colors import black, red, purple, green, maroon, brown, pink, white, HexColor
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.validators import Auto
from reportlab.lib.colors import HexColor, black

from reportlab.graphics.charts.lineplots import GridLinePlot
from reportlab.lib.colors import Color
from reportlab.graphics.charts.legends import LineLegend
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin
from reportlab.lib.validators import Auto
from reportlab.graphics.charts.axes import NormalDateXValueAxis
from reportlab.graphics.widgets.markers import makeMarker


fontname='Helvetica'
def createHeaderFooter(canvas,doc):
    canvas.saveState()    
    canvas.setFont(fontname,8)
    footer="Highly Confidential. Copyright © 2016"
    canvas.drawString(inch/2, 0.75 * inch, footer)
    canvas.setStrokeColor(colors.HexColor('#bfff00'))
    canvas.line(inch/2,inch,550,inch)
    canvas.setPageTransition(effectname='Wipe',duration=1)    
    canvas.setFont(fontname,8)
    canvas.setPageDuration(600)   
    # "Chart Report For ReportName v 1.0 "
    # canvas.drawImage('we45-Logo.jpg', 470, 790,width=80,height=45)
    # canvas.drawImage(doc.clientlogo, inch/2, 790,width=80,height=45)

    # canvas.drawImage(doc.clientlogo, 0, 790,width=80,height=45)
    # if doc.complogo: 
    #     canvas.drawImage(doc.complogo, 470, 790,width=80,height=45)
    canvas.setStrokeColor(colors.HexColor('#bfff00'))
    canvas.line(inch/2,  780,550,  780)
    canvas.drawCentredString(inch*4, 790, doc.header )    
    canvas.drawRightString(inch*7.5, 0.75 * inch, "Page %s"%(doc.page))
    canvas.restoreState()

def createCoverPage(canvas,doc):
    canvas.saveState()    
    canvas.setFont(fontname,8)
    footer="Highly Confidential. Copyright © 2015 SecuritySlate."
    canvas.drawString(inch/2, 0.75 * inch, footer)
    canvas.setStrokeColor(colors.HexColor('#bfff00'))
    canvas.line(inch/2,inch,550,inch)    # 
    canvas.setFont(fontname,18)  
    canvas.drawCentredString(inch*4, 490, doc.title ) 
    #"Chart Report For ReportName"
    # canvas.drawImage(doc.clientlogo, inch/2, 790,width=240,height=135)
    canvas.setStrokeColor(colors.HexColor('#bfff00'))
    canvas.line(inch/2,  780,550,  780)
    canvas.setFont(fontname,8)
    canvas.drawCentredString(inch*4, 790, doc.header )    
    canvas.drawRightString(inch*7.5, 0.75 * inch, "Page %s"%(doc.page))
    

    canvas.restoreState()

def createTable(tableData,cutom_width=8*cm): 
    # tab = Table(tableData, colWidths=(1*cm,width*cm,width*cm),rowHeights=None,repeatRows=1)
    tab = Table(tableData, colWidths=cutom_width,rowHeights=None,repeatRows=1)
    tab.hAlign = TA_LEFT
    tblStyle = TableStyle([('TEXTCOLOR',(0,0),(-1,-1),"#231F20"), 
                            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                            ('LINEBELOW',(0,2),(-1,2),0.25,colors.black),
                          ('BOX',(0,0),(-1,-1),0.25,colors.black),
                           ('FONTNAME', (0, 0), (0, -1), fontname),
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('TEXTFONT', (0, 0), (-1, -1), 'Times-Bold'), 
                           ('BOX',(0,0),(-1,-1),0.25,colors.black),('ALIGN',(0,0),(-1,-1),'CENTER')])
    tblStyle.add('BACKGROUND',(0,0),(3,0),"#bfff00")
    tblStyle.add('BACKGROUND',(0,1),(-1,-1),colors.white)    
    tab.setStyle(tblStyle)
    return tab

def createHeading(text):
    style=ParagraphStyle(name='Style',leftIndent=0,fontSize=20,fontName=fontname,textColor=colors.HexColor('#bfff00'))
    paragraph=Paragraph("<para alignment='center' leading='30'><b>%s</b></para>"%text,style)
    return paragraph

def createTitle(text, left=120):
    style=ParagraphStyle(name='Style',leftIndent=0,fontSize=16,fontName=fontname,textColor=colors.HexColor('#bfff00'))
    paragraph=Paragraph("<para alignment='center' leading='30'><b><u>%s</u></b></para>"%text,style)
    return paragraph

def createTitleLegend(text):
    style=ParagraphStyle(name='Style',leftIndent=0,fontSize=12,fontName=fontname,textColor=colors.HexColor('#bfff00'))
    paragraph=Paragraph("<para alignment='center' leading='30'><b><u>%s</u></b></para>"%text,style)
    return paragraph

def createCenterHeading(text):
    style=ParagraphStyle(name='Style',leftIndent=0,fontSize=16,fontName=fontname,textColor=colors.HexColor('#bfff00'))
    paragraph=Paragraph("<para alignment='center' leading='30'><b>%s</b></para>"%text,style)
    return paragraph

import os
if __name__=="__main__": #NORUNTESTS

    doc=SimpleDocTemplate('Test-Report.pdf',pageSize=A4,leftMargin=72,rightMargin=10)
    elements=[]
    elements.append(PageBreak())
    attack = "Reflected XSS Attack"
    doc.header = "Chart Report For %s"%attack
    doc.title = "Chart Report For %s"%attack
    image_path = os.path.join('Upload_Pics','moto_x_style.jpeg')
    image_path = "%s\%s"%(os.getcwd(),image_path)
    title=createTitleLegend('Attack Name')
    elements.append(title)
    elements.append(Image(image_path))
    doc.build(elements,onFirstPage=createCoverPage,onLaterPages=createHeaderFooter)