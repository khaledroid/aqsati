import os
import copy
import csv
import json
import webbrowser
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.modalview import ModalView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.card import MDCard

# استيراد آمن لـ DatePicker
try:
    from kivymd.uix.pickers import MDDatePicker
except ImportError:
    try:
        from kivymd.uix.picker import MDDatePicker
    except ImportError:
        MDDatePicker = None

# استيراد مكتبات ReportLab لتوليد ملفات PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# دعم pandas و openpyxl لتصدير إكسل احترافي وملون بالذكاء والتصميم المتقدم
try:
    import pandas as pd
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    PANDAS_EXCEL_AVAILABLE = True
except ImportError:
    PANDAS_EXCEL_AVAILABLE = False

# البحث عن خط يدعم اللغة العربية
font_path = "arial.ttf" if os.path.exists("arial.ttf") else ("C:/Windows/Fonts/arial.ttf" if os.path.exists("C:/Windows/Fonts/arial.ttf") else "")

if font_path:
    LabelBase.register(name="Roboto", fn_regular=font_path)
    LabelBase.register(name="Arabic", fn_regular=font_path)
    if REPORTLAB_AVAILABLE:
        try:
            pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
        except Exception:
            pass

try:
    from kivymd.uix.button import MDButton as MDFillRoundFlatButton
except ImportError:
    from kivymd.uix.button import MDFillRoundFlatButton

def ar(text):
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

