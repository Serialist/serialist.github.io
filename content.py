import os
import json
import hashlib
import shutil
import re
import argparse
import uuid
import yaml
from datetime import datetime, date

# ========== 核心配置 ==========
CONFIG = {
    "INPUT_DIR": "./blog",
    "OUTPUT_DIR": "./page/blog",
    "ASSETS_DIR": "./assets/content",
    "JSON_OUT": "./articles.json"
}

def get_content_hash(text):
    """计算文本内容的哈希值，用于判断内容是否变动"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def get_file_hash(file_path):
    """计算二进制文件的哈希值，用于图片去重"""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hashlib.md5(hasher.digest()).hexdigest()[:12]

def parse_markdown(raw_content):
    """
    解析 YAML Front Matter 和 提取第一个一级标题
    返回: (metadata, clean_content, extracted_title)
    """
    metadata = {}
    content = raw_content
    extracted_title = None

    # 1. 解析 YAML Front Matter
    yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.search(yaml_pattern, raw_content, re.DOTALL)
    if match:
        try:
            raw_meta = yaml.safe_load(match.group(1)) or {}
            # 处理 YAML 自动转换出的 date 对象，转为字符串以适配 JSON
            for k, v in raw_meta.items():
                if isinstance(v, (datetime, date)):
                    metadata[k] = v.isoformat()
                else:
                    metadata[k] = v
            content = raw_content[match.end():] # 移除 YAML 部分
        except yaml.YAMLError:
            pass

    # 2. 提取第一个一级标题 (# Title)
    title_match = re.search(r'^#\s+(.*)$', content, re.MULTILINE)
    if title_match:
        extracted_title = title_match.group(1).strip()
    
    return metadata, content, extracted_title

def process_assets(content, md_dir):
    """处理图片资源"""
    img_pattern = r'!\[(.*?)\]\((.*?)\)'
    os.makedirs(CONFIG["ASSETS_DIR"], exist_ok=True)

    def replace_img(match):
        alt, src = match.group(1), match.group(2)
        if src.startswith(('http', '//', 'data:')): return match.group(0)
        src_path = os.path.normpath(os.path.join(md_dir, src))
        if os.path.exists(src_path):
            ext = os.path.splitext(src)[1]
            img_id = get_file_hash(src_path)
            new_name = f"{img_id}{ext}"
            shutil.copy2(src_path, os.path.join(CONFIG["ASSETS_DIR"], new_name))
            return f"![{alt}](assets/content/{new_name})"
        return match.group(0)

    return re.sub(img_pattern, replace_img, content)

def manage():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["build", "add"])
    parser.add_argument("-r", "--recursive", action="store_true")
    args = parser.parse_args()

    # 加载旧数据
    old_data = {}
    if os.path.exists(CONFIG["JSON_OUT"]):
        with open(CONFIG["JSON_OUT"], "r", encoding="utf-8") as f:
            try:
                raw_json = json.load(f)
                for a in raw_json: old_data[a['title']] = a
            except (json.JSONDecodeError, TypeError):
                print(f"[!] {CONFIG['JSON_OUT']} 损坏，将重新生成索引。")
                old_data = {}

    # 扫描文件
    files = []
    if args.recursive:
        for r, _, fs in os.walk(CONFIG["INPUT_DIR"]):
            for f in fs:
                if f.endswith(".md"): files.append(os.path.join(r, f))
    else:
        if not os.path.exists(CONFIG["INPUT_DIR"]):
            os.makedirs(CONFIG["INPUT_DIR"])
        files = [os.path.join(CONFIG["INPUT_DIR"], f) for f in os.listdir(CONFIG["INPUT_DIR"]) if f.endswith(".md")]

    new_articles = []
    os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)

    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            raw_content = f.read()
        
        # 解析元数据和内容
        meta, clean_content, ext_title = parse_markdown(raw_content)
        
        # 确定标题：优先使用正文一级标题，其次使用文件名
        title = ext_title if ext_title else os.path.splitext(os.path.basename(fpath))[0]
        
        current_hash = get_content_hash(raw_content)
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # 判断是更新还是新建
        if title in old_data:
            item = old_data[title]
            if item.get("content_hash") == current_hash:
                new_articles.append(item)
                continue
            
            choice = input(f"[!] 检测到文章修改: {title}. 更新内容? (y/n): ").lower()
            if choice != 'y':
                new_articles.append(item)
                continue
            
            print(f"[~] 正在更新: {title}")
            item.update(meta) # 用 YAML 内容更新原有信息
            item["modified"] = now_time
            item["content_hash"] = current_hash
            # 如果 YAML 里显式写了 created，则覆盖
            if "created" in meta:
                item["created"] = str(meta["created"])
        else:
            article_id = uuid.uuid4().hex[:8]
            print(f"[+] 发现新文章: {title} -> ID: {article_id}")
            
            # 基础信息
            item = {
                "id": article_id,
                "title": title,
                "created": str(meta.get("created", now_time)),
                "modified": now_time,
                "author": meta.get("author", "Serialist"),
                "content_hash": current_hash
            }
            # 合并 YAML 中的其他自定义字段
            item.update({k: v for k, v in meta.items() if k not in item})

        # 处理图片资源（基于移除 YAML 后的内容）
        processed_content = process_assets(clean_content, os.path.dirname(fpath))
        
        # 写入输出目录（不带 YAML 头部）
        with open(os.path.join(CONFIG["OUTPUT_DIR"], f"{item['id']}.md"), "w", encoding="utf-8") as f:
            f.write(processed_content.strip())
        
        new_articles.append(item)

    # 保存索引（按创建时间倒序排）
    new_articles.sort(key=lambda x: str(x.get('created', '')), reverse=True)
    with open(CONFIG["JSON_OUT"], "w", encoding="utf-8") as f:
        json.dump(new_articles, f, ensure_ascii=False, indent=4)
    
    print(f"\n处理完成。当前库内共有 {len(new_articles)} 篇文章。")

if __name__ == "__main__":
    manage()