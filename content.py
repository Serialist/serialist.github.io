import os

def generate_file_list(root_dir, output_file="文章列表.md"):
    """
    遍历指定文件夹下的所有文件，生成Markdown格式的文件列表
    特性：
    1. 链接路径包含根文件夹名
    2. 文件夹标题最多支持6层（######）
    3. 每个条目之间有独立空行
    
    Args:
        root_dir: 要遍历的根文件夹路径
        output_file: 输出的markdown文件名
    """
    # 确保根目录路径格式正确，并提取根文件夹名称
    root_dir = os.path.abspath(root_dir)
    root_folder_name = os.path.basename(root_dir)  # 获取根文件夹名
    md_content = ["# 文章列表\n\n"]  # 初始化Markdown内容，末尾加空行
    
    def traverse_directory(current_dir, relative_path="", level=1):
        """
        递归遍历目录，生成对应的Markdown内容
        
        Args:
            current_dir: 当前遍历的目录路径
            relative_path: 相对于根目录的路径
            level: 当前文件夹层级（根文件夹为1级）
        """
        # 获取当前目录下的所有文件和文件夹，并排序（文件夹在前，文件在后）
        entries = sorted(os.listdir(current_dir), key=lambda x: (os.path.isfile(os.path.join(current_dir, x)), x))
        
        for entry in entries:
            entry_path = os.path.join(current_dir, entry)
            entry_relative_path = os.path.join(relative_path, entry) if relative_path else entry
            
            # 如果是文件夹，且层级≤6，添加对应级别的标题并递归遍历
            if os.path.isdir(entry_path):
                if level <= 6:
                    # 根据层级生成对应级别的Markdown标题（1级=##，6级=#######）
                    title_level = "#" * (level + 1)
                    md_content.append(f"{title_level} {entry}\n\n")  # 标题后加空行
                # 递归遍历子文件夹，层级+1
                traverse_directory(entry_path, entry_relative_path, level + 1)
            # 如果是文件，添加链接项
            elif os.path.isfile(entry_path):
                # 获取文件名（不含扩展名）作为title
                title = os.path.splitext(entry)[0]
                # 构建完整链接路径：根文件夹名/相对路径，统一用/分隔
                full_link_path = os.path.join(root_folder_name, entry_relative_path).replace("\\", "/")
                md_link = f"[{title}](/?p={full_link_path})"
                md_content.append(f"{md_link}\n\n")  # 链接后加空行
    
    # 开始遍历根目录
    traverse_directory(root_dir)
    
    # 去除末尾多余的空行（可选，让文件结尾更整洁）
    if md_content and md_content[-1] == "\n\n":
        md_content.pop()
    
    # 将内容写入Markdown文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("".join(md_content))
    
    print(f"文件列表已生成到: {os.path.abspath(output_file)}")

# 示例使用
if __name__ == "__main__":
    # 请修改这里的文件夹路径为你实际的blog文件夹路径
    blog_folder = "./page/blog"  # 相对路径，也可以使用绝对路径如 "C:/Users/xxx/blog"
    
    # 调用函数生成文件列表
    generate_file_list(blog_folder, output_file="./page/blog.md")

    os.system("pause")
    
    input("按回车键退出...")