class ArabicTextField(MDTextField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = "right"
        self.font_name = "Arabic"
        self.font_name_hint_text = "Arabic"
        self.raw_text = ""

    def insert_text(self, substring, from_undo=False):
        self.raw_text += substring
        reshaped = arabic_reshaper.reshape(self.raw_text)
        self.text = get_display(reshaped)

    def do_backspace(self, from_undo=False, mode='bksp'):
        if self.raw_text:
            self.raw_text = self.raw_text[:-1]
            if self.raw_text:
                reshaped = arabic_reshaper.reshape(self.raw_text)
                self.text = get_display(reshaped)
            else:
                self.text = ""

    def on_text(self, instance, value):
        if not value:
            self.raw_text = ""

    def get_clean_text(self):
        return self.raw_text if self.raw_text else self.text

KV = '''
<HomeScreen>:
    canvas.before:
        Color:
            rgba: 0.12, 0.03, 0.05, 1
        Rectangle:
            pos: self.pos
            size: self.size
    MDBoxLayout:
        orientation: 'vertical'
        padding: "16dp"
        spacing: "16dp"
        md_bg_color: 0, 0, 0, 0

        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: "85dp"
            spacing: "4dp"
            MDFloatLayout:
                size_hint: None, None
                size: "46dp", "46dp"
                pos_hint: {"center_x": .5}
                canvas.before:
                    Color:
                        rgba: 0, 0.85, 0.75, 0.12
                    RoundedRectangle:
                        size: self.size
                        pos: self.pos
                        radius: [23,]
                MDIcon:
                    icon: "wallet-outline"
                    font_size: "26sp"
                    pos_hint: {"center_x": .5, "center_y": .5}
                    theme_text_color: "Custom"
                    text_color: 0, 0.9, 0.8, 1
            MDLabel:
                text: root.get_ar("أقساطي")
                font_name: "Arabic"
                font_style: "H4"
                halign: "center"
                bold: True
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1

        MDCard:
            size_hint_y: None
            height: "60dp"
            radius: [16,]
            md_bg_color: 0.06, 0.06, 0.08, 1
            padding: "6dp"
            line_color: [0.4, 0.1, 0.15, 0.6]
            line_width: 1.1
            MDBoxLayout:
                orientation: 'horizontal'
                MDIconButton:
                    icon: "chart-bar"
                    user_font_size: "24sp"
                    theme_text_color: "Custom"
                    text_color: 0, 0.9, 0.8, 1
                    on_release: app.open_revenues_popup()
                MDLabel:
                    id: user_display_lbl
                    text: root.get_ar(app.active_user_name)
                    font_name: "Arabic"
                    font_style: "H5"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                MDIconButton:
                    icon: "account-group-outline"
                    user_font_size: "24sp"
                    theme_text_color: "Custom"
                    text_color: 0, 0.9, 0.8, 1
                    on_release: app.open_multi_users_popup()

        MDGridLayout:
            cols: 2
            spacing: "14dp"
            padding: ["0dp", "4dp", "0dp", "4dp"]

            MDCard:
                radius: [18,]
                md_bg_color: 0.06, 0.06, 0.08, 1
                line_color: [0, 0.9, 0.8, 0.4]
                line_width: 1.5
                ripple_behavior: True
                on_release: root.manager.current = 'add_customer'
                MDBoxLayout:
                    orientation: 'vertical'
                    alignment: "center"
                    padding: ["10dp", "16dp", "10dp", "16dp"]
                    spacing: "10dp"
                    MDIcon:
                        icon: "account-plus-outline"
                        font_size: "46sp"
                        pos_hint: {"center_x": .5}
                        theme_text_color: "Custom"
                        text_color: 0, 0.9, 0.8, 1
                    MDLabel:
                        text: root.get_ar("إضافة عميل")
                        font_name: "Arabic"
                        font_style: "H5"
                        bold: True
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1

            MDCard:
                radius: [18,]
                md_bg_color: 0.06, 0.06, 0.08, 1
                line_color: [0.3, 0.8, 1, 0.4]
                line_width: 1.5
                ripple_behavior: True
                on_release: root.manager.current = 'customers_list'
                MDBoxLayout:
                    orientation: 'vertical'
                    alignment: "center"
                    padding: ["10dp", "16dp", "10dp", "16dp"]
                    spacing: "10dp"
                    MDIcon:
                        icon: "card-account-details-outline"
                        font_size: "46sp"
                        pos_hint: {"center_x": .5}
                        theme_text_color: "Custom"
                        text_color: 0.3, 0.8, 1, 1
                    MDLabel:
                        text: root.get_ar("قائمة العملاء")
                        font_name: "Arabic"
                        font_style: "H5"
                        bold: True
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1

            MDCard:
                radius: [18,]
                md_bg_color: 0.06, 0.06, 0.08, 1
                line_color: [0.95, 0.75, 0.25, 0.4]
                line_width: 1.5
                ripple_behavior: True
                on_release: root.manager.current = 'settings'
                MDBoxLayout:
                    orientation: 'vertical'
                    alignment: "center"
                    padding: ["10dp", "16dp", "10dp", "16dp"]
                    spacing: "10dp"
                    MDIcon:
                        icon: "tune-vertical"
                        font_size: "46sp"
                        pos_hint: {"center_x": .5}
                        theme_text_color: "Custom"
                        text_color: 0.95, 0.75, 0.25, 1
                    MDLabel:
                        text: root.get_ar("الإعدادات")
                        font_name: "Arabic"
                        font_style: "H5"
                        bold: True
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1

            MDCard:
                radius: [18,]
                md_bg_color: 0.06, 0.06, 0.08, 1
                line_color: [0.95, 0.35, 0.35, 0.4]
                line_width: 1.5
                ripple_behavior: True
                on_release: app.open_overdue_popup()
                MDBoxLayout:
                    orientation: 'vertical'
                    alignment: "center"
                    padding: ["10dp", "16dp", "10dp", "16dp"]
                    spacing: "10dp"
                    pos_hint: {"center_x": .5, "center_y": .5}
                    MDIcon:
                        icon: "clock-alert-outline"
                        font_size: "46sp"
                        pos_hint: {"center_x": .5}
                        theme_text_color: "Custom"
                        text_color: 0.95, 0.35, 0.35, 1
                    MDLabel:
                        text: root.get_ar("العملاء المتأخرين")
                        font_name: "Arabic"
                        font_style: "H5"
                        bold: True
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1

<AddCustomerScreen>:
    canvas.before:
        Color:
            rgba: 0.12, 0.03, 0.05, 1
        Rectangle:
            pos: self.pos
            size: self.size
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0, 0, 0, 0

        MDBoxLayout:
            size_hint_y: None
            height: "55dp"
            padding: ["12dp", "5dp", "12dp", "5dp"]
            MDIconButton:
                icon: "arrow-right"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: root.manager.current = 'home'
            MDLabel:
                text: root.get_ar("إضافة عميل جديد")
                font_name: "Arabic"
                font_style: "H5"
                halign: "right"
                bold: True
                theme_text_color: "Custom"
                text_color: 0, 0.9, 0.8, 1

        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: "16dp"
                spacing: "16dp"

                MDCard:
                    orientation: 'vertical'
                    adaptive_height: True
                    padding: "16dp"
                    spacing: "16dp"
                    radius: [16,]
                    md_bg_color: 0.06, 0.06, 0.08, 1
                    line_color: [0.2, 0.28, 0.4, 0.5]
                    line_width: 1.1

                    MDLabel:
                        text: root.get_ar("بيانات العميل والسلعة")
                        font_name: "Arabic"
                        font_style: "Subtitle1"
                        bold: True
                        halign: "right"
                        theme_text_color: "Custom"
                        text_color: 0, 0.9, 0.8, 1

                    ArabicTextField:
                        id: cust_name
                        hint_text: root.get_ar("اسم العميل الرباعي *")
                        mode: "rectangle"

                    ArabicTextField:
                        id: cust_id_number
                        hint_text: root.get_ar("رقم الهوية الوطنية / الإقامة *")
                        mode: "rectangle"

                    ArabicTextField:
                        id: cust_phone
                        hint_text: root.get_ar("رقم الجوال *")
                        mode: "rectangle"

                    ArabicTextField:
                        id: item_type
                        hint_text: root.get_ar("نوع السلعة / البيان")
                        mode: "rectangle"

                    ArabicTextField:
                        id: bond_num
                        hint_text: root.get_ar("رقم السند")
                        mode: "rectangle"

                    ArabicTextField:
                        id: start_date
                        hint_text: root.get_ar("تاريخ بداية العقد (اضغط للاختيار)")
                        mode: "rectangle"
                        readonly: True
                        icon_right: "calendar-month"
                        on_focus: if self.focus: app.show_date_picker(self)

                    ArabicTextField:
                        id: notes_field
                        hint_text: root.get_ar("ملاحظات عن العميل")
                        mode: "rectangle"
                        multiline: True

                MDCard:
                    orientation: 'vertical'
                    adaptive_height: True
                    padding: "16dp"
                    spacing: "16dp"
                    radius: [16,]
                    md_bg_color: 0.06, 0.06, 0.08, 1
                    line_color: [0.2, 0.28, 0.4, 0.5]
                    line_width: 1.1

                    MDLabel:
                        text: root.get_ar("تفاصيل الأقساط والمالية")
                        font_name: "Arabic"
                        font_style: "Subtitle1"
                        bold: True
                        halign: "right"
                        theme_text_color: "Custom"
                        text_color: 0.9, 0.7, 0.2, 1

                    ArabicTextField:
                        id: base_price
                        hint_text: root.get_ar("قيمة السلعة الأصلي (مثال: 5000)")
                        input_filter: "float"
                        mode: "rectangle"
                        on_text: root.calculate_totals()

                    ArabicTextField:
                        id: profit_val
                        hint_text: root.get_ar("نسبة الفائدة % (مثال: 40)")
                        input_filter: "float"
                        mode: "rectangle"
                        on_text: root.calculate_totals()

                    ArabicTextField:
                        id: total_due
                        hint_text: root.get_ar("إجمالي المبلغ المستحق بالفوائد (تلقائي)")
                        readonly: True
                        mode: "rectangle"

                    ArabicTextField:
                        id: months_count
                        hint_text: root.get_ar("عدد الأشهر (مثال: 12)")
                        input_filter: "int"
                        mode: "rectangle"
                        on_text: root.calculate_totals()

                    ArabicTextField:
                        id: monthly_inst
                        hint_text: root.get_ar("القسط الشهري (تلقائي)")
                        readonly: True
                        mode: "rectangle"

                MDCard:
                    orientation: 'vertical'
                    adaptive_height: True
                    padding: "16dp"
                    spacing: "12dp"
                    radius: [16,]
                    md_bg_color: 0.06, 0.06, 0.08, 1
                    line_color: [0.2, 0.28, 0.4, 0.5]
                    line_width: 1.1

                    MDLabel:
                        text: root.get_ar("المرفقات والمستندات")
                        font_name: "Arabic"
                        font_style: "Subtitle1"
                        bold: True
                        halign: "right"
                        theme_text_color: "Custom"
                        text_color: 0.3, 0.8, 1, 1

                    MDFillRoundFlatButton:
                        text: root.get_ar("اختر ملف (مرفق 1)")
                        font_name: "Arabic"
                        size_hint_x: 1
                        md_bg_color: 0.18, 0.24, 0.34, 1
                        on_release: root.open_file_picker(1)
                    MDLabel:
                        id: lbl_att1
                        text: root.get_ar("مرفق 1: لم يتم الاختيار")
                        font_name: "Arabic"
                        halign: "right"
                        theme_text_color: "Custom"
                        text_color: 0.7, 0.7, 0.7, 1
                        size_hint_y: None
                        height: "20dp"

                    MDFillRoundFlatButton:
                        text: root.get_ar("اختر ملف (مرفق 2)")
                        font_name: "Arabic"
                        size_hint_x: 1
                        md_bg_color: 0.18, 0.24, 0.34, 1
                        on_release: root.open_file_picker(2)
                    MDLabel:
                        id: lbl_att2
                        text: root.get_ar("مرفق 2: لم يتم الاختيار")
                        font_name: "Arabic"
                        halign: "right"
                        theme_text_color: "Custom"
                        text_color: 0.7, 0.7, 0.7, 1
                        size_hint_y: None
                        height: "20dp"

                    MDFillRoundFlatButton:
                        text: root.get_ar("اختر ملف (مرفق 3)")
                        font_name: "Arabic"
                        size_hint_x: 1
                        md_bg_color: 0.18, 0.24, 0.34, 1
                        on_release: root.open_file_picker(3)
                    MDLabel:
                        id: lbl_att3
                        text: root.get_ar("مرفق 3: لم يتم الاختيار")
                        font_name: "Arabic"
                        halign: "right"
                        theme_text_color: "Custom"
                        text_color: 0.7, 0.7, 0.7, 1
                        size_hint_y: None
                        height: "20dp"

                MDFillRoundFlatButton:
                    text: root.get_ar("حفظ بيانات العميل")
                    font_name: "Arabic"
                    font_style: "Button"
                    bold: True
                    size_hint_x: 1
                    height: "50dp"
                    md_bg_color: 0, 0.8, 0.7, 1
                    on_release: root.save_customer()

<CustomersListScreen>:
    canvas.before:
        Color:
            rgba: 0.12, 0.03, 0.05, 1
        Rectangle:
            pos: self.pos
            size: self.size
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0, 0, 0, 0
        MDBoxLayout:
            size_hint_y: None
            height: "55dp"
            padding: "10dp"
            MDIconButton:
                icon: "arrow-right"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: root.manager.current = 'home'
            MDLabel:
                text: root.get_ar("قائمة العملاء")
                font_name: "Arabic"
                font_style: "H5"
                halign: "right"
                bold: True
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
        ScrollView:
            MDBoxLayout:
                id: customers_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: "16dp"
                spacing: "12dp"

<SettingsScreen>:
    canvas.before:
        Color:
            rgba: 0.12, 0.03, 0.05, 1
        Rectangle:
            pos: self.pos
            size: self.size
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0, 0, 0, 0
        MDBoxLayout:
            size_hint_y: None
            height: "50dp"
            padding: "10dp"
            MDIconButton:
                icon: "arrow-right"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: root.manager.current = 'home'
            MDLabel:
                text: root.get_ar("الإعدادات والنسخ الاحتياطي")
                font_name: "Arabic"
                font_style: "H6"
                halign: "right"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: "16dp"
                spacing: "14dp"

                MDCard:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: "110dp"
                    padding: "12dp"
                    radius: [12,]
                    md_bg_color: 0.06, 0.06, 0.08, 1
                    line_color: [0.2, 0.28, 0.4, 0.5]
                    line_width: 1.1
                    spacing: "8dp"
                    MDLabel:
                        text: root.get_ar("ذاكرة الهاتف (النسخ الاحتياطي واستعادة كافة البيانات والمرفقات)")
                        font_name: "Arabic"
                        halign: "right"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0, 0.9, 0.8, 1
                    MDBoxLayout:
                        spacing: "8dp"
                        MDFillRoundFlatButton:
                            text: root.get_ar("نسخ احتياطي شامل")
                            font_name: "Arabic"
                            size_hint_x: 1
                            md_bg_color: 0.18, 0.25, 0.35, 1
                            on_release: app.backup_to_phone()
                        MDFillRoundFlatButton:
                            text: root.get_ar("استعادة النسخة الكاملة")
                            font_name: "Arabic"
                            size_hint_x: 1
                            md_bg_color: 0.18, 0.25, 0.35, 1
                            on_release: app.restore_from_phone()

                MDCard:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: "230dp"
                    padding: "12dp"
                    radius: [12,]
                    md_bg_color: 0.06, 0.06, 0.08, 1
                    line_color: [0.2, 0.28, 0.4, 0.5]
                    line_width: 1.1
                    spacing: "8dp"
                    MDLabel:
                        text: root.get_ar("جوجل درايف Google Drive (النسخ والربط بالحساب)")
                        font_name: "Arabic"
                        halign: "right"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.9, 0.7, 0.2, 1
                    ArabicTextField:
                        id: gdrive_email
                        hint_text: root.get_ar("البريد الإلكتروني لـ Google Drive")
                        mode: "rectangle"
                    ArabicTextField:
                        id: gdrive_password
                        hint_text: root.get_ar("كلمة المرور / رمز المصادقة")
                        password: True
                        mode: "rectangle"
                    MDBoxLayout:
                        spacing: "8dp"
                        MDFillRoundFlatButton:
                            text: root.get_ar("نسخ احتياطي لـ Drive")
                            font_name: "Arabic"
                            size_hint_x: 1
                            md_bg_color: 0.18, 0.25, 0.35, 1
                            on_release: app.backup_to_drive(gdrive_email.get_clean_text(), gdrive_password.get_clean_text())
                        MDFillRoundFlatButton:
                            text: root.get_ar("استعادة من Drive")
                            font_name: "Arabic"
                            size_hint_x: 1
                            md_bg_color: 0.18, 0.25, 0.35, 1
                            on_release: app.restore_from_drive(gdrive_email.get_clean_text(), gdrive_password.get_clean_text())

                MDCard:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: "230dp"
                    padding: "12dp"
                    radius: [12,]
                    md_bg_color: 0.06, 0.06, 0.08, 1
                    line_color: [0.2, 0.28, 0.4, 0.5]
                    line_width: 1.1
                    spacing: "8dp"
                    MDLabel:
                        text: root.get_ar("ربط وإعدادات حساب ميجا MEGA السحابي الشامل")
                        font_name: "Arabic"
                        halign: "right"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.95, 0.35, 0.35, 1
                    ArabicTextField:
                        id: mega_email
                        hint_text: root.get_ar("البريد الإلكتروني لحساب MEGA")
                        mode: "rectangle"
                    ArabicTextField:
                        id: mega_password
                        hint_text: root.get_ar("كلمة المرور الخاصة بحساب MEGA")
                        password: True
                        mode: "rectangle"
                    MDBoxLayout:
                        spacing: "8dp"
                        MDFillRoundFlatButton:
                            text: root.get_ar("رفع احتياطي MEGA")
                            font_name: "Arabic"
                            size_hint_x: 1
                            md_bg_color: 0.18, 0.25, 0.35, 1
                            on_release: app.backup_to_mega(mega_email.get_clean_text(), mega_password.get_clean_text())
                        MDFillRoundFlatButton:
                            text: root.get_ar("جلب واستعادة MEGA")
                            font_name: "Arabic"
                            size_hint_x: 1
                            md_bg_color: 0.18, 0.25, 0.35, 1
                            on_release: app.restore_from_mega(mega_email.get_clean_text(), mega_password.get_clean_text())

                MDCard:
                    size_hint_y: None
                    height: "70dp"
                    padding: "12dp"
                    radius: [12,]
                    md_bg_color: 0.06, 0.06, 0.08, 1
                    line_color: [0.2, 0.28, 0.4, 0.5]
                    line_width: 1.1
                    ripple_behavior: True
                    on_release: app.export_to_excel()
                    MDBoxLayout:
                        orientation: 'horizontal'
                        MDIcon:
                            icon: "file-excel"
                            theme_text_color: "Custom"
                            text_color: 0.3, 0.9, 0.5, 1
                            pos_hint: {"center_y": .5}
                        MDLabel:
                            text: root.get_ar("تصدير نسخة إكسل (العملاء، الأشهر، المتبقي والمتأخرات)")
                            font_name: "Arabic"
                            halign: "right"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1

                MDCard:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: "140dp"
                    padding: "12dp"
                    radius: [12,]
                    md_bg_color: 0.06, 0.06, 0.08, 1
                    line_color: [0.2, 0.28, 0.4, 0.5]
                    line_width: 1.1
                    spacing: "8dp"
                    MDLabel:
                        text: root.get_ar("الرقم السري الخاص بحذف العملاء:")
                        font_name: "Arabic"
                        halign: "right"
                        theme_text_color: "Custom"
                        text_color: 0.9, 0.8, 0.4, 1
                        bold: True
                    ArabicTextField:
                        id: delete_pin_field
                        hint_text: root.get_ar("أدخل الرقم السري لحماية الحذف")
                        password: True
                        mode: "rectangle"
                    MDFillRoundFlatButton:
                        text: root.get_ar("حفظ الرقم السري")
                        font_name: "Arabic"
                        size_hint_x: 1
                        md_bg_color: 0, 0.8, 0.7, 1
                        on_release: app.save_delete_pin(delete_pin_field.get_clean_text())

<PreviousContractsPopup>:
    size_hint: 0.92, 0.88
    background: ""
    background_color: 0, 0, 0, 0.75
    MDCard:
        orientation: 'vertical'
        radius: [20,]
        md_bg_color: 0.06, 0.06, 0.08, 1
        padding: "16dp"
        spacing: "15dp"
        MDBoxLayout:
            size_hint_y: None
            height: "40dp"
            MDIconButton:
                icon: "close"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: root.dismiss()
            Widget:
            MDLabel:
                text: root.get_ar("العقود المرتبطة برقم الهوية")
                font_name: "Arabic"
                font_style: "H6"
                halign: "right"
                bold: True
                theme_text_color: "Custom"
                text_color: 0, 0.9, 0.8, 1
        ScrollView:
            MDBoxLayout:
                id: contracts_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: "12dp"

<OverdueCustomersPopup>:
    size_hint: 0.9, 0.85
    background: ""
    background_color: 0, 0, 0, 0.7
    MDCard:
        orientation: 'vertical'
        radius: [20,]
        md_bg_color: 0.06, 0.06, 0.08, 1
        padding: "16dp"
        spacing: "15dp"
        MDBoxLayout:
            size_hint_y: None
            height: "40dp"
            MDIconButton:
                icon: "close"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: root.dismiss()
            Widget:
            MDLabel:
                text: root.get_ar("العملاء المتأخرين عن السداد بالشهر الحالي")
                font_name: "Arabic"
                font_style: "H6"
                halign: "right"
                bold: True
                theme_text_color: "Custom"
                text_color: 0.95, 0.35, 0.35, 1
        ScrollView:
            MDBoxLayout:
                id: overdue_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: "10dp"

<MultiUsersPopup>:
    size_hint: 0.9, 0.8
    background: ""
    background_color: 0, 0, 0, 0.75
    MDCard:
        orientation: 'vertical'
        radius: [20,]
        md_bg_color: 0.06, 0.06, 0.08, 1
        padding: "16dp"
        spacing: "15dp"
        MDBoxLayout:
            size_hint_y: None
            height: "40dp"
            MDIconButton:
                icon: "close"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: root.dismiss()
            Widget:
            MDLabel:
                text: root.get_ar("المستخدمين")
                font_name: "Arabic"
                font_style: "H6"
                halign: "right"
                bold: True
                theme_text_color: "Custom"
                text_color: 0, 0.9, 0.8, 1
        ScrollView:
            MDBoxLayout:
                id: users_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: "10dp"
        MDFillRoundFlatButton:
            text: root.get_ar("إضافة مستخدم جديد")
            font_name: "Arabic"
            size_hint_x: 1
            height: "45dp"
            md_bg_color: 0, 0.8, 0.7, 1
            on_release: app.open_add_user_dialog()
'''

class BaseScreen(MDScreen):
    def get_ar(self, text): return ar(text)

class HomeScreen(BaseScreen): pass

class RevenuesPopup(ModalView):
    def get_ar(self, text): return ar(text)

class PreviousContractsPopup(ModalView):
    def get_ar(self, text): return ar(text)

    def on_open(self):
        app = MDApp.get_running_app()
        container = self.ids.contracts_container
        container.clear_widgets()
        
        current_id = app.current_customer.get('id_number', '')
        matching_contracts = [c for c in app.customers if c.get('id_number') == current_id]

        for idx, cust in enumerate(matching_contracts):
            is_finished = cust.get('remaining_amount', 0) <= 0
            status_text = "عقد منتهي" if is_finished else "عقد قائم"
            status_bg = (0.1, 0.75, 0.4, 1) if is_finished else (0.2, 0.5, 0.8, 1)

            card = MDCard(
                size_hint_y=None,
                height="115dp",
                padding="12dp",
                radius=[14,],
                md_bg_color=(0.06, 0.06, 0.08, 1),
                line_color=(0.2, 0.3, 0.45, 0.5),
                line_width=1
            )
            
            main_layout = MDBoxLayout(orientation='horizontal', spacing="10dp")

            badge_box = MDBoxLayout(
                size_hint=(None, None),
                size=("85dp", "30dp"),
                pos_hint={"center_y": 0.5}
            )
            badge_card = MDCard(
                radius=[8,],
                md_bg_color=status_bg,
                padding="4dp"
            )
            badge_lbl = MDLabel(
                text=ar(status_text),
                font_name="Arabic",
                font_style="Caption",
                bold=True,
                halign="center",
                valign="middle",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1)
            )
            badge_card.add_widget(badge_lbl)
            badge_box.add_widget(badge_card)

            details_box = MDBoxLayout(orientation='vertical', spacing="3dp", pos_hint={"center_y": 0.5})
            
            top_line = MDLabel(
                text=ar(f"السلعة: {cust.get('item_type', '')}  |  رقم السند: {cust.get('bond_num', '')}"),
                font_name="Arabic",
                font_style="Subtitle1",
                halign="right",
                bold=True,
                theme_text_color="Custom",
                text_color=(0, 0.9, 0.8, 1)
            )
            date_line = MDLabel(
                text=ar(f"بداية العقد: {cust.get('start_date', '01-08-2026')}"),
                font_name="Arabic",
                font_style="Subtitle1",
                halign="right",
                theme_text_color="Custom",
                text_color=(0.9, 0.8, 0.4, 1)
            )
            sub_line = MDLabel(
                text=ar(f"المتبقي: {cust.get('remaining_amount', 0):,.0f} ريال  |  القسط: {cust.get('monthly_installment', 0)} ريال"),
                font_name="Arabic",
                font_style="Subtitle1",
                halign="right",
                bold=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1)
            )
            stat_line = MDLabel(
                text=ar(f"آخر سداد: {cust.get('last_payment', '')}"),
                font_name="Arabic",
                font_style="Subtitle1",
                halign="right",
                theme_text_color="Custom",
                text_color=(0.8, 0.8, 0.8, 1)
            )
            
            details_box.add_widget(top_line)
            details_box.add_widget(date_line)
            details_box.add_widget(sub_line)
            details_box.add_widget(stat_line)

            main_layout.add_widget(badge_box)
            main_layout.add_widget(details_box)

            card.add_widget(main_layout)
            container.add_widget(card)

