import os
from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path, page):
    """
    解析PDF文件指定页的文本内容。
    :param file_path: PDF文件路径
    :param page: 页码（从1开始）
    :return: 文本内容字符串
    :raises: Exception if file not found, page out of range, or parse error
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    reader = PdfReader(file_path)
    if page < 1 or page > len(reader.pages):
        raise ValueError(f"页码超出范围: {page}")
    text = reader.pages[page-1].extract_text() or ''
    return text

def save_and_convert_upload_file(file, room_id, upload_root, libreoffice_path, max_size=50*1024*1024):
    """
    检查上传文件类型、大小，保存文件，必要时转换格式（如PPT转PDF）。
    :param file: werkzeug.datastructures.FileStorage
    :param room_id: 房间ID
    :param upload_root: 上传根目录
    :param libreoffice_path: LibreOffice可执行文件路径
    :param max_size: 最大文件大小（字节）
    :return: (save_path, filename, ext)
    :raises: Exception if 检查失败或保存/转换失败
    """
    allowed_ext = {'pdf', 'ppt', 'pptx'}
    filename = file.filename
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in allowed_ext:
        raise ValueError('文件类型不支持')
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > max_size:
        raise ValueError('文件大小超出限制')
    upload_dir = os.path.join(upload_root, str(room_id))
    os.makedirs(upload_dir, exist_ok=True)
    if ext in ('ppt', 'pptx'):
        import tempfile
        import shutil
        from pathlib import Path
        import pythoncom
        import subprocess
        temp_dir = tempfile.mkdtemp()
        ppt_path = os.path.join(temp_dir, filename)
        file.save(ppt_path)
        pdf_filename = Path(filename).stem + '.pdf'
        pdf_path = os.path.join(upload_dir, pdf_filename)
        pythoncom.CoInitialize()
        try:
            subprocess.run([
                libreoffice_path, '--headless', '--convert-to', 'pdf', '--outdir', upload_dir, ppt_path
            ], check=True)
            converted_pdf = os.path.join(upload_dir, Path(filename).stem + '.pdf')
            if os.path.exists(converted_pdf) and converted_pdf != pdf_path:
                shutil.move(converted_pdf, pdf_path)
            save_path = pdf_path
            filename = pdf_filename
            ext = 'pdf'
        except Exception as e:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
            raise RuntimeError(f'PPT转PDF失败: {e}')
        import time
        time.sleep(1)
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass
    else:
        save_path = os.path.join(upload_dir, filename)
        file.save(save_path)
    return save_path, filename, ext 

def extract_text_from_whole_pdf(file_path):
    """解析整个PDF文件，返回每页文本组成的列表"""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        texts = []
        for page in reader.pages:
            text = page.extract_text() or ''
            texts.append(text)
        return texts
    except Exception as e:
        print(f"extract_text_from_whole_pdf error: {e}")
        return [] 