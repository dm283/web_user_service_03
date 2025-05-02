# service functions
from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfbase import pdfmetrics 
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

import qrcode


def create_document_carpass(carpass, filepath, filename):
    # creates carpass pdf file for printing
    pdf = canvas.Canvas(filepath) 
    pdf.setTitle(filename) 
    pdfmetrics.registerFont(TTFont('Arial', 'verdana.ttf')) 

    box_yes = {}; box_no = {}
    for a in ['brokenAwning', 'brokenSeal', 'radiation']:
        box_yes[a] = 'X' if getattr(carpass, a) else ''
        box_no[a] = 'X' if not getattr(carpass, a) else ''

    # ======================================================================  ПРОПУСК
    pdf.setFont("Arial", 8); pdf.drawString(45, 810, 'ООО "Мультимодальные Транспортные Системы"')
    pdf.setFont("Arial", 14); pdf.drawString(42, 780, f'ПРОПУСК №  {carpass.id_enter}')
    pdf.setFont("Arial", 9); pdf.drawString(135, 780, '________________________')
    pdf.setFont("Arial", 7)
    pdf.drawString(37, 765, 'Московская область, городской округ Ступино, р.п. Михнево,')
    pdf.drawString(73, 755, 'ул.Старомихневская, уч.47, вл. 47, вл.47,')
    pdf.drawString(95, 745, 'стр.1, уч.49, сооружение 49')
    pdf.setFont("Arial", 9)
    pdf.drawString(25, 725, 'Фирма получатель:')
    pdf.drawString(25, 710, f'{carpass.contact_name}')
    pdf.drawString(25, 690, 'Перевозчик:')
    pdf.drawString(25, 675, f'{carpass.driver}')
    
    text_lines = [ 
        f'Номер автомашины:  {carpass.ncar}', 
        f'Дата въезда:  {carpass.dateen}', 
        f'Время въезда:  {carpass.timeen}', 
        f'Номер стоянки:  {carpass.place_n}', 
        f'Ф.И.О. водителя:  {carpass.driver_fio}', 
        f'Телефон водителя:  {carpass.driver_phone}', 
        f'№ пломбы/№ конт.:  {carpass.nseal} / {carpass.nkont}',
        f"Повреждение тента:                Да    {box_yes['brokenAwning']}       Нет    {box_no['brokenAwning']}",
        f"Повреждение пломбы:             Да    {box_yes['brokenSeal']}       Нет    {box_no['brokenSeal']}",
        f"Срабатывание Янтаря:             Да    {box_yes['radiation']}       Нет    {box_no['radiation']}",
    ]
    text_y = 655
    for text_line in text_lines:
        pdf.drawString(25, text_y, text_line)
        pdf.drawString(25, text_y-3, '___________________________________________')
        text_y -= 20

    pdf.drawString(25, 450, 'Ф.И.О. лица')
    pdf.drawString(25, 440, 'выдавшего пропуск')
    pdf.drawString(25, 437, '___________________________________________')
    pdf.drawString(25, 420, 'Подпись')
    pdf.drawString(25, 417, '___________________________________________')

    pdf.rect(195, 512, 12, 12); pdf.rect(247, 512, 12, 12)
    pdf.rect(195, 492, 12, 12); pdf.rect(247, 492, 12, 12)
    pdf.rect(195, 472, 12, 12); pdf.rect(247, 472, 12, 12)

    # pdf.line(30, 650, 100, 650)
    pdf.drawString(30, 652, '__________________________________________')

    # ======================================================================  ЗАЯВЛЕНИЕ
    pdf.setFont("Arial", 8); pdf.drawString(360, 810, 'НАЧАЛЬНИКУ Т/П МИХНЕВСКИЙ')
    pdf.setFont("Arial", 14); pdf.drawString(380, 780, f'ЗАЯВЛЕНИЕ')
    pdf.setFont("Arial", 7)
    pdf.drawString(330, 765, 'О ВЫДАЧЕ РАЗРЕЩЕНИЯ НА ПЕРЕМЕЩЕНИЕ ТОВАРОВ,')
    pdf.drawString(340, 755, 'ТРАНСПОРТНЫХ СРЕДСТВ ЧЕРЕЗ ГРАНИЦЫ ЗТК И ')
    pdf.drawString(340, 745, 'В ИХ ПРЕДЕЛАХ (РАЗРЕШЕНИЕ НА ПЕРЕМЕЩЕНИЕ)')
    pdf.setFont("Arial", 10)
    pdf.drawString(310, 725, 'СВЕДЕНИЯ, НЕОБХОДИМЫЕ ДЛЯ ПОЛУЧЕНИЯ')
    pdf.drawString(345, 712, 'РАЗРЕШЕНИЯ НА ПЕРЕМЕЩЕНИЕ')

    text_lines = [
        f'Фирма получатель:  {carpass.contact_name}',
        f'Номер автомашины:  {carpass.ncar}',
        f'ДТ:  {carpass.customs_doc}',
        f'Ф.И.О. водителя:  {carpass.driver_fio}',
        'Подпись',
        'Дата',
    ]
    pdf.setFont("Arial", 9)
    text_y = 690
    for text_line in text_lines:
        pdf.drawString(295, text_y, text_line)
        pdf.drawString(295, text_y-3, '_______________________________________________')
        text_y -= 20

    pdf.setFont("Arial", 9.5)
    pdf.drawString(295, 560, 'О ВЫДАЧЕ РАЗРЕЩЕНИЯ НА ПЕРЕМЕЩЕНИЕ ТОВАРОВ,')
    pdf.drawString(308, 550, 'ТРАНСПОРТНЫХ СРЕДСТВ ЧЕРЕЗ ГРАНИЦЫ ЗТК И')
    pdf.drawString(305, 540, 'В ИХ ПРЕДЕЛАХ (РАЗРЕШЕНИЕ НА ПЕРЕМЕЩЕНИЕ)')
    pdf.setFont("Arial", 11)
    pdf.drawString(390, 520, 'РАЗРЕШАЮ')
    pdf.setFont("Arial", 7)
    pdf.drawString(340, 510, 'УПОЛНОМОЧЕННОЕ ЛИЦО МИХНЕВСКОГО Т/П')
    pdf.setFont("Arial", 9); pdf.drawString(295, 490, 'Подпись')
    pdf.drawString(295, 487, '_______________________________________________')
    pdf.setFont("Arial", 7); pdf.drawString(450, 475, 'РАСШИФРОВКА')


    # creating border around block 1
    x = 20; y = 413; width = 400; height = 100; data = [['']]
    f = Table(data, colWidths=260, rowHeights=412)
    f.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 0.25, colors.black), ('FONT',(0,0),(-1,1),'Arial',10,12),]))
    f.wrapOn(pdf, width, height); f.drawOn(pdf, x, y)

    # creating border around block 2
    x = 290; y = 413; width = 400; height = 100; data = [['']]
    f = Table(data, colWidths=285, rowHeights=412)
    f.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 0.25, colors.black), ('FONT',(0,0),(-1,1),'Arial',10,12),]))
    f.wrapOn(pdf, width, height); f.drawOn(pdf, x, y)


    # pdf.drawInlineImage(image, 155, 200) #x.y
    pdf.save()