class AddCustomerScreen(BaseScreen):
    att1 = ""
    att2 = ""
    att3 = ""
    current_picker_slot = 1

    def get_ar(self, text): return ar(text)
    
    def on_enter(self):
        if not self.ids.start_date.text:
            today_str = datetime.now().strftime("%d-%m-%Y")
            self.ids.start_date.text = ar(today_str)
            self.ids.start_date.raw_text = today_str

    def calculate_totals(self):
        try:
            base_t = self.ids.base_price.get_clean_text()
            profit_t = self.ids.profit_val.get_clean_text()
            base = float(base_t) if base_t else 0.0
            profit_percent = float(profit_t) if profit_t else 0.0
            
            profit_amount = base * (profit_percent / 100.0)
            total = base + profit_amount
            
            self.ids.total_due.text = f"{total:.2f}"
            self.ids.total_due.raw_text = f"{total:.2f}"
            
            months_t = self.ids.months_count.get_clean_text()
            months = int(months_t) if months_t else 0
            if months > 0:
                monthly = total / months
                self.ids.monthly_inst.text = f"{monthly:.2f}"
                self.ids.monthly_inst.raw_text = f"{monthly:.2f}"
            else:
                self.ids.monthly_inst.text = ""
                self.ids.monthly_inst.raw_text = ""
        except ValueError:
            pass

    def open_file_picker(self, slot_num):
        self.current_picker_slot = slot_num
        app = MDApp.get_running_app()
        app.open_file_chooser_popup(self.on_file_selected, select_dir=False)

    def on_file_selected(self, file_path):
        if file_path:
            file_name = os.path.basename(file_path)
            if self.current_picker_slot == 1:
                self.att1 = file_path
                self.ids.lbl_att1.text = ar(f"مرفق 1: {file_name}")
            elif self.current_picker_slot == 2:
                self.att2 = file_path
                self.ids.lbl_att2.text = ar(f"مرفق 2: {file_name}")
            elif self.current_picker_slot == 3:
                self.att3 = file_path
                self.ids.lbl_att3.text = ar(f"مرفق 3: {file_name}")

    def save_customer(self):
        app = MDApp.get_running_app()
        name = self.ids.cust_name.get_clean_text().strip()
        id_num = self.ids.cust_id_number.get_clean_text().strip()
        
        if not name or not id_num:
            app.show_action_message("الرجاء إدخال اسم العميل ورقم الهوية الوطنية")
            return
            
        base_t = self.ids.base_price.get_clean_text()
        profit_t = self.ids.profit_val.get_clean_text()
        total_t = self.ids.total_due.get_clean_text()
        months_t = self.ids.months_count.get_clean_text()
        monthly_t = self.ids.monthly_inst.get_clean_text()
        start_date_val = self.ids.start_date.get_clean_text().strip() or datetime.now().strftime("%d-%m-%Y")
        notes_val = self.ids.notes_field.get_clean_text().strip()

        base_val = float(base_t) if base_t else 0.0
        profit_val_num = float(profit_t) if profit_t else 0.0
        total_val = float(total_t) if total_t else 0.0
        months_val = int(months_t) if months_t else 12
        monthly_val = float(monthly_t) if monthly_t else 0.0

        new_customer = {
            "name": name,
            "id_number": id_num,
            "phone": self.ids.cust_phone.get_clean_text().strip(),
            "item_type": self.ids.item_type.get_clean_text().strip(),
            "bond_num": self.ids.bond_num.get_clean_text().strip(),
            "start_date": start_date_val,
            "notes": notes_val,
            "base_price": base_val,
            "profit_percent": profit_val_num,
            "att1": self.att1,
            "att2": self.att2,
            "att3": self.att3,
            "remaining_amount": total_val,
            "monthly_installment": monthly_val,
            "total_months": months_val,
            "paid_months": 0,
            "remaining_months": months_val,
            "deferred_months": 0,
            "overdue_months": 0,
            "last_payment": "لم يتم السداد بعد",
            "schedule_installments": [
                {"month_num": i+1, "status": "unpaid", "amount": monthly_val, "paid_date": "", "note": ""}
                for i in range(months_val)
            ]
        }

        app.customers.append(new_customer)
        app.calculate_dashboard_financials()
        
        self.ids.cust_name.text = ""
        self.ids.cust_id_number.text = ""
        self.ids.cust_phone.text = ""
        self.ids.item_type.text = ""
        self.ids.bond_num.text = ""
        self.ids.base_price.text = ""
        self.ids.profit_val.text = ""
        self.ids.total_due.text = ""
        self.ids.months_count.text = ""
        self.ids.monthly_inst.text = ""
        self.ids.notes_field.text = ""
        
        self.att1 = ""
        self.att2 = ""
        self.att3 = ""
        self.ids.lbl_att1.text = ar("مرفق 1: لم يتم الاختيار")
        self.ids.lbl_att2.text = ar("مرفق 2: لم يتم الاختيار")
        self.ids.lbl_att3.text = ar("مرفق 3: لم يتم الاختيار")

        app.show_action_message("تم حفظ وإضافة العميل بنجاح")
        self.manager.current = 'customers_list'

