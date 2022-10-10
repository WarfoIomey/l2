from hospitals.models import Hospitals
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, HRFlowable, Frame, PageTemplate, PageBreak, FrameBreak
from reportlab.platypus import NextPageTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm
from copy import deepcopy
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT

from results.forms.flowable import FrameData, FrameDataUniversal, FrameDataCol
from results.prepare_data import fields_result_only_title_fields
from directions.models import Issledovaniya, Napravleniya
from laboratory.settings import FONTS_FOLDER
import os.path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def form_01(direction: Napravleniya, iss: Issledovaniya, fwb, doc, leftnone, user=None):
    """
    Карта обратившегося за антирабической помощью (бывш 045/у)
    """

    # hospital: Hospitals = direction.hospital
    # hospital_name = hospital.safe_short_title
    # hospital_address = hospital.safe_address

    pdfmetrics.registerFont(TTFont('PTAstraSerifBold', os.path.join(FONTS_FOLDER, 'PTAstraSerif-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('PTAstraSerifReg', os.path.join(FONTS_FOLDER, 'PTAstraSerif-Regular.ttf')))

    styleSheet = getSampleStyleSheet()
    style = styleSheet["Normal"]
    style.fontName = "PTAstraSerifReg"
    style.fontSize = 10
    style.leading = 12
    style.spaceAfter = 0 * mm
    style.alignment = TA_JUSTIFY

    data = title_fields(iss)
    underline = '_____________________'
    text = []
    params_columns = []
    text.append(Paragraph(f'17. Осложнения во время проведения прививок: {data["17. Осложнения во время проведения прививок"]}', style))
    text.append(Paragraph('18. Курс прививок полностью закончен, отменен, так как животное оказалось здоровым, прерван самостоятельно и пр. <br/> (подчеркнуть или вписать)'
                          f'{underline}', style))

    params_columns.append({"x": -5 * mm, "y": -170 * mm, "width": 136 * mm, "height": 185 * mm, "text": text, "showBoundary": 1})


    text = []
    text.append(Paragraph('текст в вторйо колонке', style))
    params_columns.append({"x": 146 * mm, "y": -170 * mm, "width": 136 * mm, "height": 185 * mm, "text": text, "showBoundary": 1})
    fwb.append(FrameDataCol(params_columns=params_columns))
    # fwb.append(FrameBreak())
    # fwb.append(Spacer(1, 5 * mm))
    # fwb.append(FrameDataCol(columns=col_data))

    return fwb


def title_fields(iss):
    title_fields = [
        "Дата осмотра",
        "6. В какое лечебное учреждение обращался по поводу укуса и когда",
        "7. Описание повреждения и локализация его",
        "8. Сведения об укусившем, оцарапавшем, ослюнившем животном",
        "9. Обстоятельства укуса, оцарапания, ослюнения",
        "10. Бешенство животного установлено ветврачом клинически, лабораторно (подчеркнуть или вписать)",
        "11. Животное осталось здоровым, пало, убито, неизвестно (подчеркнуть или вписать)",
        "а) заболевание нервной системы",
        "б) употребляет ли спиртные напитки, как часто",
        "в) получал ли в прошлом антирабические прививки, когда, сколько",
        "г) прочие сведения",
        "13. Назначение прививки",
        "14. Назначенный режим (госпитализация, амбулаторное лечение)",
        "15. Введение антирабического гаммаглобулина: дата, серия",
        "покраснение",
        "отек",
        "Десенсибилизация",
        "Суточная доза",
        "Повторные введения",
        "17. Осложнения во время проведения прививок",
        "18. Курс прививок полностью закончен, отменен, так как животное оказалось здоровым, прерван самовольно и пр. (подчеркнуть или вписать)",
        "19. Какие приняты меры к продолжению прерванных прививок",
        "20. Примечание",
    ]

    result = fields_result_only_title_fields(iss, title_fields, False)
    data = {i['title']: i['value'] for i in result}

    for t in title_fields:
        if not data.get(t, None):
            data[t] = ""

    return data
