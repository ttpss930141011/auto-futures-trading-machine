import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
import threading

from src.interactor.use_cases.user_login_use_case import UserLoginUseCase


class LoginDialog:
    def __init__(self, parent: tk.Tk, login_use_case: UserLoginUseCase):
        self.parent = parent
        self.login_use_case = login_use_case
        self.result: Optional[Dict[str, Any]] = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("登入")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self._center_window()
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create UI
        self._create_ui()
        
        # Focus on username field
        self.username_entry.focus()
    
    def _center_window(self):
        """將對話框置中"""
        self.dialog.update_idletasks()
        
        # Get window dimensions
        window_width = self.dialog.winfo_width()
        window_height = self.dialog.winfo_height()
        
        # Get screen dimensions
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _create_ui(self):
        """創建登入界面"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="PFCF 系統登入", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Username
        ttk.Label(form_frame, text="帳號:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(form_frame, text="密碼:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Environment
        ttk.Label(form_frame, text="環境:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.env_var = tk.StringVar(value="test")
        env_frame = ttk.Frame(form_frame)
        env_frame.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Radiobutton(
            env_frame, 
            text="測試環境", 
            variable=self.env_var, 
            value="test"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            env_frame, 
            text="正式環境", 
            variable=self.env_var, 
            value="prod"
        ).pack(side=tk.LEFT)
        
        # Remember login
        self.remember_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            form_frame, 
            text="記住登入資訊", 
            variable=self.remember_var
        ).grid(row=3, column=1, sticky=tk.W, pady=10, padx=(10, 0))
        
        # Status label
        self.status_label = ttk.Label(form_frame, text="", foreground="red")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.login_button = ttk.Button(
            button_frame, 
            text="登入", 
            command=self._on_login,
            style="Accent.TButton"
        )
        self.login_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_button = ttk.Button(
            button_frame, 
            text="取消", 
            command=self._on_cancel
        )
        cancel_button.pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.dialog.bind("<Return>", lambda e: self._on_login())
        self.dialog.bind("<Escape>", lambda e: self._on_cancel())
    
    def _on_login(self):
        """處理登入動作"""
        # Get input values
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        environment = self.env_var.get()
        
        # Validate inputs
        if not username:
            self._show_error("請輸入帳號")
            self.username_entry.focus()
            return
        
        if not password:
            self._show_error("請輸入密碼")
            self.password_entry.focus()
            return
        
        # Disable UI during login
        self._set_ui_enabled(False)
        self.status_label.config(text="登入中...", foreground="blue")
        
        # Perform login in background thread
        thread = threading.Thread(
            target=self._perform_login,
            args=(username, password, environment)
        )
        thread.daemon = True
        thread.start()
    
    def _perform_login(self, username: str, password: str, environment: str):
        """在背景執行登入"""
        try:
            # Execute login use case
            result = self.login_use_case.execute({
                "username": username,
                "password": password,
                "environment": environment
            })
            
            # Handle result in main thread
            self.dialog.after(0, self._handle_login_result, result)
            
        except Exception as e:
            # Handle error in main thread
            self.dialog.after(0, self._handle_login_error, str(e))
    
    def _handle_login_result(self, result: Dict[str, Any]):
        """處理登入結果"""
        if result["success"]:
            self.result = result
            self._show_success("登入成功")
            self.dialog.after(500, self.dialog.destroy)
        else:
            self._show_error(result.get("error", "登入失敗"))
            self._set_ui_enabled(True)
    
    def _handle_login_error(self, error: str):
        """處理登入錯誤"""
        self._show_error(f"登入錯誤: {error}")
        self._set_ui_enabled(True)
    
    def _on_cancel(self):
        """處理取消動作"""
        self.dialog.destroy()
    
    def _set_ui_enabled(self, enabled: bool):
        """啟用/停用 UI 元件"""
        state = "normal" if enabled else "disabled"
        self.username_entry.config(state=state)
        self.password_entry.config(state=state)
        self.login_button.config(state=state)
        
        # Radio buttons need different handling
        for child in self.dialog.winfo_children():
            if isinstance(child, ttk.Radiobutton):
                child.config(state=state)
    
    def _show_error(self, message: str):
        """顯示錯誤訊息"""
        self.status_label.config(text=message, foreground="red")
    
    def _show_success(self, message: str):
        """顯示成功訊息"""
        self.status_label.config(text=message, foreground="green")
    
    def show(self) -> Optional[Dict[str, Any]]:
        """顯示對話框並等待結果"""
        self.dialog.wait_window()
        return self.result