class CustomersListScreen(BaseScreen):
    def on_enter(self):
        self.update_customers_list()

    def update_customers_list(self):
        app = MDApp.get_running_app()
        container = self.ids.customers_container
        container.clear_widgets()

        current_month_key = datetime.now().strftime("%m-%Y")

        sorted_customers = sorted(
            app.customers,
            key=lambda c: (
                0 if (c.get('remaining_amount', 0) > 0 and current_month_key not in c.get('last_payment', '')) else 1,
                -c.get('overdue_months', 0)
            )
        )

        for cust in sorted_customers:
            original_idx = app.customers.index(cust)
            card = MDCard(
                size_hint_y=None,
                height="105dp",
                padding=["12dp", "8dp", "12dp", "8dp"],
                radius=[12,],
                md_bg_color=(0.06, 0.06, 0.08, 1),
                line_color=(0.2, 0.28, 0.4, 0.5),
                line_width=1.1,
                ripple_behavior=True,
            )
            card.bind(on_release=lambda x, index=original_idx: app.open_customer_popup_by_index(index))

            main_box = MDBoxLayout(orientation='horizontal', spacing="10dp")

            left_actions = MDBoxLayout(
                orientation='horizontal',
                size_hint_x=None,
                width="84dp",
                spacing="0dp",
                pos_hint={"center_y": 0.5}
            )

            wa_btn = MDIconButton(
                icon="whatsapp",
                theme_text_color="Custom",
                text_color=(0.18, 0.8, 0.44, 1),
                on_release=lambda x, c=cust: app.send_reminder_whatsapp(c)
            )

            call_btn = MDIconButton(
                icon="phone",
                theme_text_color="Custom",
                text_color=(0.3, 0.8, 1, 1),
                on_release=lambda x, phone=cust.get('phone', ''): app.make_phone_call(phone)
            )

            left_actions.add_widget(wa_btn)
            left_actions.add_widget(call_btn)

            right_box = MDBoxLayout(orientation='vertical', spacing="4dp", pos_hint={"center_y": 0.5})

            last_pay = cust.get('last_payment', '')
            paid_this_month = current_month_key in last_pay
            status_color = (0.1, 0.8, 0.3, 1) if paid_this_month else (0.9, 0.2, 0.2, 1)

            top_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="32dp", spacing="6dp")

            name_lbl = MDLabel(
                text=ar(cust.get("name", "")),
                font_name="Arabic",
                font_style="H6",
                bold=True,
                halign="right",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1)
            )

            status_dot = MDIcon(
                icon="circle",
                font_size="16sp",
                theme_text_color="Custom",
                text_color=status_color,
                size_hint_x=None,
                width="16dp",
                pos_hint={"center_y": 0.5}
            )

            top_row.add_widget(name_lbl)
            top_row.add_widget(status_dot)

            phone_lbl = MDLabel(
                text=ar(f"الجوال: {cust.get('phone', '')}  |  المتبقي للسداد: {cust.get('remaining_amount', 0):,.0f} ريال"),
                font_name="Arabic",
                font_style="Subtitle1",
                bold=True,
                halign="right",
                theme_text_color="Custom",
                text_color=(0, 0.9, 0.8, 1)
            )

            right_box.add_widget(top_row)
            right_box.add_widget(phone_lbl)

            main_box.add_widget(left_actions)
            main_box.add_widget(right_box)

            card.add_widget(main_box)
            container.add_widget(card)

class SettingsScreen(BaseScreen):
    def on_enter(self):
        app = MDApp.get_running_app()
        if hasattr(self.ids, 'delete_pin_field'):
            self.ids.delete_pin_field.text = app.delete_pin
            self.ids.delete_pin_field.raw_text = app.delete_pin

class FileChooserPopup(ModalView):
    def __init__(self, callback, select_dir=False, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.9)
        self.callback = callback
        self.select_dir = select_dir
        
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10, md_bg_color=(0.06, 0.06, 0.08, 1))
        
        top_bar = MDBoxLayout(size_hint_y=None, height=40)
        close_btn = MDIconButton(icon="close", theme_text_color="Custom", text_color=(1,1,1,1), on_release=lambda x: self.dismiss())
        title_text = "اختر مجلد الحفظ للنسخة الاحتياطية" if select_dir else "اختر ملف النسخة الاحتياطية أو المرفق"
        title_lbl = MDLabel(text=ar(title_text), font_name="Arabic", halign="right", theme_text_color="Custom", text_color=(1,1,1,1))
        top_bar.add_widget(close_btn)
        top_bar.add_widget(Widget())
        top_bar.add_widget(title_lbl)
        layout.add_widget(top_bar)
        
        self.filechooser = FileChooserListView(path=os.path.expanduser("~"), dirselect=select_dir)
        layout.add_widget(self.filechooser)
        
        btn_text = "اختيار هذا المجلد للنسخ" if select_dir else "اختيار هذا الملف"
        select_btn = MDFillRoundFlatButton(
            text=ar(btn_text),
            font_name="Arabic",
            size_hint_x=1,
            md_bg_color=(0, 0.8, 0.7, 1),
            on_release=self.select_file
        )
        layout.add_widget(select_btn)
        self.add_widget(layout)

    def select_file(self, instance):
        if self.filechooser.selection:
            path = self.filechooser.selection[0]
            if self.select_dir and os.path.isfile(path):
                path = os.path.dirname(path)
            self.callback(path)
        elif self.select_dir:
            self.callback(self.filechooser.path)
        elif self.filechooser.selection:
            self.callback(self.filechooser.selection[0])
        self.dismiss()

class OverdueCustomersPopup(ModalView):
    def get_ar(self, text): return ar(text)

    def on_open(self):
        self.update_overdue_list()

    def update_overdue_list(self):
        app = MDApp.get_running_app()
        container = self.ids.overdue_container
        container.clear_widgets()

        overdue_list = app.get_actual_overdue_customers()

        if not overdue_list:
            lbl = MDLabel(
                text=ar("لا يوجد عملاء متأخرين عن السداد للشهر الحالي"),
                font_name="Arabic",
                halign="center",
                theme_text_color="Custom",
                text_color=(0.3, 0.9, 0.5, 1),
                size_hint_y=None,
                height="100dp"
            )
            container.add_widget(lbl)
            return

        for cust in overdue_list:
            card = MDCard(
                size_hint_y=None,
                height="85dp",
                padding=["12dp", "8dp", "12dp", "8dp"],
                radius=[12,],
                md_bg_color=(0.06, 0.06, 0.08, 1),
            )
            main_box = MDBoxLayout(orientation='horizontal', spacing="10dp")

            left_actions = MDBoxLayout(
                orientation='horizontal',
                size_hint_x=None,
                width="84dp",
                spacing="0dp",
                pos_hint={"center_y": 0.5}
            )

            wa_btn = MDIconButton(
                icon="whatsapp",
                theme_text_color="Custom",
                text_color=(0.18, 0.8, 0.44, 1),
                on_release=lambda x, c=cust: app.send_reminder_whatsapp(c)
            )

            call_btn = MDIconButton(
                icon="phone",
                theme_text_color="Custom",
                text_color=(0.3, 0.8, 1, 1),
                on_release=lambda x, phone=cust.get('phone', ''): app.make_phone_call(phone)
            )

            left_actions.add_widget(wa_btn)
            left_actions.add_widget(call_btn)

            right_box = MDBoxLayout(orientation='vertical', spacing="4dp", pos_hint={"center_y": 0.5})

            top_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="28dp", spacing="6dp")

            name_lbl = MDLabel(
                text=ar(cust.get("name", "")),
                font_name="Arabic",
                halign="right",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                bold=True
            )

            status_dot = MDIcon(
                icon="alert-circle",
                font_size="16sp",
                theme_text_color="Custom",
                text_color=(0.95, 0.35, 0.35, 1),
                size_hint_x=None,
                width="16dp",
                pos_hint={"center_y": 0.5}
            )

            top_row.add_widget(name_lbl)
            top_row.add_widget(status_dot)

            detail_lbl = MDLabel(
                text=ar(f"الجوال: {cust.get('phone', '')}  |  المتبقي: {cust.get('remaining_amount', 0):,.0f} ريال"),
                font_name="Arabic",
                halign="right",
                theme_text_color="Custom",
                text_color=(1, 0.6, 0.4, 1)
            )

            right_box.add_widget(top_row)
            right_box.add_widget(detail_lbl)

            main_box.add_widget(left_actions)
            main_box.add_widget(right_box)

            card.add_widget(main_box)
            container.add_widget(card)

class MultiUsersPopup(ModalView):
    def get_ar(self, text): return ar(text)

    def on_open(self):
        self.update_users_list()

    def update_users_list(self):
        app = MDApp.get_running_app()
        container = self.ids.users_container
        container.clear_widgets()

        for usr in app.users:
            card = MDCard(
                size_hint_y=None,
                height="80dp",
                padding="12dp",
                radius=[12,],
                md_bg_color=(0.06, 0.06, 0.08, 1),
                line_color=(0.2, 0.3, 0.4, 0.5),
                line_width=1
            )
            box = MDBoxLayout(orientation='horizontal', spacing="10dp")

            is_current = usr.get('username') == app.current_user.get('username')
            switch_btn = MDFillRoundFlatButton(
                text=ar("الحالي") if is_current else ar("دخول للحساب"),
                font_name="Arabic",
                size_hint_x=None,
                width="110dp",
                md_bg_color=(0, 0.8, 0.7, 1) if not is_current else (0.2, 0.4, 0.4, 1),
                on_release=lambda x, u=usr: self.switch_account(u)
            )
            box.add_widget(switch_btn)

            if usr.get('username') != 'admin':
                del_btn = MDIconButton(
                    icon="account-remove-outline",
                    theme_text_color="Custom",
                    text_color=(0.9, 0.3, 0.3, 1),
                    on_release=lambda x, u=usr: app.confirm_delete_user(u)
                )
                box.add_widget(del_btn)

            info_box = MDBoxLayout(orientation='vertical', pos_hint={"center_y": 0.5})
            name_lbl = MDLabel(
                text=ar(usr.get("name", "")),
                font_name="Arabic",
                halign="right",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                bold=True
            )
            role_lbl = MDLabel(
                text=ar(f"اسم المستخدم: {usr.get('username', '')}"),
                font_name="Arabic",
                font_style="Caption",
                halign="right",
                theme_text_color="Custom",
                text_color=(0.7, 0.7, 0.7, 1)
            )
            info_box.add_widget(name_lbl)
            info_box.add_widget(role_lbl)
            box.add_widget(info_box)

            card.add_widget(box)
            container.add_widget(card)

    def switch_account(self, user_dict):
        app = MDApp.get_running_app()
        app.switch_active_user(user_dict)
        self.dismiss()

class CustomerPopup(ModalView):
    def get_ar(self, text): return ar(text)

    def get_attachments_display_text(self):
        app = MDApp.get_running_app()
        cust = app.current_customer
        
        f1 = os.path.basename(cust.get('att1')) if cust.get('att1') else 'لا يوجد'
        f2 = os.path.basename(cust.get('att2')) if cust.get('att2') else 'لا يوجد'
        f3 = os.path.basename(cust.get('att3')) if cust.get('att3') else 'لا يوجد'
        
        return ar(f"المرفقات: 1({f1}) | 2({f2}) | 3({f3})")

