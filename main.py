import flet as ft
import cv2
import pytesseract
from PIL import Image
import numpy as np
import os
import requests
import shutil
from datetime import datetime

# تهيئة Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # تعديل حسب نظامك

def main(page: ft.Page):
    page.title = "Document Scanner"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # متغيرات التطبيق
    captured_image_path = None
    extracted_text = ""
    pc_ip = ""
    
    # عناصر الواجهة
    img = ft.Image(
        width=300,
        height=400,
        fit=ft.ImageFit.CONTAIN,
        border_radius=ft.border_radius.all(10)
    )
    
    result_text = ft.TextField(
        multiline=True,
        min_lines=10,
        max_lines=10,
        expand=True,
        border_color=ft.Colors.BLUE_GREY
    )
    
    ip_textfield = ft.TextField(
        label="PC IP Address",
        value="192.168.1.100",
        width=300
    )
    
    def capture_image(e):
        nonlocal captured_image_path
        # في التطبيق الحقيقي، هنا يتم استخدام الكاميرا
        # هذا مثال للاختبار فقط
        captured_image_path = "sample_doc.jpg"  # استبدل بمسار صورة حقيقية
        img.src = captured_image_path
        page.update()
        page.snack_bar = ft.SnackBar(ft.Text("تم التقاط الصورة بنجاح"))
        page.snack_bar.open = True
        page.update()
    
    def extract_text(e):
        nonlocal extracted_text, captured_image_path
        if not captured_image_path:
            return
            
        try:
            # معالجة الصورة باستخدام OpenCV
            img_cv = cv2.imread(captured_image_path)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # تحسين الصورة للـOCR
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # استخراج النص
            extracted_text = pytesseract.image_to_string(gray, lang='ara+eng')
            result_text.value = extracted_text
            
            # حفظ النص في ملف
            with open('extracted_text.txt', 'w', encoding='utf-8') as f:
                f.write(extracted_text)
                
            page.snack_bar = ft.SnackBar(ft.Text("تم استخراج النص بنجاح"))
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"خطأ في استخراج النص: {str(ex)}"))
        
        page.snack_bar.open = True
        page.update()
    
    def save_for_usb(e):
        try:
            # إنشاء مجلد للملفات
            output_dir = "/sdcard/Documents/ocr_output/"
            os.makedirs(output_dir, exist_ok=True)
            
            # نسخ الملفات
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy('extracted_text.txt', f"{output_dir}text_{timestamp}.txt")
            
            if os.path.exists('output.pdf'):
                shutil.copy('output.pdf', f"{output_dir}doc_{timestamp}.pdf")
            
            page.snack_bar = ft.SnackBar(ft.Text(f"تم حفظ الملفات في {output_dir}"))
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"خطأ في حفظ الملفات: {str(ex)}"))
        
        page.snack_bar.open = True
        page.update()
    
    def send_to_pc(e):
        nonlocal pc_ip
        pc_ip = ip_textfield.value
        
        try:
            url = f'http://{pc_ip}:5000/upload'
            
            # إرسال ملف النص
            with open('extracted_text.txt', 'rb') as f:
                response = requests.post(url, files={'file': f})
            
            if response.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("تم إرسال الملف إلى الحاسوب بنجاح"))
            else:
                page.snack_bar = ft.SnackBar(ft.Text("فشل إرسال الملف إلى الحاسوب"))
                
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"خطأ في الإرسال: {str(ex)}"))
        
        page.snack_bar.open = True
        page.update()
    
    # بناء الواجهة
    page.add(
        ft.Column([
            ft.Text("Document Scanner", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.CAMERA_ALT,
                    on_click=capture_image,
                    tooltip="التقاط صورة"
                ),
                ft.IconButton(
                    icon=ft.Icons.TEXT_SNIPPET,
                    on_click=extract_text,
                    tooltip="استخراج النص"
                ),
                ft.IconButton(
                    icon=ft.Icons.USB,
                    on_click=save_for_usb,
                    tooltip="حفظ للإرسال عبر USB"
                ),
                ft.IconButton(
                    icon=ft.Icons.SEND,
                    on_click=send_to_pc,
                    tooltip="إرسال عبر الشبكة"
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Container(
                content=img,
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY)
            ),
            
            ip_textfield,
            
            ft.Container(
                content=result_text,
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY),
                expand=True
            ),
            
            ft.Text("اختر طريقة الإرسال:", size=16),
        ], expand=True)
    )

if __name__ == "__main__":
    ft.app(target=main)
