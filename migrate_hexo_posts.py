import os
import re
import shutil
from datetime import datetime
from pathlib import Path

# 配置路径
SOURCE_DIR = r"d:\hexo\Sanoka\source\_posts"
TARGET_DIR = r"d:\hexo\academicpages.github.io\_posts"
IMAGES_SOURCE = r"d:\hexo\Sanoka\source\images"
IMAGES_TARGET = r"d:\hexo\academicpages.github.io\images"

def extract_hexo_frontmatter(content):
    """提取 Hexo 的 Front Matter"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        body = content[match.end():]
        return frontmatter, body
    return None, content

def parse_hexo_frontmatter(frontmatter):
    """解析 Hexo Front Matter"""
    data = {}
    
    # 提取 title
    title_match = re.search(r'title:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.MULTILINE)
    data['title'] = title_match.group(1).strip() if title_match else "Untitled"
    
    # 提取 date
    date_match = re.search(r'date:\s*(\d{4}-\d{2}-\d{2})', frontmatter)
    data['date'] = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
    
    # 提取 tags (多行格式)
    tags = []
    tags_section = re.search(r'tags:\s*\n((?:  - .+\n?)+)', frontmatter)
    if tags_section:
        tags = re.findall(r'  - (.+)', tags_section.group(1))
    data['tags'] = tags
    
    # 提取 categories (多行格式)
    categories = []
    cat_section = re.search(r'categories:\s*\n((?:  - .+\n?)+)', frontmatter)
    if cat_section:
        categories = re.findall(r'  - (.+)', cat_section.group(1))
    data['categories'] = categories
    
    # 提取其他字段
    excerpt_match = re.search(r'excerpt:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.MULTILINE)
    if excerpt_match:
        data['excerpt'] = excerpt_match.group(1).strip()
    
    return data

def create_jekyll_frontmatter(data):
    """创建 Jekyll Front Matter"""
    title = data.get('title', 'Untitled').replace("'", "''")
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    tags = data.get('tags', [])
    categories = data.get('categories', [])
    excerpt = data.get('excerpt', '')
    
    # 生成 permalink
    safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-').lower()
    safe_title = safe_title[:50]  # 限制长度
    permalink = f"/posts/{date.replace('-', '/')}/{safe_title}/"
    
    frontmatter = f"""---
title: '{title}'
date: {date}
permalink: {permalink}
"""
    
    if tags:
        frontmatter += "tags:\n"
        for tag in tags:
            frontmatter += f"  - {tag}\n"
    
    if categories:
        frontmatter += "categories:\n"
        for cat in categories:
            frontmatter += f"  - {cat}\n"
    
    if excerpt:
        frontmatter += f"excerpt: '{excerpt}'\n"
    
    frontmatter += "---\n\n"
    
    return frontmatter

def fix_image_paths(body):
    """修复图片路径"""
    # Hexo: ../images/xxx.png -> Jekyll: /images/xxx.png
    body = re.sub(r'\.\./images/', '/images/', body)
    body = re.sub(r'\.\./img/', '/images/', body)
    
    # 相对路径 images/xxx.png -> /images/xxx.png
    body = re.sub(r'(?<![/\w])images/', '/images/', body)
    body = re.sub(r'(?<![/\w])img/', '/images/', body)
    
    return body

def sanitize_filename(title, date):
    """生成安全的文件名"""
    # 移除特殊字符
    safe_title = re.sub(r'[^\w\s-]', '', title)
    safe_title = safe_title.strip().replace(' ', '-').lower()
    safe_title = re.sub(r'-+', '-', safe_title)  # 合并多个连字符
    safe_title = safe_title[:50]  # 限制长度
    
    return f"{date}-{safe_title}.md"

def convert_file(source_path):
    """转换单个文件"""
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取并解析 Front Matter
        hexo_fm, body = extract_hexo_frontmatter(content)
        
        if not hexo_fm:
            print(f"  ⚠️  没有 Front Matter，跳过")
            return None
        
        data = parse_hexo_frontmatter(hexo_fm)
        
        # 创建 Jekyll Front Matter
        jekyll_fm = create_jekyll_frontmatter(data)
        
        # 修复图片路径
        body = fix_image_paths(body)
        
        # 组合新内容
        new_content = jekyll_fm + body
        
        # 生成新文件名
        new_filename = sanitize_filename(data['title'], data['date'])
        
        return new_filename, new_content
        
    except Exception as e:
        print(f"  ❌ 转换失败: {e}")
        return None

def migrate_posts():
    """批量迁移文章"""
    # 创建目标目录
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    # 获取所有 Markdown 文件
    md_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.md')]
    
    print(f"\n{'='*60}")
    print(f"📦 找到 {len(md_files)} 篇文章")
    print(f"{'='*60}\n")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for filename in sorted(md_files):
        print(f"处理: {filename}")
        source_path = os.path.join(SOURCE_DIR, filename)
        
        result = convert_file(source_path)
        
        if result:
            new_filename, new_content = result
            target_path = os.path.join(TARGET_DIR, new_filename)
            
            # 检查文件是否已存在
            if os.path.exists(target_path):
                print(f"  ⚠️  文件已存在，跳过: {new_filename}")
                skip_count += 1
                continue
            
            # 写入新文件
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✅ {filename} -> {new_filename}")
            success_count += 1
        else:
            print(f"  ❌ 转换失败")
            error_count += 1
        
        print()
    
    print(f"{'='*60}")
    print(f"📊 迁移统计:")
    print(f"  ✅ 成功: {success_count}")
    print(f"  ⚠️  跳过: {skip_count}")
    print(f"  ❌ 失败: {error_count}")
    print(f"{'='*60}\n")

def migrate_images():
    """迁移图片文件"""
    if not os.path.exists(IMAGES_SOURCE):
        print("⚠️  源图片文件夹不存在，跳过图片迁移")
        return
    
    print(f"\n{'='*60}")
    print(f"📸 开始迁移图片文件...")
    print(f"{'='*60}\n")
    
    os.makedirs(IMAGES_TARGET, exist_ok=True)
    
    # 复制所有图片文件
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']
    copied_count = 0
    
    for root, dirs, files in os.walk(IMAGES_SOURCE):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                source_file = os.path.join(root, file)
                
                # 保持相对路径结构
                rel_path = os.path.relpath(source_file, IMAGES_SOURCE)
                target_file = os.path.join(IMAGES_TARGET, rel_path)
                
                # 创建目标目录
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                
                # 复制文件
                if not os.path.exists(target_file):
                    shutil.copy2(source_file, target_file)
                    print(f"  ✅ {rel_path}")
                    copied_count += 1
                else:
                    print(f"  ⚠️  已存在，跳过: {rel_path}")
    
    print(f"\n✅ 共复制 {copied_count} 个图片文件\n")

def main():
    print("\n" + "="*60)
    print("🚀 Hexo 到 Jekyll (Academic Pages) 博客迁移工具")
    print("="*60)
    
    # 迁移文章
    migrate_posts()
    
    # 迁移图片
    migrate_images()
    
    print("🎉 迁移完成！")
    print("\n下一步:")
    print("  1. 检查 _posts 文件夹中的文章")
    print("  2. 重启 Jekyll: bundle exec jekyll serve --livereload")
    print("  3. 在浏览器中预览: http://localhost:4000/posts/")
    print()

if __name__ == "__main__":
    main()