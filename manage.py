import os
import json
import hashlib
import shutil
import re
import argparse
import uuid
import yaml
import signal
import sys
from datetime import datetime, date

# 尝试导入 curses，针对 Windows 提供安装建议
try:
    import curses
except ImportError:
    print("Error: 'curses' library not found.")
    print("Please install it via 'pip install windows-curses' if you are on Windows.")
    sys.exit(1)

# ========== 全局撤销缓存 ==========
UNDO_CACHE = None


def signal_handler(sig, frame):
    try:
        curses.endwin()
    except:
        pass
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# ========== 核心逻辑类 ==========


class BlogManager:
    def __init__(self, args):
        self.args = args
        self.articles = []
        self.load_json()

    def _serialize_yaml_meta(self, data):
        if isinstance(data, (datetime, date)):
            return data.isoformat()
        elif isinstance(data, dict):
            return {k: self._serialize_yaml_meta(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_yaml_meta(i) for i in data]
        return data

    def parse_markdown(self, raw_content):
        metadata = {}
        content = raw_content
        yaml_pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.search(yaml_pattern, raw_content, re.DOTALL)
        if match:
            try:
                raw_meta = yaml.safe_load(match.group(1)) or {}
                metadata = self._serialize_yaml_meta(raw_meta)
                content = raw_content[match.end() :]
            except:
                pass

        extracted_title = None
        title_match = re.search(r"^#\s+(.*)$", content, re.MULTILINE)
        if title_match:
            extracted_title = title_match.group(1).strip()
        return metadata, content, extracted_title

    def get_file_hash(self, file_path):
        hasher = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()[:12]
        except:
            return "err"

    def process_assets(self, content, md_dir, output_root):
        # 1. 获取配置中的 assets_path（如 "./assets/blog"）
        conf_assets = getattr(self.args, "assets_path", "assets")

        # 2. 核心逻辑：无论用户填什么，都将其视为相对于“执行命令时路径”的路径
        # 使用 os.path.abspath 确保它是基于当前 shell 运行位置的绝对路径
        full_assets_path = os.path.abspath(conf_assets)

        # 3. 确保目录存在
        os.makedirs(full_assets_path, exist_ok=True)

        img_pattern = r"!\[(.*?)\]\((.*?)\)"

        def replace_img(match):
            alt, src = match.group(1), match.group(2)
            if src.startswith(("http", "//", "data:")):
                return match.group(0)

            # 这里的 md_dir 已经是 abspath(fpath) 的 dirname，所以没问题
            src_path = os.path.normpath(os.path.join(md_dir, src))

            if os.path.exists(src_path):
                ext = os.path.splitext(src)[1]
                new_name = f"{self.get_file_hash(src_path)}{ext}"
                dest_path = os.path.join(full_assets_path, new_name)

                # 复制文件到执行路径下的 assets 目录
                shutil.copy2(src_path, dest_path)

                # --- 重点：Markdown 里的链接怎么写？ ---
                # 如果你的网页渲染器要求图片相对于 dist 目录，
                # 我们需要计算 full_assets_path 相对于 output_root 的相对路径
                try:
                    rel_link_prefix = os.path.relpath(
                        full_assets_path, os.path.abspath(output_root)
                    )
                    rel_link = os.path.join(rel_link_prefix, new_name).replace(
                        "\\", "/"
                    )
                except ValueError:
                    # 如果跨了盘符（Windows），relpath 会报错，此时退回到配置值
                    rel_link = f"{conf_assets}/{new_name}".replace("\\", "/")

                return f"![{alt}]({rel_link})"
            return match.group(0)

        return re.sub(img_pattern, replace_img, content)

    def load_json(self):
        if os.path.exists(self.args.list):
            try:
                with open(self.args.list, "r", encoding="utf-8") as f:
                    self.articles = json.load(f)
            except:
                self.articles = []

    def save_json(self):
        with open(self.args.list, "w", encoding="utf-8") as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=4)

    def add_or_update(self, fpath):
        fpath = os.path.abspath(fpath)
        if not os.path.exists(fpath):
            return
        with open(fpath, "r", encoding="utf-8") as f:
            raw_content = f.read()
        meta, clean_content, ext_title = self.parse_markdown(raw_content)

        # 优先级：YAML元数据 > 正文H1 > 配置文件默认Title > 文件名
        default_title = getattr(self.args, "default_title", None)
        title = (
            meta.get("title")
            or ext_title
            or default_title
            or os.path.splitext(os.path.basename(fpath))[0]
        )

        existing = next((a for a in self.articles if a.get("path") == fpath), None)
        item = existing if existing else {"id": uuid.uuid4().hex[:8], "path": fpath}

        item.update(meta)
        if "title" not in item:
            item["title"] = title
        if "author" not in item and hasattr(self.args, "author"):
            item["author"] = self.args.author
        if "email" not in item and hasattr(self.args, "email"):
            item["email"] = self.args.email

        if "created" not in item:
            item["created"] = datetime.now().strftime("%Y-%m-%d")
        item["modified"] = datetime.now().strftime("%Y-%m-%d")

        proc_content = self.process_assets(
            clean_content, os.path.dirname(fpath), self.args.output
        )
        out_file = os.path.join(self.args.output, f"{item['id']}.md")
        os.makedirs(self.args.output, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(proc_content)

        if not existing:
            self.articles.append(item)

    def add_logic(self):
        targets = self.args.input
        # 确保 targets 是列表（处理单字符串默认值的情况）
        if isinstance(targets, str):
            targets = [targets]

        all_files = []
        for target in targets:
            if os.path.isdir(target):
                if self.args.recursive:
                    for r, _, fs in os.walk(target):
                        for f in fs:
                            if f.endswith(".md"):
                                all_files.append(os.path.join(r, f))
                else:
                    files = [
                        os.path.join(target, f)
                        for f in os.listdir(target)
                        if f.endswith(".md")
                    ]
                    all_files.extend(files)
            elif os.path.isfile(target):
                if target.endswith(".md"):
                    all_files.append(target)

        # 去重（防止重复传入同一个文件）
        unique_files = list(set(os.path.abspath(f) for f in all_files))

        for f in unique_files:
            self.add_or_update(f)

        self.save_json()
        print(f"Processed {len(unique_files)} unique files.")

    def create_article(self, filename):
        if not filename.endswith(".md"):
            filename += ".md"
        input_dir = self.args.input if os.path.isdir(self.args.input) else "input"
        os.makedirs(input_dir, exist_ok=True)
        target_path = os.path.join(input_dir, filename)
        if os.path.exists(target_path):
            return False, "File exists!"
        now = datetime.now().strftime("%Y-%m-%d")

        author = getattr(self.args, "author", "admin")
        title = os.path.splitext(filename)[0]

        template = f"---\ntitle: {title}\ncreated: {now}\nauthor: {author}\ntag: []\n---\n\n# New Article\n"
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(template)
        self.add_or_update(target_path)
        self.save_json()
        return True, target_path


# ========== TUI 实现 ==========


class ArticleTUI:
    def __init__(self, manager):
        self.mgr = manager
        self.cursor = 0
        self.offset = 0
        self.selected = set()
        self.multi_mode = False
        self.sort_key = "created"
        self.query = ""
        self.status = "Ready"

        self.main_options = [
            ("Attr(1)", "1"),
            ("Del(2)", "2"),
            ("Upd(3)", "3"),
            ("Find(4)", "4"),
            ("All(5)", "5"),
            ("Create(n)", "n"),
        ]
        self.attr_options = [
            ("Title(1)", "title"),
            ("Author(2)", "author"),
            ("Created(3)", "created"),
            ("Modified(4)", "modified"),
            ("Tag(5)", "tag"),
            ("Path(6)", "path"),
        ]
        self.confirm_options = [("YES(y)", "y"), ("NO(n)", "n")]

        self.opt_idx = 0
        self.menu_state = "MAIN"
        self.pending_action = None

    def get_list(self):
        lst = [a for a in self.mgr.articles if self.query.lower() in str(a).lower()]
        lst.sort(key=lambda x: str(x.get(self.sort_key, "")), reverse=True)
        return lst

    def edit_string(self, stdscr, prompt, initial_text=""):
        curses.curs_set(1)
        h, w = stdscr.getmaxyx()
        s = list(initial_text)
        pos = len(s)
        while True:
            stdscr.move(h - 1, 0)
            stdscr.clrtoeol()
            display = f"{prompt}: {''.join(s)}"
            try:
                stdscr.addstr(h - 1, 0, display[: w - 1])
                stdscr.move(h - 1, min(w - 1, len(prompt) + 2 + pos))
            except:
                pass
            ch = stdscr.getch()
            if ch in [10, 13]:
                break
            elif ch == 27:
                curses.curs_set(0)
                return None
            elif ch == curses.KEY_LEFT:
                pos = max(0, pos - 1)
            elif ch == curses.KEY_RIGHT:
                pos = min(len(s), pos + 1)
            elif ch in [curses.KEY_BACKSPACE, 8, 127]:
                if pos > 0:
                    s.pop(pos - 1)
                    pos -= 1
            elif 32 <= ch <= 126:
                s.insert(pos, chr(ch))
                pos += 1
        curses.curs_set(0)
        return "".join(s)

    def draw(self, stdscr):
        h, w = stdscr.getmaxyx()
        stdscr.erase()
        articles = self.get_list()

        reserved_w = 35

        for i in range(h - 2):
            idx = i + self.offset
            if idx >= len(articles):
                break
            art = articles[idx]
            is_cur = idx == self.cursor
            is_sel = art["id"] in self.selected
            char = "X" if is_sel else (">" if is_cur else " ")

            if is_cur:
                stdscr.attron(curses.A_BOLD)
                if is_sel:
                    stdscr.attron(curses.A_REVERSE)
            elif is_sel:
                stdscr.attron(curses.A_DIM)

            c_d, m_d = art.get("created", "")[:10], art.get("modified", "")[:10]

            title_w = max(0, w - reserved_w)
            title_text = art.get("title", "Untitle")[:title_w].ljust(title_w)

            line_str = f"{char} | {title_text} | {c_d} | {m_d}"
            try:
                stdscr.addstr(i, 0, line_str[: w - 1])
            except:
                pass
            stdscr.attroff(curses.A_BOLD | curses.A_REVERSE | curses.A_DIM)

        # 状态栏
        if curses.has_colors():
            stdscr.attron(curses.color_pair(1))
        st_left = f" {self.status}"
        st_right = f" Total: {len(articles)} | {self.sort_key} | Multi:{'ON' if self.multi_mode else 'OFF'} "
        try:
            stdscr.addstr(h - 2, 0, " " * (w - 1))
            stdscr.addstr(h - 2, 0, st_left[: max(0, w - len(st_right) - 1)])
            if w > len(st_right):
                stdscr.addstr(h - 2, w - len(st_right), st_right)
        except:
            pass
        if curses.has_colors():
            stdscr.attroff(curses.color_pair(1))

        # 底部选项
        try:
            stdscr.move(h - 1, 0)
            stdscr.clrtoeol()
            opts = self.main_options
            if self.menu_state == "ATTR":
                opts = self.attr_options
            elif self.menu_state == "CONFIRM":
                opts = self.confirm_options

            x_offset = 1
            for i, (name, key) in enumerate(opts):
                if x_offset + len(name) >= w:
                    break
                if i == self.opt_idx:
                    stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(h - 1, x_offset, name)
                stdscr.attroff(curses.A_REVERSE)
                x_offset += len(name) + 2

            hint = "ESC:Back Ctrl+Z:Undo "
            if x_offset + len(hint) < w:
                stdscr.addstr(h - 1, w - len(hint), hint)
        except:
            pass
        stdscr.refresh()

    def request_confirm(self, msg, action):
        self.status = f"CONFIRM: {msg}"
        self.menu_state = "CONFIRM"
        self.opt_idx = 1
        self.pending_action = action

    def do_delete(self):
        global UNDO_CACHE
        UNDO_CACHE = list(self.mgr.articles)
        for uid in list(self.selected):
            out_p = os.path.normpath(os.path.join(self.mgr.args.output, f"{uid}.md"))
            if os.path.exists(out_p):
                os.remove(out_p)
        self.mgr.articles = [
            a for a in self.mgr.articles if a["id"] not in self.selected
        ]
        self.selected.clear()
        self.mgr.save_json()
        self.status = "Deleted."

    def handle_action(self, stdscr, key):
        if key == "n":
            fname = self.edit_string(stdscr, "New Filename")
            if fname:
                success, info = self.mgr.create_article(fname)
                self.status = f"Created: {info}" if success else info
        elif key == "1":
            if not self.selected:
                self.status = "Select article first!"
                return
            self.menu_state = "ATTR"
            self.opt_idx = 0
            self.status = "Edit field..."
        elif key == "2":
            if not self.selected:
                self.status = "Nothing selected!"
                return
            self.request_confirm(f"Delete {len(self.selected)} items?", self.do_delete)
        elif key == "3":
            if not self.selected:
                self.status = "Select first!"
                return
            for uid in self.selected:
                art = next(a for a in self.mgr.articles if a["id"] == uid)
                self.mgr.add_or_update(art["path"])
            self.mgr.save_json()
            self.status = "Updated."
        elif key == "4":
            q = self.edit_string(stdscr, "Search")
            if q is not None:
                self.query = q
                self.cursor = 0
        elif key == "5":
            all_ids = {a["id"] for a in self.get_list()}
            self.selected = set() if self.selected == all_ids else all_ids

    def run(self, stdscr):
        global UNDO_CACHE
        curses.curs_set(0)
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        stdscr.keypad(True)
        while True:
            self.draw(stdscr)
            ch = stdscr.getch()
            if ch == 27:
                if self.menu_state != "MAIN":
                    self.menu_state = "MAIN"
                    self.opt_idx = 0
                    self.status = "Ready"
                else:
                    break
            elif ch == curses.KEY_LEFT:
                cur_len = len(
                    self.confirm_options
                    if self.menu_state == "CONFIRM"
                    else (
                        self.attr_options
                        if self.menu_state == "ATTR"
                        else self.main_options
                    )
                )
                self.opt_idx = (self.opt_idx - 1) % cur_len
            elif ch == curses.KEY_RIGHT:
                cur_len = len(
                    self.confirm_options
                    if self.menu_state == "CONFIRM"
                    else (
                        self.attr_options
                        if self.menu_state == "ATTR"
                        else self.main_options
                    )
                )
                self.opt_idx = (self.opt_idx + 1) % cur_len
            elif ch in [10, 13]:
                if self.menu_state == "CONFIRM":
                    if self.confirm_options[self.opt_idx][1] == "y":
                        self.pending_action()
                    self.menu_state = "MAIN"
                    self.opt_idx = 0
                elif self.menu_state == "ATTR":
                    uid = list(self.selected)[0]
                    art = next(a for a in self.mgr.articles if a["id"] == uid)
                    field = self.attr_options[self.opt_idx][1]
                    curr = (
                        ",".join(art.get(field, []))
                        if field == "tag"
                        else str(art.get(field, ""))
                    )
                    new_v = self.edit_string(stdscr, f"Edit {field}", curr)
                    if new_v is not None:
                        art[field] = (
                            [x.strip() for x in new_v.split(",")]
                            if field == "tag"
                            else new_v
                        )
                        self.mgr.save_json()
                        self.status = "Updated."
                else:
                    self.handle_action(stdscr, self.main_options[self.opt_idx][1])
            elif self.menu_state == "CONFIRM":
                if ch in [ord("y"), ord("Y")]:
                    self.pending_action()
                    self.menu_state = "MAIN"
                    self.opt_idx = 0
                elif ch in [ord("n"), ord("N")]:
                    self.menu_state = "MAIN"
                    self.opt_idx = 0
            elif self.menu_state == "ATTR":
                if ord("1") <= ch <= ord("6"):
                    field = self.attr_options[ch - ord("1")][1]
                    uid = list(self.selected)[0]
                    art = next(a for a in self.mgr.articles if a["id"] == uid)
                    curr = (
                        ",".join(art.get(field, []))
                        if field == "tag"
                        else str(art.get(field, ""))
                    )
                    new_v = self.edit_string(stdscr, f"Edit {field}", curr)
                    if new_v is not None:
                        art[field] = (
                            [x.strip() for x in new_v.split(",")]
                            if field == "tag"
                            else new_v
                        )
                        self.mgr.save_json()
                        self.status = "Updated."
            else:
                if ch == curses.KEY_UP:
                    if self.cursor > 0:
                        self.cursor -= 1
                    if self.cursor < self.offset:
                        self.offset -= 1
                elif ch == curses.KEY_DOWN:
                    articles = self.get_list()
                    if self.cursor < len(articles) - 1:
                        self.cursor += 1
                    if self.cursor >= self.offset + (curses.LINES - 2):
                        self.offset += 1
                elif ch == 26:
                    if UNDO_CACHE:
                        self.mgr.articles = list(UNDO_CACHE)
                        self.mgr.save_json()
                        self.status = "Undo."
                elif ch in [ord("m"), ord("M"), 9]:
                    self.multi_mode = not self.multi_mode
                    if not self.multi_mode:
                        self.selected.clear()
                elif ch == ord(" "):
                    articles = self.get_list()
                    if articles:
                        uid = articles[self.cursor]["id"]
                        if self.multi_mode:
                            if uid in self.selected:
                                self.selected.remove(uid)
                            else:
                                self.selected.add(uid)
                        else:
                            self.selected = {uid} if uid not in self.selected else set()
                elif ch in [ord("`"), ord("~")]:
                    keys = ["title", "created", "modified", "author", "tag"]
                    self.sort_key = keys[(keys.index(self.sort_key) + 1) % len(keys)]
                elif ord("1") <= ch <= ord("5"):
                    self.handle_action(stdscr, chr(ch))
                elif ch in [ord("n"), ord("N")]:
                    self.handle_action(stdscr, "n")


def main():
    # 默认配置路径
    default_conf_path = "manage.yaml"

    # 预解析，为了获取 config 文件路径
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--config", default=default_conf_path)
    pre_args, _ = pre_known = pre_parser.parse_known_args()

    # 读取配置文件
    conf = {}
    if os.path.exists(pre_args.config):
        try:
            with open(pre_args.config, "r", encoding="utf-8") as f:
                conf = yaml.safe_load(f) or {}
        except:
            pass

    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["add", "manage"], nargs="?", default="manage")
    parser.add_argument(
        "--config", default=default_conf_path, help="Path to config yaml"
    )
    parser.add_argument("-r", "--recursive", action="store_true")

    # 从配置文件读取默认值
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        default=conf.get("input_path", ["input"]),
        help="One or more input files or directories",
    )
    parser.add_argument("-o", "--output", default=conf.get("output_path", "./article"))
    parser.add_argument(
        "-l", "--list", default=conf.get("list_path", "./article-list.json")
    )

    # 附加配置项（不在原 argparse 中但逻辑需要）
    parser.add_argument(
        "--assets_path",
        default=conf.get("assets_path", "assets"),
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--author", default=conf.get("author", "admin"), help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--email", default=conf.get("email", ""), help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--default_title", default=conf.get("title", ""), help=argparse.SUPPRESS
    )

    args = parser.parse_args()

    for p in [os.path.dirname(os.path.abspath(args.list)), args.output]:
        if p and not os.path.exists(p):
            os.makedirs(p)

    bm = BlogManager(args)
    if args.mode == "add":
        bm.add_logic()
    else:
        curses.wrapper(lambda s: ArticleTUI(bm).run(s))


if __name__ == "__main__":
    main()