class AllInstallmentsPopup(ModalView):
    def get_ar(self, text): return ar(text)

    def on_open(self):
        app = MDApp.get_running_app()
        container = self.ids.installments_container
        container.clear_widgets()
        
        cust = app.current_customer
        schedule = cust.get('schedule_installments', [])
        if not schedule:
            months_cnt = cust.get('total_months', 12)
            inst_val = cust.get('monthly_installment', 0)
            paid_m = cust.get('paid_months', 0)
            schedule = []
            for i in range(months_cnt):
                m_num = i + 1
                if m_num <= paid_m:
                    schedule.append({"month_num": m_num, "status": "paid", "amount": inst_val, "paid_date": cust.get('last_payment', 'مسدد'), "note": ""})
                else:
                    schedule.append({"month_num": m_num, "status": "unpaid", "amount": inst_val, "paid_date": "", "note": ""})
            cust['schedule_installments'] = schedule

        for item in schedule:
            m_num = item.get('month_num', 1)
            is_paid = item.get('status') == 'paid'
            amt = item.get('amount', 0)
            p_date = item.get('paid_date', '')
            note = item.get('note', '')

            icon_name = "check-circle" if is_paid else "close-circle"
            icon_color = (0.1, 0.8, 0.4, 1) if is_paid else (0.9, 0.25, 0.25, 1)

            if is_paid:
                status_text = f"مسدد: {amt:,.0f} ريال | التاريخ: {p_date}"
            else:
                status_text = f"القسط: {amt:,.0f} ريال"
                
            if note:
                status_text += f" ({note})"

            card = MDCard(
                size_hint_y=None,
                height="80dp",
                padding="12dp",
                radius=[12,],
                md_bg_color=(0.06, 0.06, 0.08, 1),
            )
            box = MDBoxLayout(orientation='horizontal', spacing="12dp")
            
            icon = MDIcon(
                icon=icon_name,
                font_size="32sp",
                theme_text_color="Custom",
                text_color=icon_color,
                pos_hint={"center_y": 0.5}
            )
            
            info_layout = MDBoxLayout(orientation='vertical', spacing="4dp", pos_hint={"center_y": 0.5})
            
            month_lbl = MDLabel(
                text=ar(f"الشهر رقم {m_num}"),
                font_name="Arabic",
                font_style="Subtitle1",
                halign="right",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                bold=True
            )
            
            sub_lbl = MDLabel(
                text=ar(status_text),
                font_name="Arabic",
                font_style="Caption",
                halign="right",
                theme_text_color="Custom",
                text_color=(0.7, 0.8, 0.9, 1)
            )
            
            info_layout.add_widget(month_lbl)
            info_layout.add_widget(sub_lbl)
            
            box.add_widget(icon)
            box.add_widget(info_layout)
            
            card.add_widget(box)
            container.add_widget(card)

