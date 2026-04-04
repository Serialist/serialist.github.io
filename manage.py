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
import locale
import unicodedata
import io
import subprocess
from datetime import datetime, date

# ========== 全局常量与正则预编译 ==========
YAML_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TITLE_PATTERN = re.compile(r"^#\s+(.*)$", re.MULTILINE)
IMG_PATTERN = re.compile(r"!\[(.*?)\]\((.*?)\)")
UNDO_CACHE = None

def setup_windows_unicode():
    if sys.platform == "win32":
        # 1. 尝试调用 chcp 65001 确保控制台支持 UTF-8
        subprocess.run("chcp 65001", shell=True, capture_output=True)
        # 2. 强制标准流使用 UTF-8
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

try:
    import curses
except ImportError:
    print("Error: 'curses' library not found.")
    print("Please install it via 'pip install windows-curses' if you are on Windows.")
    sys.exit(1)

locale.setlocale(locale.LC_ALL, "")

# ========== 工具函数 ==========

def get_display_width(s):
    """精确计算东亚文字宽度"""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)

def truncate_by_width(s, max_width):
    """根据显示宽度截断字符串，防止对齐错乱"""
    curr_w = 0
    res = []
    for char in s:
        # 逻辑与原代码保持高度一致
        w = 2 if any([
            "\u4e00" <= char <= "\u9fff",
            "\u3000" <= char <= "\u303f",
            "\uff00" <= char <= "\uffef"
        ]) else 1
        if curr_w + w > max_width:
            break
        res.append(char)
        curr_w += w
    return "".join(res)

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

    def _serialize_meta(self, data):
        if isinstance(data, (datetime, date)):
            return data.isoformat()
        if isinstance(data, dict):
            return {k: self._serialize_meta(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._serialize_meta(i) for i in data]
        return data

    def parse_markdown(self, raw_content):
        metadata, content, ext_title = {}, raw_content, None
        match = YAML_PATTERN.search(raw_content)
        if match:
            try:
                raw_meta = yaml.safe_load(match.group(1)) or {}
                metadata = self._serialize_meta(raw_meta)
                content = raw_content[match.end():]
            except:
                pass
        
        t_match = TITLE_PATTERN.search(content)
        if t_match:
            ext_title = t_match.group(1).strip()
        return metadata, content, ext_title

    def get_file_hash(self, file_path):
        hasher = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()[:12]
        except:
            return "err"

    def process_assets(self, content, md_dir, output_root):
        conf_assets = getattr(self.args, "assets_path", "assets")
        full_assets_path = os.path.abspath(conf_assets)
        os.makedirs(full_assets_path, exist_ok=True)

        def replace_img(match):
            alt, src = match.group(1), match.group(2)
            if src.startswith(("http", "//", "data:")):
                return match.group(0)

            src_path = os.path.normpath(os.path.join(md_dir, src))
            if os.path.exists(src_path):
                ext = os.path.splitext(src)[1]
                new_name = f"{self.get_file_hash(src_path)}{ext}"
                dest_path = os.path.join(full_assets_path, new_name)
                shutil.copy2(src_path, dest_path)

                try:
                    rel_prefix = os.path.relpath(full_assets_path, os.path.abspath(output_root))
                    rel_link = os.path.join(rel_prefix, new_name).replace("\\", "/")
                except ValueError:
                    rel_link = f"{conf_assets}/{new_name}".replace("\\", "/")
                return f"![{alt}]({rel_link})"
            return match.group(0)

        return IMG_PATTERN.sub(replace_img, content)

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
        if not os.path.exists(fpath): return
        
        with open(fpath, "r", encoding="utf-8") as f:
            raw_content = f.read()
        
        meta, clean_content, ext_title = self.parse_markdown(raw_content)
        title = meta.get("title") or ext_title or getattr(self.args, "default_title", "") or os.path.splitext(os.path.basename(fpath))[0]

        existing = next((a for a in self.articles if a.get("path") == fpath), None)
        item = existing if existing else {"id": uuid.uuid4().hex[:8], "path": fpath}

        item.update(meta)
        item.setdefault("title", title)
        for attr in ["author", "email"]:
            if attr not in item and hasattr(self.args, attr):
                item[attr] = getattr(self.args, attr)
        
        today = datetime.now().strftime("%Y-%m-%d")
        item.setdefault("created", today)
        item["modified"] = today

        proc_content = self.process_assets(clean_content, os.path.dirname(fpath), self.args.output)
        os.makedirs(self.args.output, exist_ok=True)
        with open(os.path.join(self.args.output, f"{item['id']}.md"), "w", encoding="utf-8") as f:
            f.write(proc_content)

        if not existing:
            self.articles.append(item)

    def add_logic(self):
        targets = self.args.input if isinstance(self.args.input, list) else [self.args.input]
        all_files = []
        for target in targets:
            if os.path.isdir(target):
                for r, _, fs in os.walk(target) if self.args.recursive else [(target, [], os.listdir(target))]:
                    all_files.extend([os.path.join(r, f) for f in fs if f.endswith(".md")])
            elif os.path.isfile(target) and target.endswith(".md"):
                all_files.append(target)

        unique_files = list(set(os.path.abspath(f) for f in all_files))
        for f in unique_files:
            self.add_or_update(f)
        self.save_json()
        print(f"Processed {len(unique_files)} unique files.")

    def create_article(self, filename):
        if not filename.endswith(".md"): filename += ".md"
        input_dir = self.args.input[0] if (isinstance(self.args.input, list) and os.path.isdir(self.args.input[0])) else "input"
        os.makedirs(input_dir, exist_ok=True)
        target_path = os.path.join(input_dir, filename)
        if os.path.exists(target_path): return False, "File exists!"
        
        now = datetime.now().strftime("%Y-%m-%d")
        template = f"---\ntitle: {os.path.splitext(filename)[0]}\ncreated: {now}\nauthor: {getattr(self.args, 'author', 'admin')}\ntag: []\n---\n\n# New Article\n"
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(template)
        self.add_or_update(target_path)
        self.save_json()
        return True, target_path

# ========== TUI 实现 ==========

class ArticleTUI:
    def __init__(self, manager):
        self.mgr = manager
        self.cursor, self.offset = 0, 0
        self.selected = set()
        self.multi_mode = False
        self.sort_key = "created"
        self.query = ""
        self.status = "Ready"
        self.menu_state = "MAIN"
        self.opt_idx = 0
        self.pending_action = None

        self.menus = {
            "MAIN": [("Attr(1)", "1"), ("Del(2)", "2"), ("Upd(3)", "3"), ("Find(4)", "4"), ("All(5)", "5"), ("Create(n)", "n")],
            "ATTR": [("Title(1)", "title"), ("Author(2)", "author"), ("Created(3)", "created"), ("Modified(4)", "modified"), ("Tag(5)", "tag"), ("Path(6)", "path")],
            "CONFIRM": [("YES(y)", "y"), ("NO(n)", "n")]
        }

    def get_list(self):
        lst = [a for a in self.mgr.articles if self.query.lower() in str(a).lower()]
        lst.sort(key=lambda x: str(x.get(self.sort_key, "")), reverse=True)
        return lst

    def edit_string(self, stdscr, prompt, initial_text=""):
        curses.curs_set(1)
        h, w = stdscr.getmaxyx()
        s = list(str(initial_text))
        pos = len(s)
        
        while True:
            stdscr.move(h - 1, 0)
            stdscr.addstr(" " * (w - 1)) 
            display_prefix = f"{prompt}: "
            draw_text = truncate_by_width(display_prefix + "".join(s), w - 2)
            
            try:
                stdscr.addstr(h - 1, 0, draw_text)
                target_x = get_display_width(display_prefix) + get_display_width("".join(s[:pos]))
                stdscr.move(h - 1, min(target_x, w - 1))
            except: pass

            stdscr.refresh()
            try:
                ch = stdscr.get_wch()
            except: continue

            if ch in ["\n", "\r", 10, 13]: break
            elif ch == "\x1b": curses.curs_set(0); return None
            elif ch == curses.KEY_LEFT: pos = max(0, pos - 1)
            elif ch == curses.KEY_RIGHT: pos = min(len(s), pos + 1)
            elif ch in [curses.KEY_BACKSPACE, "\b", "\x7f", "\x08"]:
                if pos > 0: s.pop(pos - 1); pos -= 1
            elif isinstance(ch, str) and ch.isprintable():
                s.insert(pos, ch); pos += 1
                
        curses.curs_set(0)
        return "".join(s)

    def draw(self, stdscr):
        h, w = stdscr.getmaxyx()
        stdscr.erase()
        articles = self.get_list()

        # 列表绘制逻辑
        for i in range(h - 2):
            idx = i + self.offset
            if idx >= len(articles): break
            art = articles[idx]
            is_cur, is_sel = (idx == self.cursor), (art["id"] in self.selected)
            char = "X" if is_sel else (">" if is_cur else " ")

            if is_cur:
                stdscr.attron(curses.A_BOLD)
                if is_sel: stdscr.attron(curses.A_REVERSE)
            elif is_sel: stdscr.attron(curses.A_DIM)

            c_d, m_d = art.get("created", "")[:10], art.get("modified", "")[:10]
            title_text = truncate_by_width(art.get("title", "Untitle"), max(0, w - 35))
            padding = " " * (max(0, w - 35) - get_display_width(title_text))

            try:
                stdscr.addstr(i, 0, f"{char} | {title_text}{padding} | {c_d} | {m_d}"[:w-1])
            except: pass
            stdscr.attroff(curses.A_BOLD | curses.A_REVERSE | curses.A_DIM)

        # 状态栏绘制
        if curses.has_colors(): stdscr.attron(curses.color_pair(1))
        st_l = truncate_by_width(f" {self.status}", max(0, w - 40))
        st_r = f" Total: {len(articles)} | {self.sort_key} | Multi:{'ON' if self.multi_mode else 'OFF'} "
        try:
            stdscr.addstr(h - 2, 0, " " * (w - 1))
            stdscr.addstr(h - 2, 0, st_l)
            if w > get_display_width(st_r):
                stdscr.addstr(h - 2, w - get_display_width(st_r), st_r)
        except: pass
        if curses.has_colors(): stdscr.attroff(curses.color_pair(1))

        # 菜单绘制
        try:
            stdscr.move(h - 1, 0)
            stdscr.clrtoeol()
            opts = self.menus.get(self.menu_state, self.menus["MAIN"])
            x_offset = 1
            for i, (name, _) in enumerate(opts):
                if x_offset + get_display_width(name) >= w: break
                if i == self.opt_idx: stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(h - 1, x_offset, name)
                stdscr.attroff(curses.A_REVERSE)
                x_offset += get_display_width(name) + 2
            
            hint = "ESC:Back Ctrl+Z:Undo "
            if x_offset + get_display_width(hint) < w:
                stdscr.addstr(h - 1, w - get_display_width(hint), hint)
        except: pass
        stdscr.refresh()

    def do_delete(self):
        global UNDO_CACHE
        UNDO_CACHE = list(self.mgr.articles)
        for uid in list(self.selected):
            out_p = os.path.normpath(os.path.join(self.mgr.args.output, f"{uid}.md"))
            if os.path.exists(out_p): os.remove(out_p)
        self.mgr.articles = [a for a in self.mgr.articles if a["id"] not in self.selected]
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
            if not self.selected: self.status = "Select article first!"
            else: self.menu_state, self.opt_idx, self.status = "ATTR", 0, "Edit field..."
        elif key == "2":
            if not self.selected: self.status = "Nothing selected!"
            else: self.status, self.menu_state, self.opt_idx, self.pending_action = f"CONFIRM: Delete {len(self.selected)} items?", "CONFIRM", 1, self.do_delete
        elif key == "3":
            if not self.selected: self.status = "Select first!"
            else:
                for uid in self.selected:
                    art = next(a for a in self.mgr.articles if a["id"] == uid)
                    self.mgr.add_or_update(art["path"])
                self.mgr.save_json(); self.status = "Updated."
        elif key == "4":
            q = self.edit_string(stdscr, "Search")
            if q is not None: self.query, self.cursor = q, 0
        elif key == "5":
            all_ids = {a["id"] for a in self.get_list()}
            self.selected = set() if self.selected == all_ids else all_ids

    def run(self, stdscr):
        global UNDO_CACHE
        curses.curs_set(0)
        if curses.has_colors(): curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        stdscr.keypad(True)
        
        while True:
            self.draw(stdscr)
            ch = stdscr.getch()
            h, _ = stdscr.getmaxyx()
            
            if ch == 27: # ESC
                if self.menu_state != "MAIN": self.menu_state, self.opt_idx, self.status = "MAIN", 0, "Ready"
                else: break
            elif ch in (curses.KEY_LEFT, curses.KEY_RIGHT):
                opts_len = len(self.menus[self.menu_state])
                step = -1 if ch == curses.KEY_LEFT else 1
                self.opt_idx = (self.opt_idx + step) % opts_len
            elif ch in (10, 13): # Enter
                if self.menu_state == "CONFIRM":
                    if self.menus["CONFIRM"][self.opt_idx][1] == "y": self.pending_action()
                    self.menu_state, self.opt_idx = "MAIN", 0
                elif self.menu_state == "ATTR":
                    self._perform_attr_edit(stdscr, self.menus["ATTR"][self.opt_idx][1])
                else:
                    self.handle_action(stdscr, self.menus["MAIN"][self.opt_idx][1])
            elif self.menu_state == "MAIN":
                self._handle_main_input(stdscr, ch, h)
            elif self.menu_state == "CONFIRM":
                if ch in (ord('y'), ord('Y')): self.pending_action(); self.menu_state, self.opt_idx = "MAIN", 0
                elif ch in (ord('n'), ord('N')): self.menu_state, self.opt_idx = "MAIN", 0
            elif self.menu_state == "ATTR":
                if ord("1") <= ch <= ord("6"): self._perform_attr_edit(stdscr, self.menus["ATTR"][ch - ord("1")][1])

    def _perform_attr_edit(self, stdscr, field):
        uid = list(self.selected)[0]
        art = next(a for a in self.mgr.articles if a["id"] == uid)
        curr = ",".join(art.get(field, [])) if field == "tag" else str(art.get(field, ""))
        new_v = self.edit_string(stdscr, f"Edit {field}", curr)
        if new_v is not None:
            art[field] = [x.strip() for x in new_v.split(",")] if field == "tag" else new_v
            self.mgr.save_json(); self.status = "Updated."

    def _handle_main_input(self, stdscr, ch, h):
        global UNDO_CACHE
        if ch == curses.KEY_UP:
            if self.cursor > 0: self.cursor -= 1
            if self.cursor < self.offset: self.offset -= 1
        elif ch == curses.KEY_DOWN:
            arts = self.get_list()
            if self.cursor < len(arts) - 1: self.cursor += 1
            if self.cursor >= self.offset + (h - 2): self.offset += 1
        elif ch == 26: # Ctrl+Z
            if UNDO_CACHE: self.mgr.articles = list(UNDO_CACHE); self.mgr.save_json(); self.status = "Undo."
        elif ch in (ord("m"), ord("M"), 9):
            self.multi_mode = not self.multi_mode
            if not self.multi_mode: self.selected.clear()
        elif ch == ord(" "):
            arts = self.get_list()
            if arts:
                uid = arts[self.cursor]["id"]
                if self.multi_mode:
                    if uid in self.selected: self.selected.remove(uid)
                    else: self.selected.add(uid)
                else: self.selected = {uid} if uid not in self.selected else set()
        elif ch in (ord("`"), ord("~")):
            keys = ["title", "created", "modified", "author", "tag"]
            self.sort_key = keys[(keys.index(self.sort_key) + 1) % len(keys)]
        elif ord("1") <= ch <= ord("5"): self.handle_action(stdscr, chr(ch))
        elif ch in (ord("n"), ord("N")): self.handle_action(stdscr, "n")

def main():
    setup_windows_unicode()
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--config", default="manage.yaml")
    pre_args, _ = pre_parser.parse_known_args()

    conf = {}
    if os.path.exists(pre_args.config):
        try:
            with open(pre_args.config, "r", encoding="utf-8") as f:
                conf = yaml.safe_load(f) or {}
        except: pass

    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["add", "manage"], nargs="?", default="manage")
    parser.add_argument("--config", default="manage.yaml")
    parser.add_argument("-r", "--recursive", action="store_true")
    parser.add_argument("-i", "--input", nargs="+", default=conf.get("input_path", ["input"]))
    parser.add_argument("-o", "--output", default=conf.get("output_path", "./article"))
    parser.add_argument("-l", "--list", default=conf.get("list_path", "./article-list.json"))
    
    # 隐藏参数
    for attr, d_val in [("assets_path", "assets"), ("author", "admin"), ("email", ""), ("title", "")]:
        parser.add_argument(f"--{attr if attr != 'title' else 'default_title'}", 
                            default=conf.get(attr, d_val), help=argparse.SUPPRESS)

    args = parser.parse_args()
    for p in [os.path.dirname(os.path.abspath(args.list)), args.output]:
        if p and not os.path.exists(p): os.makedirs(p)

    bm = BlogManager(args)
    if args.mode == "add": bm.add_logic()
    else: curses.wrapper(lambda s: ArticleTUI(bm).run(s))

if __name__ == "__main__":
    main()