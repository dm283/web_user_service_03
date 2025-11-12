# service functions
from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfbase import pdfmetrics 
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import qrcode
import PIL


def create_document_carpass(carpass, filepath, filename):
    # creates enter carpass pdf file for printing

    # QR code creating
    qrcode_data = f'GUID: {carpass.uuid}\n' \
        f'Регистрационный № ТС: {carpass.ncar}\n' \
        f'ФИО водителя: {carpass.driver_fio}\n' \
        f'Телефон водителя: {carpass.driver_phone}\n'
    qr = qrcode.QRCode(box_size=5)
    qr.add_data(qrcode_data)
    qr.make()
    qr_code_image = qr.make_image()

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


    pdf.setFont("Arial", 25); pdf.drawString(25, 300, 'НОМЕР СТОЯНКИ')
    pdf.setFont("Arial", 120); pdf.drawString(25, 150, F'{carpass.place_n}')
    pdf.drawInlineImage(qr_code_image, 265, 50) #x.y QR-code image

    pdf.showPage()
    #################################### PAGE 2

    pdf.setFont("Arial", 7); pdf.drawString(20, 820, 'Я, водитель а/м')
    pdf.setFont("Arial", 9); pdf.drawString(100, 820, f'{carpass.driver_fio}')
    text_lines = [
        '-проинформирован о месте уведомления таможенного органа о прибытии товаров и транспортных средств в место доставки.',
        '-предупрежден о том, что я обязан уведомить таможенный орган о прибытии в рабочее время не позднее 3-х.',
        'часов с момента прибытия, в нерабочее время - не позднее 3-х часов после начала работы таможенного поста.',
        '-ознакомлен с правилами поведения в зоне таможенного контроля и обязуюсь их выполнять.',
        '-знаю, что на территории ЗТК запрещено :',
        '',
        '- Приводить, привозить посторонних лиц.',
        '- Провозить, проносить и распивать спиртные напитки.',
        '- Производить ремонт, мойку автомобилей.',
        '- Создавать конфликтную ситуацию с персоналом и другими водителями.',
        '- Разбрасывать на территории мусор, остатки продуктов, кормить животных.',
        '- Пользоваться открытым огнем (готовить пищу, использовать газовые балоны, паяльные лампы).',
        '- Курение.',
        '- Самовольно перемещать а/т по ЗТК/СВХ ООО "МТС".',
        '- Справлять нужду в неположенном месте',
        '',
        'Нарушение правил СВХ влечет наложение административной ответственности в соответствии с законодательством РФ.',
        '',
        'С правилами внутреннего распорядка ознакомлен',
    ]
    pdf.setFont("Arial", 7)
    text_y = 810
    for text_line in text_lines:
        pdf.drawString(20, text_y, text_line)
        text_y -= 10
    pdf.setFont("Arial", 7); pdf.drawString(20, 610, 'Водитель ____________________________ ')
    pdf.setFont("Arial", 7); pdf.drawString(80, 603, 'подпись')
    pdf.setFont("Arial", 7); pdf.drawString(20, 580, 'Претензий не имею')
    pdf.setFont("Arial", 9); pdf.drawString(130, 580, f'{carpass.driver_fio}')
    pdf.setFont("Arial", 7); pdf.drawString(300, 580, 'подпись водителя/экспедитора')
    pdf.drawString(130, 577, '_________________________________________________________________')
    pdf.setFont("Arial", 7); pdf.drawString(20, 560, 'Подтверждение получил')
    pdf.setFont("Arial", 9); pdf.drawString(130, 560, f'{carpass.driver_fio}')
    pdf.setFont("Arial", 7); pdf.drawString(300, 560, 'подпись водителя/экспедитора')
    pdf.drawString(130, 557, '_________________________________________________________________')
    pdf.drawString(20, 540, 'Дата, время выдачи документов')
    pdf.drawString(20, 537, '__________________________________________________________')
    pdf.drawString(300, 540, 'Дата, время выезда ТС')
    pdf.drawString(300, 537, '__________________________________________________________')
    pdf.drawString(20, 520, 'Номер пломбы')
    pdf.drawString(20, 517, '__________________________________________________________')
    pdf.drawString(300, 520, 'Подпись охраны')
    pdf.drawString(300, 517, '__________________________________________________________')
    pdf.drawString(20, 500, 'Подпись ответ. лица СВХ')
    pdf.drawString(20, 497, '__________________________________________________________')
    
    # pdf.line(30, 482, 560, 482)
    # pdf.setFont("Arial", 14); pdf.drawString(230, 462, 'ПЛАН СТОЯНКИ ТС')
    # parking_map_image = PIL.Image.open('saved_files/parking-map.png')
    # pdf.drawInlineImage(parking_map_image, 20, 60, 550, 380) #x.y parking map
    

    pdf.save()