# def odl_create_document_carpass(carpass, filepath, filename):
#     # creates carpass pdf file for printing
#     title = 'Пропуск ТС на въезд'
#     subTitle = f'Рег. № ТС:  {carpass.ncar}'
#     textLines = [ 
#         f'Перевозчик:  {carpass.driver}', 
#         f'ФИО водителя:  {carpass.driver_fio}', 
#         f'Телефон водителя:  {carpass.driver_phone}', 
#         f'Номер стоянки:  {carpass.place_n}', 
#     ] 

#     # QR code creating
#     qrcode_data = f'GUID: {carpass.uuid}\n' \
#         f'Регистрационный № ТС: {carpass.ncar}\n' \
#         f'ФИО водителя: {carpass.driver_fio}\n' \
#         f'Телефон водителя: {carpass.driver_phone}\n'
#     qr = qrcode.QRCode(box_size=5)
#     qr.add_data(qrcode_data)
#     qr.make()
#     image = qr.make_image()

#     pdf = canvas.Canvas(filepath) 
#     pdf.setTitle(filename) 
#     pdfmetrics.registerFont(TTFont('Arial', 'verdana.ttf')) 
#     pdf.setFont('Arial', 30) 
#     pdf.drawCentredString(300, 770, title) 
#     # pdf.setFillColorRGB(0, 0, 255) 
#     pdf.setFont("Arial", 24) 
#     pdf.drawCentredString(290, 720, subTitle) 
#     pdf.line(30, 710, 550, 710) 
#     text = pdf.beginText(40, 680) 
#     text.setFont("Arial", 18) 
#     for line in textLines: 
#         text.textLine(line) 
#     pdf.drawText(text) 
#     pdf.drawInlineImage(image, 155, 200) #x.y
#     pdf.save()


# def create_document_exitcarpass(carpass, filepath, filename):
#     # creates exitcarpass pdf file for printing
#     title = 'Пропуск ТС на выезд'
#     subTitle = f'Рег. № ТС:  {carpass.ncar}'
#     textLines = [ 
#         f'ФИО водителя:  {carpass.drv_man}', 
#         f'Телефон водителя:  {carpass.dev_phone}', 
#         f'№ документа выпуска:  {carpass.ndexit}', 
#     ] 

#     # QR code creating
#     qrcode_data = f'GUID: {carpass.uuid}\n' \
#         f'Регистрационный № ТС: {carpass.ncar}\n' \
#         f'ФИО водителя: {carpass.drv_man}\n' \
#         f'Телефон водителя: {carpass.dev_phone}\n'
#     qr = qrcode.QRCode(box_size=5)
#     qr.add_data(qrcode_data)
#     qr.make()
#     image = qr.make_image()

#     pdf = canvas.Canvas(filepath) 
#     pdf.setTitle(filename) 
#     pdfmetrics.registerFont(TTFont('Arial', 'verdana.ttf')) 
#     pdf.setFont('Arial', 30) 
#     pdf.drawCentredString(300, 770, title) 
#     # pdf.setFillColorRGB(0, 0, 255) 
#     pdf.setFont("Arial", 24) 
#     pdf.drawCentredString(290, 720, subTitle) 
#     pdf.line(30, 710, 550, 710) 
#     text = pdf.beginText(40, 680) 
#     text.setFont("Arial", 18) 
#     for line in textLines: 
#         text.textLine(line) 
#     pdf.drawText(text) 
#     pdf.drawInlineImage(image, 155, 200) #x.y
#     pdf.save()