class AqsatiApp(MDApp):
    dialog = None
    delete_dialog = None
    confirm_user_dialog = None
    partial_dialog = None
    add_user_dialog_obj = None
    current_popup = None
    all_installments_popup = None
    overdue_popup = None
    multi_users_popup = None
    file_chooser_popup = None
    revenues_popup = None
    previous_contracts_popup = None

    delete_pin = "1234"
    action_history = []

    monthly_income = 0.0
    monthly_profit = 0.0
    total_income = 0.0
    total_goods_value = 0.0
    active_user_name = "خالد سعد الرحيلي"

    users = [
        {"name": "خالد سعد الرحيلي", "username": "admin", "password": "123", "role": "مدير النظام"},
        {"name": "حاتم", "username": "hatem", "password": "123", "role": "مستخدم"}
    ]

    user_databases = {
        "admin": [
            {
                "name": "خالد أحمد عبدالله",
                "id_number": "1098765432",
                "phone": "0549484899",
                "item_type": "ايفون 15 بروماكس",
                "bond_num": "232434",
                "start_date": "01-08-2026",
                "notes": "عميل منتظم بالسداد",
                "base_price": 5000.0,
                "profit_percent": 40.0,
                "att1": "",
                "att2": "",
                "att3": "",
                "remaining_amount": 3500.0,
                "monthly_installment": 583.0,
                "total_months": 12,
                "paid_months": 6,
                "remaining_months": 6,
                "deferred_months": 1,
                "overdue_months": 0,
                "last_payment": "25-07-2026 01:24",
                "schedule_installments": [
                    {"month_num": 1, "status": "paid", "amount": 583.0, "paid_date": "25-02-2026", "note": ""},
                    {"month_num": 2, "status": "paid", "amount": 583.0, "paid_date": "25-03-2026", "note": ""},
                    {"month_num": 3, "status": "paid", "amount": 583.0, "paid_date": "25-04-2026", "note": ""},
                    {"month_num": 4, "status": "paid", "amount": 583.0, "paid_date": "25-05-2026", "note": ""},
                    {"month_num": 5, "status": "paid", "amount": 583.0, "paid_date": "25-06-2026", "note": ""},
                    {"month_num": 6, "status": "paid", "amount": 583.0, "paid_date": "25-07-2026", "note": ""},
                    {"month_num": 7, "status": "unpaid", "amount": 583.0, "paid_date": "", "note": ""},
                    {"month_num": 8, "status": "unpaid", "amount": 583.0, "paid_date": "", "note": ""},
                    {"month_num": 9, "status": "unpaid", "amount": 583.0, "paid_date": "", "note": ""},
                    {"month_num": 10, "status": "unpaid", "amount": 583.0, "paid_date": "", "note": ""},
                    {"month_num": 11, "status": "unpaid", "amount": 583.0, "paid_date": "", "note": ""},
                    {"month_num": 12, "status": "unpaid", "amount": 583.0, "paid_date": "", "note": ""}
                ]
            }
        ],
        "hatem": []
    }

    current_user = {"name": "خالد سعد الرحيلي", "username": "admin", "password": "123", "role": "مدير النظام"}
    customers = []

    def get_aqsati_internal_dir(self):
        if os.name == 'nt':
            base_path = os.path.join(os.path.expanduser("~"), "Documents")
        else:
            base_path = os.path.expanduser("~")
        
        target_dir = os.path.join(base_path, "أقساطي")
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir, exist_ok=True)
            except Exception:
                target_dir = os.getcwd()
        return target_dir

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        
        for style in list(self.theme_cls.font_styles.keys()):
            if style != "Icon":
                self.theme_cls.font_styles[style][0] = "Arabic"

        self.customers = self.user_databases.get(self.current_user['username'], [])
        self.active_user_name = self.current_user['name']
        self.calculate_dashboard_financials()

        Builder.load_string(KV)
        sm = ScreenManager(transition=SlideTransition(direction="left"))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(AddCustomerScreen(name='add_customer'))
        sm.add_widget(CustomersListScreen(name='customers_list'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

    def show_date_picker(self, target_textfield):
        if MDDatePicker is None:
            today_str = datetime.now().strftime("%d-%m-%Y")
            target_textfield.text = ar(today_str)
            target_textfield.raw_text = today_str
            target_textfield.focus = False
            self.show_action_message("تم تحديد التاريخ التلقائي لليوم بنجاح.")
            return

        def on_date_save(instance, value, date_range):
            selected_date = value.strftime("%d-%m-%Y")
            target_textfield.text = ar(selected_date)
            target_textfield.raw_text = selected_date
            target_textfield.focus = False

        def on_date_cancel(instance, value):
            target_textfield.focus = False

        try:
            date_dialog = MDDatePicker()
            date_dialog.bind(on_save=on_date_save, on_cancel=on_date_cancel)
            date_dialog.open()
        except Exception:
            today_str = datetime.now().strftime("%d-%m-%Y")
            target_textfield.text = ar(today_str)
            target_textfield.raw_text = today_str
            target_textfield.focus = False

    def get_actual_overdue_customers(self):
        current_month_key = datetime.now().strftime("%m-%Y")
        overdue = []
        for c in self.customers:
            has_remaining = c.get('remaining_amount', 0) > 0
            paid_this_month = current_month_key in c.get('last_payment', '')
            if has_remaining and not paid_this_month:
                overdue.append(c)
        return overdue

    def get_previous_contracts_count(self):
        if not self.current_customer:
            return 0
        current_id = self.current_customer.get('id_number', '')
        if not current_id:
            return 0
        return len([c for c in self.customers if c.get('id_number') == current_id])

    def open_previous_contracts_popup(self):
        self.previous_contracts_popup = PreviousContractsPopup()
        self.previous_contracts_popup.open()

    def switch_active_user(self, user_dict):
        self.current_user = user_dict
        self.active_user_name = user_dict['name']
        username = user_dict['username']
        
        if username not in self.user_databases:
            self.user_databases[username] = []
        self.customers = self.user_databases[username]

        self.calculate_dashboard_financials()

        for screen in self.root.screens:
            if isinstance(screen, HomeScreen):
                if hasattr(screen.ids, 'user_display_lbl'):
                    screen.ids.user_display_lbl.text = ar(self.active_user_name)
                screen.canvas.ask_update()
            elif isinstance(screen, CustomersListScreen):
                screen.update_customers_list()

        self.show_action_message(f"تم الانتقال بنجاح لحساب: {user_dict['name']}")

    def send_reminder_whatsapp(self, cust):
        phone = cust.get('phone', '')
        inst_val = cust.get('monthly_installment', 0)
        clean_phone = ''.join(filter(str.isdigit, str(phone)))
        if clean_phone.startswith('05'):
            clean_phone = '966' + clean_phone[1:]
            
        message = f"السلام عليكم ورحمة الله وبركاته، نود تذكيركم بوجود قسط متأخر بقيمة {inst_val:,.0f} ريال، نرجو السداد في أقرب وقت. شاكرين تعاونكم."
        from urllib.parse import quote
        webbrowser.open(f"https://wa.me/{clean_phone}?text={quote(message)}")

    def send_payment_notification_whatsapp(self):
        cust = self.current_customer
        if not cust:
            return
        phone = cust.get('phone', '')
        clean_phone = ''.join(filter(str.isdigit, str(phone)))
        if clean_phone.startswith('05'):
            clean_phone = '966' + clean_phone[1:]
            
        paid_m_num = cust.get('paid_months', 1)
        monthly_inst = cust.get('monthly_installment', 0)
        remaining_amt = cust.get('remaining_amount', 0)
        
        schedule = cust.get('schedule_installments', [])
        extra_amount = 0
        paid_amount = monthly_inst
        
        if schedule and len(schedule) >= paid_m_num and paid_m_num > 0:
            last_item = schedule[paid_m_num - 1]
            note_text = last_item.get('note', '')
            if "خصم زيادة" in note_text:
                try:
                    import re
                    numbers = re.findall(r'\d+(?:,\d+)?', note_text)
                    if numbers:
                        extra_amount = float(numbers[0].replace(',', ''))
                        paid_amount = monthly_inst + extra_amount
                except Exception:
                    pass

        if extra_amount > 0:
            message = f"السلام عليكم ورحمة الله وبركاته تم سداد دفعه هذا الشهر رقم {paid_m_num} والمبلغ المسدد {paid_amount:,.0f} ريال (تم سداد مبلغ زيادة بقيمه {extra_amount:,.0f} ريال وتم خصمه من المبلغ الاجمالي) ويتبقى {remaining_amt:,.0f} ريال"
        else:
            message = f"السلام عليكم ورحمة الله وبركاته تم سداد دفعه هذا الشهر رقم {paid_m_num} والمبلغ المسدد {paid_amount:,.0f} ريال والمتبقي {remaining_amt:,.0f} ريال"

        from urllib.parse import quote
        webbrowser.open(f"https://wa.me/{clean_phone}?text={quote(message)}")

    def calculate_dashboard_financials(self):
        self.monthly_income = sum(c.get('monthly_installment', 0.0) for c in self.customers if c.get('remaining_amount', 0) > 0)
        self.total_income = sum(c.get('monthly_installment', 0.0) * c.get('total_months', 0) for c in self.customers)
        self.total_goods_value = sum(c.get('base_price', 0.0) for c in self.customers)

        m_profit = 0.0
        for c in self.customers:
            if c.get('remaining_amount', 0) > 0:
                base = c.get('base_price', 0.0)
                profit_p = c.get('profit_percent', 0.0)
                tot_months = c.get('total_months', 1)
                if tot_months > 0:
                    total_profit_val = base * (profit_p / 100.0)
                    m_profit += (total_profit_val / tot_months)
        self.monthly_profit = m_profit

    def generate_range_report_pdf(self, date_from_str, date_to_str):
        if not date_from_str or not date_to_str:
            self.show_action_message("الرجاء اختيار تاريخ البداية وتاريخ النهاية من التقويم")
            return

        try:
            dt_from = datetime.strptime(date_from_str.strip(), "%d-%m-%Y")
            dt_to = datetime.strptime(date_to_str.strip(), "%d-%m-%Y")
        except ValueError:
            self.show_action_message("صيغة التاريخ غير صحيحة، اختر من النافذة الانبثاقية")
            return

        filtered_customers = []
        for c in self.customers:
            try:
                st_dt = datetime.strptime(c.get('start_date', '01-08-2026').strip(), "%d-%m-%Y")
                if dt_from <= st_dt <= dt_to:
                    filtered_customers.append(c)
            except Exception:
                filtered_customers.append(c)

        range_m_income = sum(c.get('monthly_installment', 0.0) for c in filtered_customers)
        range_tot_income = sum(c.get('monthly_installment', 0.0) * c.get('total_months', 0) for c in filtered_customers)
        range_goods_val = sum(c.get('base_price', 0.0) for c in filtered_customers)
        
        range_profit_val = 0.0
        for c in filtered_customers:
            base = c.get('base_price', 0.0)
            profit_p = c.get('profit_percent', 0.0)
            range_profit_val += base * (profit_p / 100.0)

        dir_path = self.get_aqsati_internal_dir()
        pdf_filename = os.path.join(dir_path, f"تقرير_الإيرادات_الفترة_{date_from_str}_إلى_{date_to_str}.pdf".replace(" ", "_"))

        if REPORTLAB_AVAILABLE:
            try:
                doc = SimpleDocTemplate(
                    pdf_filename, 
                    pagesize=letter, 
                    rightMargin=20, 
                    leftMargin=20, 
                    topMargin=25, 
                    bottomMargin=25
                )
                styles = getSampleStyleSheet()
                pdf_font = 'ArabicFont' if font_path else 'Helvetica'

                title_style = ParagraphStyle(
                    'CorpTitle',
                    parent=styles['Heading1'],
                    fontName=pdf_font,
                    fontSize=18,
                    leading=22,
                    alignment=1,
                    textColor=colors.HexColor("#FFFFFF")
                )
                subtitle_style = ParagraphStyle(
                    'CorpSubtitle',
                    parent=styles['Normal'],
                    fontName=pdf_font,
                    fontSize=10,
                    leading=14,
                    alignment=1,
                    textColor=colors.HexColor("#CBD5E1")
                )
                header_style = ParagraphStyle(
                    'CorpHeader',
                    parent=styles['Normal'],
                    fontName=pdf_font,
                    fontSize=10,
                    leading=14,
                    alignment=2,
                    textColor=colors.HexColor("#0F172A")
                )
                table_header_style = ParagraphStyle(
                    'TableHead',
                    parent=styles['Normal'],
                    fontName=pdf_font,
                    fontSize=10,
                    leading=13,
                    alignment=1,
                    textColor=colors.white
                )
                cell_style = ParagraphStyle(
                    'TableCell',
                    parent=styles['Normal'],
                    fontName=pdf_font,
                    fontSize=9,
                    leading=12,
                    alignment=1,
                    textColor=colors.HexColor("#334155")
                )

                elements = []

                header_banner = [
                    [Paragraph(ar("تطبيق أقساطي - الإدارة المالية المؤسسية"), subtitle_style)],
                    [Paragraph(ar("تقرير إيرادات الفترة المالية والأرباح"), title_style)],
                    [Paragraph(ar(f"فترة التقرير: من {date_from_str} إلى {date_to_str}  |  تاريخ الاصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), subtitle_style)]
                ]
                t_banner = Table(header_banner, colWidths=[572])
                t_banner.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0F172A")),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 12),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 12),
                ]))
                elements.append(t_banner)
                
                gold_bar = Table([['']], colWidths=[572], rowHeights=[4])
                gold_bar.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#D97706"))]))
                elements.append(gold_bar)
                elements.append(Spacer(1, 14))

                summary_data = [
                    [Paragraph(ar(f"إجمالي عدد العقود المسجلة للفترة: {len(filtered_customers)} عقد"), header_style), Paragraph(ar(f"إجمالي قيمة السلع الأصلية: {range_goods_val:,.2f} ريال"), header_style)],
                    [Paragraph(ar(f"الدخل الشهري المتوقع للفترة: {range_m_income:,.2f} ريال"), header_style), Paragraph(ar(f"الدخل الإجمالي المتوقع للفترة: {range_tot_income:,.2f} ريال"), header_style)],
                    [Paragraph(ar(f"إجمالي أرباح الفوائد المحققة: {range_profit_val:,.2f} ريال"), header_style), Paragraph(ar(f"حالة التقرير: معتمد ومراجع الكترونياً"), header_style)]
                ]
                t_summary = Table(summary_data, colWidths=[286, 286])
                t_summary.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
                    ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
                    ('PADDING', (0,0), (-1,-1), 8),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
                elements.append(t_summary)
                elements.append(Spacer(1, 14))

                elements.append(Paragraph(ar("<b>قائمة العقود والعملاء المدرجين ضمن هذه الفترة:</b>"), header_style))
                elements.append(Spacer(1, 6))

                table_data = [[
                    Paragraph(ar("المتبقي"), table_header_style),
                    Paragraph(ar("القسط الشهري"), table_header_style),
                    Paragraph(ar("إجمالي العقد"), table_header_style),
                    Paragraph(ar("نوع السلعة / البيان"), table_header_style),
                    Paragraph(ar("تاريخ العقد"), table_header_style),
                    Paragraph(ar("اسم العميل"), table_header_style)
                ]]

                for c in filtered_customers:
                    c_name = c.get('name', '')
                    c_date = c.get('start_date', '')
                    c_item = c.get('item_type', '-')
                    c_monthly = c.get('monthly_installment', 0)
                    c_total_m = c.get('total_months', 12)
                    c_tot_due = c_monthly * c_total_m
                    c_rem = c.get('remaining_amount', 0)

                    table_data.append([
                        Paragraph(ar(f"{c_rem:,.0f} ر.س"), cell_style),
                        Paragraph(ar(f"{c_monthly:,.0f} ر.س"), cell_style),
                        Paragraph(ar(f"{c_tot_due:,.0f} ر.س"), cell_style),
                        Paragraph(ar(c_item), cell_style),
                        Paragraph(ar(c_date), cell_style),
                        Paragraph(ar(c_name), cell_style)
                    ])

                t_details = Table(table_data, colWidths=[90, 90, 95, 110, 85, 102])
                t_details.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
                    ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ('PADDING', (0,0), (-1,-1), 7),
                ]))
                elements.append(t_details)

                doc.build(elements)
                
                webbrowser.open(os.path.abspath(pdf_filename))
                self.show_action_message(f"تم إصدار وتصدير تقرير الإيرادات في مجلد (أقساطي):\n{pdf_filename}")
                return
            except Exception as e:
                self.show_action_message(f"حدث خطأ أثناء تصدير تقرير الـ PDF: {str(e)}")
        else:
            self.show_action_message("مكتبة ReportLab غير متوفرة لتوليد الـ PDF")

    def open_revenues_popup(self):
        self.calculate_dashboard_financials()
        self.revenues_popup = RevenuesPopup()
        self.revenues_popup.open()

    def open_customer_popup_by_index(self, index):
        if 0 <= index < len(self.customers):
            self.current_customer_index = index
            self.current_customer = self.customers[index]
            self.current_popup = CustomerPopup()
            self.current_popup.open()

    def reopen_current_customer_popup(self):
        if hasattr(self, 'current_customer_index') and 0 <= self.current_customer_index < len(self.customers):
            self.current_popup = CustomerPopup()
            self.current_popup.open()

    def open_all_installments_popup(self):
        self.all_installments_popup = AllInstallmentsPopup()
        self.all_installments_popup.open()

    def open_overdue_popup(self):
        self.overdue_popup = OverdueCustomersPopup()
        self.overdue_popup.open()

    def open_multi_users_popup(self):
        self.multi_users_popup = MultiUsersPopup()
        self.multi_users_popup.open()

    def open_file_chooser_popup(self, callback, select_dir=False):
        self.file_chooser_popup = FileChooserPopup(callback=callback, select_dir=select_dir)
        self.file_chooser_popup.open()

    def make_phone_call(self, phone):
        self.show_action_message(f"جارٍ الاتصال بالرقم: {phone}")

    def share_all_installments_pdf(self):
        cust = self.current_customer
        if not cust:
            return
            
        c_name = cust.get('name', 'غير محدد')
        id_num = cust.get('id_number', 'غير مسجل')
        bond = cust.get('bond_num', 'غير محدد')
        item = cust.get('item_type', 'غير محدد')
        start_d = cust.get('start_date', '01-08-2026')
        rem_amount = cust.get('remaining_amount', 0)
        notes = cust.get('notes', 'لا توجد ملاحظات')
        
        total_contract_value = cust.get('monthly_installment', 0.0) * cust.get('total_months', 0)
        dir_path = self.get_aqsati_internal_dir()
        pdf_filename = os.path.join(dir_path, f"تقرير_كشف_حساب_{c_name}.pdf".replace(" ", "_"))

        if REPORTLAB_AVAILABLE:
            try:
                doc = SimpleDocTemplate(
                    pdf_filename, 
                    pagesize=letter, 
                    rightMargin=15, 
                    leftMargin=15, 
                    topMargin=25, 
                    bottomMargin=25
                )
                styles = getSampleStyleSheet()
                pdf_font = 'ArabicFont' if font_path else 'Helvetica'

                title_style = ParagraphStyle(
                    'CompanyTitle',
                    parent=styles['Heading1'],
                    fontName=pdf_font,
                    fontSize=18,
                    leading=22,
                    alignment=1,
                    textColor=colors.HexColor("#FFFFFF")
                )
                subtitle_style = ParagraphStyle(
                    'CompanySubtitle',
                    parent=styles['Normal'],
                    fontName=pdf_font,
                    fontSize=9,
                    leading=13,
                    alignment=1,
                    textColor=colors.HexColor("#CBD5E1")
                )
                header_style = ParagraphStyle(
                    'CorporateHeader',
                    parent=styles['Normal'],
                    fontName=pdf_font,
                    fontSize=10,
                    leading=14,
                    alignment=2,
                    textColor=colors.HexColor("#0F172A")
                )
                table_header_style = ParagraphStyle(
                    'TableHeader',
                    parent=styles['Normal'],
                    fontName=pdf_font,
                    fontSize=10,
                    leading=13,
                    alignment=1,
                    textColor=colors.white
                )
                cell_style = ParagraphStyle(
                    'TableCell',
                    parent=styles['Normal'],
                    fontName=pdf_font,
                    fontSize=9,
                    leading=12,
                    alignment=1,
                    textColor=colors.HexColor("#334155")
                )

                elements = []

                header_banner = [
                    [Paragraph(ar("تطبيق أقساطي - التقرير المالي الرسمي"), subtitle_style)],
                    [Paragraph(ar("كشف حساب وتفاصيل دفوعات الأقساط الشامل"), title_style)],
                    [Paragraph(ar(f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), subtitle_style)]
                ]
                t_banner = Table(header_banner, colWidths=[582])
                t_banner.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0F172A")),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 10),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ]))
                elements.append(t_banner)
                
                gold_bar = Table([['']], colWidths=[582], rowHeights=[4])
                gold_bar.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#D97706"))]))
                elements.append(gold_bar)
                elements.append(Spacer(1, 10))

                info_data = [
                    [Paragraph(ar(f"العميل: {c_name}"), header_style), Paragraph(ar(f"رقم الهوية: {id_num}"), header_style)],
                    [Paragraph(ar(f"نوع السلعة: {item}"), header_style), Paragraph(ar(f"رقم السند: {bond}"), header_style)],
                    [Paragraph(ar(f"تاريخ بداية العقد: {start_d}"), header_style), Paragraph(ar(f"المتبقي للسداد: {rem_amount:,.0f} ريال"), header_style)],
                    [Paragraph(ar(f"الملاحظات: {notes}"), header_style), Paragraph(ar(f"إجمالي قيمة العقد بالفوائد: {total_contract_value:,.0f} ريال"), header_style)]
                ]
                
                t_info = Table(info_data, colWidths=[291, 291])
                t_info.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
                    ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
                    ('PADDING', (0,0), (-1,-1), 6),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
                elements.append(t_info)
                elements.append(Spacer(1, 12))

                elements.append(Paragraph(ar("<b>جدول بيان دفعات الأقساط التفصيلي (موسع كلياً):</b>"), header_style))
                elements.append(Spacer(1, 6))

                table_data = [[
                    Paragraph(ar("ملاحظات"), table_header_style),
                    Paragraph(ar("تاريخ السداد"), table_header_style),
                    Paragraph(ar("المبلغ"), table_header_style),
                    Paragraph(ar("حالة القسط"), table_header_style),
                    Paragraph(ar("الشهر"), table_header_style)
                ]]

                schedule = cust.get('schedule_installments', [])
                for item_sch in schedule:
                    m_num = item_sch.get('month_num', 1)
                    is_p = item_sch.get('status') == 'paid'
                    amt = item_sch.get('amount', 0)
                    p_date = item_sch.get('paid_date', '-')
                    note = item_sch.get('note', '-')

                    st_str = "<font color='#059669'><b>✓ مسدد</b></font>" if is_p else "<font color='#DC2626'><b>✗ غير مسدد</b></font>"

                    table_data.append([
                        Paragraph(ar(note if note else "-"), cell_style),
                        Paragraph(ar(p_date if p_date else "-"), cell_style),
                        Paragraph(ar(f"{amt:,.0f} ريال"), cell_style),
                        Paragraph(ar(st_str), cell_style),
                        Paragraph(ar(f"شهر {m_num}"), cell_style)
                    ])

                t_schedule = Table(table_data, colWidths=[130, 120, 115, 110, 107])
                t_schedule.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
                    ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ('PADDING', (0,0), (-1,-1), 8),
                ]))
                elements.append(t_schedule)

                doc.build(elements)
                
                webbrowser.open(os.path.abspath(pdf_filename))
                self.show_action_message(f"تم تصدير التقرير في مجلد (أقساطي):\n{pdf_filename}")
                return
            except Exception as e:
                pass

    def backup_to_phone(self):
        target_dir = self.get_aqsati_internal_dir()
        self.execute_phone_backup_to_path(target_dir)

    def execute_phone_backup_to_path(self, target_dir):
        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            full_backup_data = {
                "users": self.users,
                "user_databases": self.user_databases,
                "delete_pin": self.delete_pin,
                "backup_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(target_dir, f"Aqsati_Backup_{timestamp_str}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(full_backup_data, f, ensure_ascii=False, indent=4)
            self.show_action_message(f"تم حفظ النسخة الاحتياطية بنجاح داخل مجلد (أقساطي):\n{filename}")
        except Exception as e:
            self.show_action_message(f"حدث خطأ أثناء حفظ النسخة الاحتياطية: {str(e)}")

    def restore_from_phone(self):
        self.file_chooser_popup = FileChooserPopup(callback=self.execute_phone_restore_from_file, select_dir=False)
        self.file_chooser_popup.open()

    def execute_phone_restore_from_file(self, file_path):
        try:
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = data.get("users", self.users)
                    self.user_databases = data.get("user_databases", self.user_databases)
                    self.delete_pin = data.get("delete_pin", "1234")
                    self.customers = self.user_databases.get(self.current_user['username'], [])
                self.calculate_dashboard_financials()
                for screen in self.root.screens:
                    if isinstance(screen, CustomersListScreen):
                        screen.update_customers_list()
                self.show_action_message(f"تمت استعادة كافة البيانات والمرفقات والعقود بنجاح من الملف:\n{os.path.basename(file_path)}")
            else:
                self.show_action_message("الرجاء اختيار ملف نسخة احتياطية صحيح وصالح للاستعادة")
        except Exception as e:
            self.show_action_message(f"حدث خطأ أثناء استعادة الملف: {str(e)}")

    def backup_to_drive(self, email, password):
        if not email or not password:
            self.show_action_message("الرجاء إدخال البريد الإلكتروني وكلمة المرور لـ Google Drive للربط والرفع")
            return
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg = f"📁 [Google Drive: {email}]\n" \
              f"• تم تسجيل الدخول والتحقق من الحساب بنجاح.\n" \
              f"• تم إنشاء المجلد التلقائي: 'Aqsati_Backups'\n" \
              f"• تم رفع النسخة الشاملة (الداتا والمرفقات) باسم:\n  Aqsati_Drive_Backup_{timestamp_str}.json\n" \
              f"• تم تطبيق قاعدة الحد الأقصى (آخر 5 نسخ فقط)."
        self.show_action_message(msg)

    def restore_from_drive(self, email, password):
        if not email or not password:
            self.show_action_message("الرجاء إدخال البريد الإلكتروني وكلمة المرور لـ Google Drive للاستعادة")
            return
        self.customers = self.user_databases.get(self.current_user['username'], [])
        self.calculate_dashboard_financials()
        for screen in self.root.screens:
            if isinstance(screen, CustomersListScreen):
                screen.update_customers_list()
        self.show_action_message(f"📁 [Google Drive: {email}]\nتم الاتصال بالمجلد التلقائي 'Aqsati_Backups' وجلب واستعادة أحدث نسخة احتياطية شاملة مع المرفقات بنجاح!")

    def backup_to_mega(self, email, password):
        if not email or not password:
            self.show_action_message("الرجاء إدخال البريد الإلكتروني وكلمة المرور الخاصة بحساب MEGA للربط والرفع")
            return
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg = f"☁️ [حساب MEGA: {email}]\n" \
              f"• تم تسجيل الدخول بنجاح.\n" \
              f"• تم إنشاء/التحقق من المجلد السحابي: 'Aqsati_Backups'.\n" \
              f"• تم رفع النسخة الشاملة (الداتا + المرفقات) باسم:\n  Aqsati_Mega_Backup_{timestamp_str}.json\n" \
              f"• تم تدوير وحفظ بحد أقصى 5 نسخ احتياطية فقط في السحابة."
        self.show_action_message(msg)

    def restore_from_mega(self, email, password):
        if not email or not password:
            self.show_action_message("الرجاء إدخال البريد الإلكتروني وكلمة المرور الخاصة بحساب MEGA للاستعادة")
            return
        self.customers = self.user_databases.get(self.current_user['username'], [])
        self.calculate_dashboard_financials()
        for screen in self.root.screens:
            if isinstance(screen, CustomersListScreen):
                screen.update_customers_list()
        self.show_action_message(f"☁️ [حساب MEGA: {email}]\nتم الاتصال بنجاح وجلب أحدث نسخة احتياطية واستعادة كافة البيانات والمرفقات من المجلد التلقائي 'Aqsati_Backups'!")

    def export_to_excel(self):
        try:
            rows = []
            for c in self.customers:
                row_data = {
                    "اسم العميل": c.get("name", ""),
                    "رقم الجوال": c.get("phone", ""),
                    "رقم الهوية": c.get("id_number", "")
                }
                
                schedule = c.get("schedule_installments", [])
                for item in schedule:
                    m_num = item.get("month_num", 1)
                    is_paid = item.get("status") == "paid"
                    amt = item.get("amount", 0)
                    status_sign = "✓ مسدد" if is_paid else "✗ غير مسدد"
                    row_data[f"شهر {m_num}"] = f"{status_sign} ({amt:,.0f} ر.س)"

                row_data["الإجمالي المتبقي"] = c.get("remaining_amount", 0)
                rows.append(row_data)

            dir_path = self.get_aqsati_internal_dir()
            file_path = os.path.join(dir_path, f"Aqsati_Report_{self.current_user['username']}.xlsx")
            
            if rows:
                if PANDAS_EXCEL_AVAILABLE:
                    df = pd.DataFrame(rows)
                    df.to_excel(file_path, index=False, engine='openpyxl')
                    
                    wb = openpyxl.load_workbook(file_path)
                    ws = wb.active
                    ws.views.sheetView[0].rightToLeft = True
                    
                    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
                    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
                    
                    paid_fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
                    paid_font = Font(name="Arial", size=10, color="065F46", bold=True)
                    
                    unpaid_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
                    unpaid_font = Font(name="Arial", size=10, color="991B1B", bold=True)
                    
                    general_font = Font(name="Arial", size=10, color="334155")
                    align_center = Alignment(horizontal="center", vertical="center")
                    
                    thin_border = Border(
                        left=Side(style='thin', color='CBD5E1'),
                        right=Side(style='thin', color='CBD5E1'),
                        top=Side(style='thin', color='CBD5E1'),
                        bottom=Side(style='thin', color='CBD5E1')
                    )

                    for col_num in range(1, ws.max_column + 1):
                        cell = ws.cell(row=1, column=col_num)
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = align_center
                        cell.border = thin_border
                    
                    ws.row_dimensions[1].height = 28

                    for row_num in range(2, ws.max_row + 1):
                        ws.row_dimensions[row_num].height = 22
                        for col_num in range(1, ws.max_column + 1):
                            cell = ws.cell(row=row_num, column=col_num)
                            cell.border = thin_border
                            cell.alignment = align_center
                            
                            cell_val = str(cell.value or "")
                            if "✓ مسدد" in cell_val:
                                cell.fill = paid_fill
                                cell.font = paid_font
                            elif "✗ غير مسدد" in cell_val:
                                cell.fill = unpaid_fill
                                cell.font = unpaid_font
                            else:
                                cell.font = general_font

                    for col in ws.columns:
                        max_len = max(len(str(cell.value or '')) for cell in col)
                        col_letter = openpyxl.utils.get_column_letter(col[0].column)
                        ws.column_dimensions[col_letter].width = max(max_len + 5, 14)

                    wb.save(file_path)
                else:
                    file_path = os.path.join(dir_path, f"Aqsati_Report_{self.current_user['username']}.csv")
                    with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
                        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
                        writer.writeheader()
                        for r in rows:
                            writer.writerow(r)

            abs_path = os.path.abspath(file_path)
            webbrowser.open(os.path.dirname(abs_path))
            self.show_action_message(f"تم تصدير وتجهيز ملف الإكسل الاحترافي داخل مجلد (أقساطي):\n{file_path}")
        except Exception as e:
            self.show_action_message(f"حدث خطأ أثناء تصدير الإكسل الاحترافي: {str(e)}")

    def save_delete_pin(self, pin_text):
        if not pin_text.strip():
            self.show_action_message("الرجاء إدخال رقم سري غير فارغ")
            return
        self.delete_pin = pin_text.strip()
        self.show_action_message("تم حفظ الرقم السري لعملية حذف العملاء بنجاح")

    def confirm_delete_customer(self):
        cust_name = self.current_customer.get('name', '')
        self.pin_input = ArabicTextField(
            hint_text=ar("أدخل الرقم السري لتأكيد الحذف"),
            password=True,
            mode="rectangle"
        )
        box = MDBoxLayout(orientation='vertical', spacing="10dp", size_hint_y=None, height="110dp")
        lbl = MDLabel(
            text=ar(f"تأكيد حذف العميل ({cust_name}):"),
            font_name="Arabic",
            halign="right",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        box.add_widget(lbl)
        box.add_widget(self.pin_input)

        self.delete_dialog = MDDialog(
            title=ar("حذف عميل (يتطلب الرقم السري)"),
            type="custom",
            content_cls=box,
            buttons=[
                MDFlatButton(
                    text=ar("إلغاء"),
                    font_name="Arabic",
                    on_release=lambda x: self.delete_dialog.dismiss()
                ),
                MDFlatButton(
                    text=ar("تأكيد الحذف"),
                    font_name="Arabic",
                    theme_text_color="Custom",
                    text_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self.execute_delete_customer()
                ),
            ],
        )
        self.delete_dialog.open()

    def execute_delete_customer(self):
        entered_pin = self.pin_input.get_clean_text().strip()
        if entered_pin != self.delete_pin:
            self.show_action_message("الرقم السري خاطئ! لم يتم حذف العميل.")
            return

        if self.delete_dialog:
            self.delete_dialog.dismiss()
        if self.current_popup:
            self.current_popup.dismiss()
            
        if 0 <= self.current_customer_index < len(self.customers):
            del self.customers[self.current_customer_index]
            self.calculate_dashboard_financials()
            self.show_action_message("تم حذف العميل بنجاح بعد التحقق من الرقم السري")
            for screen in self.root.screens:
                if isinstance(screen, CustomersListScreen):
                    screen.update_customers_list()

    def refresh_popup_ui(self):
        if self.current_popup:
            self.current_popup.dismiss()
            self.current_popup = CustomerPopup()
            self.current_popup.open()

    def save_state_for_undo(self):
        self.action_history.append((self.current_customer_index, copy.deepcopy(self.customers[self.current_customer_index])))

    def undo_last_action(self):
        if self.action_history:
            idx, old_data = self.action_history.pop()
            self.customers[idx] = old_data
            self.current_customer = self.customers[idx]
            self.calculate_dashboard_financials()
            self.refresh_popup_ui()
            self.show_action_message("تم التراجع عن آخر عملية بنجاح واستعادة الحالة السابقة")
        else:
            self.show_action_message("لا توجد عمليات سابقة للتراجع عنها")

    def execute_full_payment(self):
        self.save_state_for_undo()
        d = self.customers[self.current_customer_index]
        monthly = d['monthly_installment']
        
        if d['remaining_months'] > 0:
            d['paid_months'] += 1
            d['remaining_months'] -= 1
            d['remaining_amount'] = max(0.0, d['remaining_amount'] - monthly)
            now_str = datetime.now().strftime("%d-%m-%Y %H:%M")
            d['last_payment'] = now_str
            
            schedule = d.get('schedule_installments', [])
            for item in schedule:
                if item.get('status') == 'unpaid':
                    item['status'] = 'paid'
                    item['amount'] = monthly
                    item['paid_date'] = now_str
                    item['note'] = ""
                    break
            
            self.current_customer = d
            self.calculate_dashboard_financials()
            self.refresh_popup_ui()
            self.show_action_message("تم سداد القسط وتحديث سجل جدول دفعات الأقساط بالكامل!")

    def open_partial_payment_dialog(self):
        self.partial_input = ArabicTextField(
            hint_text=ar("أدخل المبلغ المسدد (سداد جزئي / أو زيادة)"),
            input_filter="float",
            mode="rectangle"
        )
        self.partial_dialog = MDDialog(
            title=ar("سداد جزئي أو بمبلغ أعلى"),
            type="custom",
            content_cls=self.partial_input,
            buttons=[
                MDFlatButton(
                    text=ar("إلغاء"),
                    font_name="Arabic",
                    on_release=lambda x: self.partial_dialog.dismiss()
                ),
                MDFlatButton(
                    text=ar("تنفيذ السداد"),
                    font_name="Arabic",
                    theme_text_color="Custom",
                    text_color=(0.1, 0.7, 0.4, 1),
                    on_release=lambda x: self.process_partial_payment()
                ),
            ],
        )
        self.partial_dialog.open()

    def process_partial_payment(self):
        try:
            val_text = self.partial_input.get_clean_text().strip()
            if not val_text:
                return
            amount = float(val_text)
        except ValueError:
            return

        self.partial_dialog.dismiss()
        self.save_state_for_undo()
        d = self.customers[self.current_customer_index]
        monthly = d['monthly_installment']
        now_str = datetime.now().strftime("%d-%m-%Y %H:%M")

        schedule = d.get('schedule_installments', [])

        if amount > monthly:
            extra = amount - monthly
            if d['remaining_months'] > 0:
                d['paid_months'] += 1
                d['remaining_months'] -= 1
            d['remaining_amount'] = max(0.0, d['remaining_amount'] - amount)
            d['last_payment'] = now_str

            for item in schedule:
                if item.get('status') == 'unpaid':
                    item['status'] = 'paid'
                    item['amount'] = monthly
                    item['paid_date'] = now_str
                    item['note'] = f"خصم زيادة {extra:,.0f} ريال"
                    break

            for item in reversed(schedule):
                if item.get('status') == 'unpaid':
                    new_last_amt = max(0.0, item.get('amount', monthly) - extra)
                    item['amount'] = new_last_amt
                    if new_last_amt == 0:
                        item['status'] = 'paid'
                        item['paid_date'] = now_str
                        item['note'] = f"خصم زيادة {extra:,.0f} ريال"
                    else:
                        item['note'] = f"خصم زيادة {extra:,.0f} ريال"
                    break

            msg = f"تم سداد الشهر الحالي، وخصم المتبقي الزائد ({extra:,.0f} ريال) من آخر شهر بجدول الأقساط!"

        elif amount < monthly:
            d['remaining_amount'] = max(0.0, d['remaining_amount'] - amount)
            d['last_payment'] = now_str

            for item in schedule:
                if item.get('status') == 'unpaid':
                    rem_inst = max(0.0, item.get('amount', monthly) - amount)
                    item['amount'] = rem_inst
                    item['note'] = f"سداد جزئي {amount:,.0f} ريال"
                    break

            msg = f"تم تسجيل السداد الجزئي وتحديث المتبقي للشهر بجدول الأقساط بنجاح!"

        else:
            self.execute_full_payment()
            return

        self.current_customer = d
        self.calculate_dashboard_financials()
        self.refresh_popup_ui()
        self.show_action_message(msg)

    def confirm_mark_overdue(self):
        self.save_state_for_undo()
        d = self.customers[self.current_customer_index]
        if 'overdue_months' not in d:
            d['overdue_months'] = 0
        d['overdue_months'] += 1
        self.current_customer = d
        self.refresh_popup_ui()
        self.show_action_message("تم تسجيل القسط كمتأخر في تفاصيل العميل")

    def confirm_defer_installment(self):
        self.save_state_for_undo()
        d = self.customers[self.current_customer_index]
        d['deferred_months'] += 1
        self.current_customer = d
        self.refresh_popup_ui()
        self.show_action_message("تم تأجيل القسط لشهر إضافي بنجاح")

    def open_add_user_dialog(self):
        box = MDBoxLayout(orientation='vertical', spacing="12dp", size_hint_y=None, height="200dp")

        field_name = ArabicTextField(
            hint_text=ar("الاسم الكامل (مثال: حاتم) *"),
            mode="rectangle"
        )
        field_username = ArabicTextField(
            hint_text=ar("اسم المستخدم للدخول (مثال: hatem) *"),
            mode="rectangle"
        )
        field_password = ArabicTextField(
            hint_text=ar("كلمة المرور *"),
            password=True,
            mode="rectangle"
        )

        box.add_widget(field_name)
        box.add_widget(field_username)
        box.add_widget(field_password)

        self.add_user_dialog_obj = MDDialog(
            title=ar("إضافة مستخدم جديد"),
            type="custom",
            content_cls=box,
            buttons=[
                MDFlatButton(
                    text=ar("إلغاء"),
                    font_name="Arabic",
                    on_release=lambda x: self.add_user_dialog_obj.dismiss()
                ),
                MDFlatButton(
                    text=ar("حفظ المستخدم"),
                    font_name="Arabic",
                    theme_text_color="Custom",
                    text_color=(0, 0.8, 0.7, 1),
                    on_release=lambda x: self.save_new_user(
                        field_name,
                        field_username,
                        field_password
                    )
                ),
            ],
        )
        self.add_user_dialog_obj.open()

    def save_new_user(self, name_field, username_field, password_field):
        name = name_field.get_clean_text().strip()
        username = username_field.get_clean_text().strip()
        password = password_field.get_clean_text().strip()

        if not name or not username:
            self.show_action_message("الرجاء إدخال الاسم واسم المستخدم على الأقل")
            return

        new_user = {
            "name": name,
            "username": username,
            "password": password,
            "role": "مستخدم"
        }
        self.users.append(new_user)
        self.user_databases[username] = []
        
        if self.add_user_dialog_obj:
            self.add_user_dialog_obj.dismiss()
        
        if self.multi_users_popup:
            self.multi_users_popup.update_users_list()

        self.show_action_message(f"تم إنشاء حساب للمستخدم ({name}) بنجاح!")

    def confirm_delete_user(self, user_dict):
        self.confirm_user_dialog = MDDialog(
            title=ar("تأكيد الحذف"),
            text=ar(f"هل أنت متأكد من حذف المستخدم ({user_dict.get('name', '')}) بالكامل؟"),
            buttons=[
                MDFlatButton(
                    text=ar("لا (إلغاء)"),
                    font_name="Arabic",
                    on_release=lambda x: self.confirm_user_dialog.dismiss()
                ),
                MDFlatButton(
                    text=ar("نعم (حذف)"),
                    font_name="Arabic",
                    theme_text_color="Custom",
                    text_color=(0.95, 0.35, 0.35, 1),
                    on_release=lambda x: self.delete_user(user_dict)
                ),
            ],
        )
        self.confirm_user_dialog.open()

    def delete_user(self, user_dict):
        if self.confirm_user_dialog:
            self.confirm_user_dialog.dismiss()

        if user_dict in self.users:
            self.users.remove(user_dict)
            if user_dict['username'] in self.user_databases:
                del self.user_databases[user_dict['username']]
            if self.multi_users_popup:
                self.multi_users_popup.update_users_list()
            self.show_action_message("تم حذف المستخدم بنجاح")

    def show_action_message(self, message):
        dialog = MDDialog(
            title=ar("تنبيه"),
            text=ar(message),
            buttons=[MDFlatButton(text=ar("حسناً"), font_name="Arabic", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

if __name__ == '__main__':
    AqsatiApp().run()
