import requests
import os
from time import sleep
import json

class ZenodoRecord:
    def __init__(self, record_id, title, authors, keywords, publication_date, description, files):
        self.record_id = record_id
        self.title = title
        self.authors = authors
        self.keywords = keywords
        self.publication_date = publication_date
        self.description = description
        self.files = files

    def to_dict(self):
        return {
            "record_id": self.record_id,
            "title": self.title,
            "authors": self.authors,
            "keywords": self.keywords,
            "publication_date": self.publication_date,
            "description": self.description,
            "files": self.files
        }

def find_pdf_url(record):
    """根据 Zenodo 官方文件结构检测 PDF 文件"""
    files = record.get('files', [])
    for file in files:
        file_key = file.get('key', '').lower()
        file_type = file.get('mimetype', '').lower()

        if file_key.endswith('.pdf') or file_type == 'application/pdf':
            return file.get('links', {}).get('self', '')
    return None

def save_metadata_to_txt(record, output_path):
    """将记录元数据保存到txt文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        # 写入标题
        f.write(f"Title: {record.title}\n\n")

        # 写入作者信息
        authors = ', '.join(record.authors)
        f.write(f"Authors: {authors}\n\n")

        # 写入关键词
        keywords = ', '.join(record.keywords)
        f.write(f"Keywords: {keywords}\n\n")

        # 写入出版日期
        f.write(f"Publication date: {record.publication_date}\n\n")

        # 写入描述
        f.write("Description:\n")
        f.write(record.description.replace('<p>', '\n').replace('</p>', '\n').replace('<br>', '\n').replace('<br/>', '\n'))
        f.write("\n\n")

        # 写入文件信息
        if record.files:
            f.write("Contents:\n")
            for file in record.files:
                file_key = file.get('key', 'unknown')
                f.write(f" - {file_key}\n")

def zenodo_crawler(search_query, max_results=10, sort_by="mostrecent",
                   download_pdf=False, output_dir='./zenodo_records'):
    os.makedirs(output_dir, exist_ok=True)

    base_url = "https://zenodo.org/api/records"
    params = {
        "q": search_query,
        "size": max_results,
        "sort": sort_by,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        for record in data.get('hits', {}).get('hits', []):
            record_id = record.get('id', 'unknown_id')
            print(f"\nProcessing record: {record_id}")

            # 提取元数据
            title = record.get('metadata', {}).get('title', 'N/A')
            authors = [author.get('name', 'N/A') for author in record.get('metadata', {}).get('creators', [])]
            keywords = record.get('metadata', {}).get('keywords', [])
            publication_date = record.get('metadata', {}).get('publication_date', 'N/A')
            description = record.get('metadata', {}).get('description', 'N/A')
            files = record.get('files', [])

            # 创建 ZenodoRecord 对象
            zenodo_record = ZenodoRecord(
                record_id=record_id,
                title=title,
                authors=authors,
                keywords=keywords,
                publication_date=publication_date,
                description=description,
                files=files
            )

            # 保存元数据
            base_filename = os.path.join(output_dir, str(record_id))
            save_metadata_to_txt(zenodo_record, f"{base_filename}.txt")

            # PDF 下载处理
            if download_pdf:
                pdf_url = find_pdf_url(record)
                if pdf_url:
                    pdf_path = f"{base_filename}.pdf"

                    if not os.path.exists(pdf_path):
                        print(f"Found PDF at: {pdf_url}")
                        print(f"Attempting download to: {pdf_path}")

                        try:
                            headers = {'User-Agent': 'Mozilla/5.0'}
                            response = requests.get(pdf_url, headers=headers, stream=True)
                            response.raise_for_status()

                            with open(pdf_path, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)

                            print("Download completed successfully")
                            sleep(1)  # 礼貌性延迟

                        except Exception as e:
                            print(f"PDF download failed: {str(e)}")
                            if os.path.exists(pdf_path):
                                os.remove(pdf_path)
                    else:
                        print(f"PDF already exists at {pdf_path}")
                else:
                    print("No PDF file found in this record. Available files:")
                    for f in files:
                        print(f" - {f.get('key', 'unknown')} (type: {f.get('mimetype', 'unknown')})")

    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    search_query = ""
    zenodo_crawler(
        search_query=search_query,
        max_results=500,
        sort_by="mostrecent",
        download_pdf=False,
        output_dir="./zenodo_papers"
    )