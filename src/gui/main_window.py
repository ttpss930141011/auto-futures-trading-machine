import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from src.domain.entities.component_status import ComponentStatus
from src.domain.entities.user import User
from src.domain.entities.session import Session
from src.domain.entities.condition import Condition
from src.infrastructure.services.service_container import ServiceContainer
from src.infrastructure.services.system_manager import SystemManager
from src.interactor.use_cases.user_login_use_case import UserLoginUseCase
from src.interactor.use_cases.register_item_use_case import RegisterItemUseCase
from src.interactor.use_cases.select_order_account_use_case import SelectOrderAccountUseCase
from src.interactor.use_cases.create_condition_use_case import CreateConditionUseCase
from src.interactor.use_cases.application_startup_status_use_case import ApplicationStartupStatusUseCase


class MainWindow:
    def __init__(self, service_container: ServiceContainer, system_manager: SystemManager):
        self.service_container = service_container
        self.system_manager = system_manager
        self.logger = service_container.logger
        
        # Use cases
        self.login_use_case = UserLoginUseCase(
            service_container.exchange_api,
            service_container.session_repository,
            service_container.logger
        )
        self.register_item_use_case = RegisterItemUseCase(
            service_container.exchange_api,
            service_container.session_repository,
            service_container.logger
        )
        self.select_order_account_use_case = SelectOrderAccountUseCase(
            service_container.exchange_api,
            service_container.session_repository,
            service_container.logger
        )
        self.create_condition_use_case = CreateConditionUseCase(
            service_container.condition_repository,
            service_container.session_repository,
            service_container.logger
        )
        self.startup_status_use_case = ApplicationStartupStatusUseCase(
            service_container.session_repository,
            service_container.condition_repository,
            service_container.logger
        )
        
        # Window setup
        self.root = tk.Tk()
        self.root.title("Auto Futures Trading Machine")
        self.root.geometry("1200x800")
        
        # State variables
        self.current_user: Optional[User] = None
        self.current_session: Optional[Session] = None
        self.registered_items: List[str] = []
        self.selected_order_account: Optional[str] = None
        self.conditions: List[Condition] = []
        
        # Create GUI components
        self._create_menu_bar()
        self._create_top_frame()
        self._create_main_content()
        self._create_status_bar()
        
        # Auto-login on startup
        self.root.after(100, self._auto_login)
        
        # Start status update timer
        self._update_status()
    
    def _create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="檔案", menu=file_menu)
        file_menu.add_command(label="登入", command=self._show_login_dialog)
        file_menu.add_command(label="登出", command=self._logout)
        file_menu.add_separator()
        file_menu.add_command(label="結束", command=self._on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="檢視", menu=view_menu)
        view_menu.add_command(label="重新整理", command=self._refresh_ui)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="說明", menu=help_menu)
        help_menu.add_command(label="關於", command=self._show_about)
    
    def _create_top_frame(self):
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Left side - Login status
        self.login_status_label = ttk.Label(self.top_frame, text="未登入", font=("Arial", 10))
        self.login_status_label.pack(side=tk.LEFT, padx=5)
        
        # Right side - Register Item Index
        self.register_item_label = ttk.Label(
            self.top_frame, 
            text="Register Item: None", 
            font=("Arial", 10, "bold")
        )
        self.register_item_label.pack(side=tk.RIGHT, padx=5)
        
        # System status indicators
        self.status_frame = ttk.Frame(self.top_frame)
        self.status_frame.pack(side=tk.RIGHT, padx=20)
        
        self._create_status_indicator("Gateway", 0)
        self._create_status_indicator("Strategy", 1)
        self._create_status_indicator("Order Executor", 2)
    
    def _create_status_indicator(self, name: str, column: int):
        frame = ttk.Frame(self.status_frame)
        frame.grid(row=0, column=column, padx=5)
        
        label = ttk.Label(frame, text=name, font=("Arial", 8))
        label.pack()
        
        canvas = tk.Canvas(frame, width=20, height=20)
        canvas.pack()
        
        # Create status circle
        indicator = canvas.create_oval(2, 2, 18, 18, fill="gray", outline="black")
        
        # Store reference
        setattr(self, f"{name.lower().replace(' ', '_')}_indicator", (canvas, indicator))
    
    def _create_main_content(self):
        # Main notebook for different sections
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Trading setup tab
        self.trading_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trading_frame, text="交易設定")
        self._create_trading_tab()
        
        # System monitor tab
        self.monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitor_frame, text="系統監控")
        self._create_monitor_tab()
        
        # Log viewer tab
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="日誌")
        self._create_log_tab()
    
    def _create_trading_tab(self):
        # Left panel - Account and product selection
        left_panel = ttk.LabelFrame(self.trading_frame, text="帳戶與商品", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Register items
        ttk.Label(left_panel, text="商品選擇:").pack(anchor=tk.W)
        self.register_items_frame = ttk.Frame(left_panel)
        self.register_items_frame.pack(fill=tk.X, pady=5)
        
        # Default items
        self.item_vars = {}
        for item in ["TXF", "MXF"]:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.register_items_frame, text=item, variable=var)
            cb.pack(anchor=tk.W)
            self.item_vars[item] = var
        
        ttk.Button(left_panel, text="註冊商品", command=self._register_items).pack(fill=tk.X, pady=5)
        
        # Order account
        ttk.Label(left_panel, text="下單帳戶:").pack(anchor=tk.W, pady=(10, 0))
        self.account_combo = ttk.Combobox(left_panel, state="readonly")
        self.account_combo.pack(fill=tk.X, pady=5)
        self.account_combo.bind("<<ComboboxSelected>>", self._on_account_selected)
        
        # Right panel - Trading conditions
        right_panel = ttk.LabelFrame(self.trading_frame, text="交易條件", padding=10)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Condition form
        form_frame = ttk.Frame(right_panel)
        form_frame.pack(fill=tk.X)
        
        # Action (Buy/Sell)
        ttk.Label(form_frame, text="動作:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.action_var = tk.StringVar(value="Buy")
        action_frame = ttk.Frame(form_frame)
        action_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(action_frame, text="買", variable=self.action_var, value="Buy").pack(side=tk.LEFT)
        ttk.Radiobutton(action_frame, text="賣", variable=self.action_var, value="Sell").pack(side=tk.LEFT)
        
        # Target price
        ttk.Label(form_frame, text="目標價格:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.target_price_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.target_price_var).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Turning point
        ttk.Label(form_frame, text="轉折點:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.turning_point_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.turning_point_var).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Quantity
        ttk.Label(form_frame, text="數量:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.quantity_var = tk.IntVar(value=1)
        ttk.Spinbox(form_frame, textvariable=self.quantity_var, from_=1, to=100).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Take profit
        ttk.Label(form_frame, text="停利點 (選填):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.take_profit_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.take_profit_var).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Stop loss
        ttk.Label(form_frame, text="停損點 (選填):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.stop_loss_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.stop_loss_var).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Follow condition
        ttk.Label(form_frame, text="跟隨條件:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.follow_var = tk.BooleanVar()
        ttk.Checkbutton(form_frame, variable=self.follow_var).grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(right_panel)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="新增條件", command=self._add_condition).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清除條件", command=self._clear_conditions).pack(side=tk.LEFT, padx=5)
        
        # Conditions list
        ttk.Label(right_panel, text="現有條件:").pack(anchor=tk.W, pady=(10, 0))
        
        self.conditions_tree = ttk.Treeview(
            right_panel, 
            columns=("action", "price", "turning", "quantity", "status"),
            height=5
        )
        self.conditions_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.conditions_tree.heading("#0", text="ID")
        self.conditions_tree.heading("action", text="動作")
        self.conditions_tree.heading("price", text="目標價格")
        self.conditions_tree.heading("turning", text="轉折點")
        self.conditions_tree.heading("quantity", text="數量")
        self.conditions_tree.heading("status", text="狀態")
        
        self.conditions_tree.column("#0", width=50)
        self.conditions_tree.column("action", width=60)
        self.conditions_tree.column("price", width=80)
        self.conditions_tree.column("turning", width=80)
        self.conditions_tree.column("quantity", width=60)
        self.conditions_tree.column("status", width=80)
        
        # Start trading button
        self.start_button = ttk.Button(
            right_panel, 
            text="啟動交易系統", 
            command=self._start_trading,
            style="Accent.TButton"
        )
        self.start_button.pack(pady=10)
    
    def _create_monitor_tab(self):
        # System health
        health_frame = ttk.LabelFrame(self.monitor_frame, text="系統健康狀態", padding=10)
        health_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.health_text = tk.Text(health_frame, height=10, width=50)
        self.health_text.pack(fill=tk.BOTH, expand=True)
        
        # Market data
        market_frame = ttk.LabelFrame(self.monitor_frame, text="市場數據", padding=10)
        market_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.market_tree = ttk.Treeview(
            market_frame,
            columns=("time", "symbol", "price", "volume"),
            height=10
        )
        self.market_tree.pack(fill=tk.BOTH, expand=True)
        
        self.market_tree.heading("time", text="時間")
        self.market_tree.heading("symbol", text="商品")
        self.market_tree.heading("price", text="價格")
        self.market_tree.heading("volume", text="成交量")
    
    def _create_log_tab(self):
        # Log text widget
        self.log_text = tk.Text(self.log_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log scrollbar
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Log control buttons
        control_frame = ttk.Frame(self.log_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="清除日誌", command=self._clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="儲存日誌", command=self._save_log).pack(side=tk.LEFT, padx=5)
    
    def _create_status_bar(self):
        self.status_bar = ttk.Label(
            self.root, 
            text="就緒", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _auto_login(self):
        """嘗試使用上次的登入資訊自動登入"""
        try:
            # Check if there's a valid session
            sessions = self.service_container.session_repository.get_all()
            if sessions:
                # Get the most recent session
                latest_session = max(sessions, key=lambda s: s.created_at)
                if not latest_session.is_expired():
                    self.current_session = latest_session
                    self.current_user = latest_session.user
                    self._update_login_status()
                    self._load_user_preferences()
                    self._log_message(f"自動登入成功: {self.current_user.username}")
                    return
            
            self._log_message("無有效的登入資訊，請手動登入")
        except Exception as e:
            self._log_message(f"自動登入失敗: {str(e)}")
    
    def _load_user_preferences(self):
        """載入使用者偏好設定"""
        try:
            # Load registered items from last session
            if hasattr(self.current_session, "registered_items"):
                self.registered_items = self.current_session.registered_items
                self._update_register_items_display()
            
            # Load order accounts and select first one
            self._refresh_order_accounts()
            
            # Load saved conditions
            self._refresh_conditions()
            
        except Exception as e:
            self._log_message(f"載入偏好設定失敗: {str(e)}")
    
    def _show_login_dialog(self):
        """顯示登入對話框"""
        from src.gui.widgets.login_dialog import LoginDialog
        dialog = LoginDialog(self.root, self.login_use_case)
        result = dialog.show()
        
        if result:
            self.current_user = result["user"]
            self.current_session = result["session"]
            self._update_login_status()
            self._load_user_preferences()
            self._log_message(f"登入成功: {self.current_user.username}")
    
    def _logout(self):
        """登出"""
        if not self.current_session:
            messagebox.showinfo("提示", "您尚未登入")
            return
        
        try:
            # Stop system if running
            if self._is_system_running():
                self._stop_trading()
            
            # Clear session
            self.current_user = None
            self.current_session = None
            self.registered_items = []
            self.selected_order_account = None
            
            self._update_login_status()
            self._clear_ui()
            self._log_message("已登出")
            
        except Exception as e:
            self._log_message(f"登出失敗: {str(e)}")
    
    def _register_items(self):
        """註冊選擇的商品"""
        if not self.current_session:
            messagebox.showwarning("警告", "請先登入")
            return
        
        try:
            # Get selected items
            selected = [item for item, var in self.item_vars.items() if var.get()]
            
            if not selected:
                messagebox.showwarning("警告", "請至少選擇一個商品")
                return
            
            # Register each item
            for item in selected:
                result = self.register_item_use_case.execute({
                    "session_id": self.current_session.id,
                    "item_code": item
                })
                
                if result["success"]:
                    self.registered_items.append(item)
                    self._log_message(f"成功註冊商品: {item}")
                else:
                    self._log_message(f"註冊商品失敗: {item} - {result.get('error', 'Unknown error')}")
            
            self._update_register_items_display()
            
        except Exception as e:
            messagebox.showerror("錯誤", f"註冊商品失敗: {str(e)}")
    
    def _on_account_selected(self, event):
        """處理帳戶選擇"""
        if not self.current_session:
            return
        
        try:
            selected_index = self.account_combo.current()
            if selected_index >= 0:
                result = self.select_order_account_use_case.execute({
                    "session_id": self.current_session.id,
                    "account_index": selected_index
                })
                
                if result["success"]:
                    self.selected_order_account = self.account_combo.get()
                    self._log_message(f"已選擇下單帳戶: {self.selected_order_account}")
                    
        except Exception as e:
            self._log_message(f"選擇帳戶失敗: {str(e)}")
    
    def _add_condition(self):
        """新增交易條件"""
        if not self.current_session:
            messagebox.showwarning("警告", "請先登入")
            return
        
        try:
            # Validate inputs
            if not self.target_price_var.get() or not self.turning_point_var.get():
                messagebox.showwarning("警告", "請填寫必要欄位")
                return
            
            # Create condition
            condition_data = {
                "session_id": self.current_session.id,
                "action": self.action_var.get(),
                "target_price": self.target_price_var.get(),
                "turning_point": self.turning_point_var.get(),
                "quantity": self.quantity_var.get(),
                "is_following_condition": self.follow_var.get()
            }
            
            # Add optional fields
            if self.take_profit_var.get():
                condition_data["take_profit"] = self.take_profit_var.get()
            if self.stop_loss_var.get():
                condition_data["stop_loss"] = self.stop_loss_var.get()
            
            result = self.create_condition_use_case.execute(condition_data)
            
            if result["success"]:
                self._log_message("成功新增交易條件")
                self._refresh_conditions()
                self._clear_condition_form()
            else:
                messagebox.showerror("錯誤", f"新增條件失敗: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            messagebox.showerror("錯誤", f"新增條件失敗: {str(e)}")
    
    def _clear_conditions(self):
        """清除所有條件"""
        if not self.current_session:
            return
        
        if messagebox.askyesno("確認", "確定要清除所有交易條件嗎？"):
            try:
                # Clear from repository
                self.service_container.condition_repository.delete_all()
                self._refresh_conditions()
                self._log_message("已清除所有交易條件")
            except Exception as e:
                self._log_message(f"清除條件失敗: {str(e)}")
    
    def _start_trading(self):
        """啟動交易系統"""
        if not self.current_session:
            messagebox.showwarning("警告", "請先登入")
            return
        
        try:
            # Check startup status
            status = self.startup_status_use_case.execute({
                "session_id": self.current_session.id
            })
            
            if not status["can_start"]:
                missing = "\n".join(f"- {item}" for item in status["missing_requirements"])
                messagebox.showwarning("無法啟動", f"請先完成以下設定:\n{missing}")
                return
            
            # Start system
            self.system_manager.start()
            self._log_message("交易系統已啟動")
            
            # Update UI
            self.start_button.config(text="停止交易系統", command=self._stop_trading)
            
        except Exception as e:
            messagebox.showerror("錯誤", f"啟動失敗: {str(e)}")
    
    def _stop_trading(self):
        """停止交易系統"""
        try:
            self.system_manager.stop()
            self._log_message("交易系統已停止")
            
            # Update UI
            self.start_button.config(text="啟動交易系統", command=self._start_trading)
            
        except Exception as e:
            messagebox.showerror("錯誤", f"停止失敗: {str(e)}")
    
    def _is_system_running(self) -> bool:
        """檢查系統是否正在運行"""
        health = self.system_manager.health_check()
        return health.get("overall_status") == ComponentStatus.RUNNING
    
    def _update_status(self):
        """更新系統狀態顯示"""
        try:
            if self.system_manager:
                health = self.system_manager.health_check()
                
                # Update component indicators
                self._update_component_status("gateway", health["components"]["gateway"]["status"])
                self._update_component_status("strategy", health["components"]["strategy"]["status"])
                self._update_component_status("order_executor", health["components"]["order_executor"]["status"])
                
                # Update health text
                if hasattr(self, "health_text"):
                    self.health_text.delete(1.0, tk.END)
                    self.health_text.insert(tk.END, f"整體狀態: {health['overall_status']}\n")
                    self.health_text.insert(tk.END, f"運行時間: {health.get('uptime', 'N/A')}\n\n")
                    
                    for comp_name, comp_data in health["components"].items():
                        self.health_text.insert(tk.END, f"{comp_name}:\n")
                        self.health_text.insert(tk.END, f"  狀態: {comp_data['status']}\n")
                        self.health_text.insert(tk.END, f"  運行時間: {comp_data.get('uptime', 'N/A')}\n")
                        if comp_data.get("message"):
                            self.health_text.insert(tk.END, f"  訊息: {comp_data['message']}\n")
                        self.health_text.insert(tk.END, "\n")
        
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
        
        # Schedule next update
        self.root.after(1000, self._update_status)
    
    def _update_component_status(self, component: str, status: str):
        """更新組件狀態指示器顏色"""
        if hasattr(self, f"{component}_indicator"):
            canvas, indicator = getattr(self, f"{component}_indicator")
            
            color_map = {
                ComponentStatus.STOPPED: "gray",
                ComponentStatus.STARTING: "yellow",
                ComponentStatus.RUNNING: "green",
                ComponentStatus.STOPPING: "orange",
                ComponentStatus.ERROR: "red"
            }
            
            color = color_map.get(status, "gray")
            canvas.itemconfig(indicator, fill=color)
    
    def _update_login_status(self):
        """更新登入狀態顯示"""
        if self.current_user:
            self.login_status_label.config(text=f"已登入: {self.current_user.username}")
        else:
            self.login_status_label.config(text="未登入")
    
    def _update_register_items_display(self):
        """更新註冊商品顯示"""
        if self.registered_items:
            items_str = ", ".join(self.registered_items)
            self.register_item_label.config(text=f"Register Items: {items_str}")
        else:
            self.register_item_label.config(text="Register Item: None")
    
    def _refresh_order_accounts(self):
        """重新載入下單帳戶列表"""
        if not self.current_session:
            return
        
        try:
            # Get accounts from exchange client
            accounts = self.service_container.exchange_client.UserOrderSet
            if accounts:
                account_names = [f"{acc.BrokerID}-{acc.Account}" for acc in accounts]
                self.account_combo["values"] = account_names
                
                # Select first account by default
                if account_names:
                    self.account_combo.current(0)
                    self._on_account_selected(None)
                    
        except Exception as e:
            self._log_message(f"載入帳戶失敗: {str(e)}")
    
    def _refresh_conditions(self):
        """重新載入交易條件列表"""
        try:
            # Clear existing items
            for item in self.conditions_tree.get_children():
                self.conditions_tree.delete(item)
            
            # Load conditions
            conditions = self.service_container.condition_repository.get_all()
            self.conditions = conditions
            
            # Add to tree
            for i, condition in enumerate(conditions):
                self.conditions_tree.insert(
                    "", 
                    tk.END, 
                    text=str(i+1),
                    values=(
                        condition.action,
                        condition.target_price,
                        condition.turning_point,
                        condition.quantity,
                        "啟用" if condition.is_active else "停用"
                    )
                )
                
        except Exception as e:
            self._log_message(f"載入條件失敗: {str(e)}")
    
    def _clear_condition_form(self):
        """清空條件表單"""
        self.target_price_var.set(0)
        self.turning_point_var.set(0)
        self.quantity_var.set(1)
        self.take_profit_var.set(0)
        self.stop_loss_var.set(0)
        self.follow_var.set(False)
    
    def _clear_ui(self):
        """清空 UI 顯示"""
        self.register_item_label.config(text="Register Item: None")
        self.account_combo.set("")
        self.account_combo["values"] = []
        self._clear_condition_form()
        self._refresh_conditions()
    
    def _log_message(self, message: str):
        """寫入日誌訊息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        if hasattr(self, "log_text"):
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
        
        # Also update status bar
        self.status_bar.config(text=message)
        
        # Log to file
        self.logger.info(message)
    
    def _clear_log(self):
        """清除日誌"""
        self.log_text.delete(1.0, tk.END)
    
    def _save_log(self):
        """儲存日誌到檔案"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("成功", "日誌已儲存")
            except Exception as e:
                messagebox.showerror("錯誤", f"儲存失敗: {str(e)}")
    
    def _refresh_ui(self):
        """重新整理 UI"""
        if self.current_session:
            self._refresh_order_accounts()
            self._refresh_conditions()
            self._log_message("UI 已重新整理")
    
    def _show_about(self):
        """顯示關於對話框"""
        messagebox.showinfo(
            "關於",
            "Auto Futures Trading Machine\n\n"
            "版本: 1.0.0\n"
            "基於 PFCF API 的自動期貨交易系統"
        )
    
    def _on_closing(self):
        """處理視窗關閉事件"""
        if self._is_system_running():
            if messagebox.askyesno("確認", "交易系統正在運行，確定要結束嗎？"):
                self._stop_trading()
            else:
                return
        
        self.root.quit()
    
    def run(self):
        """運行 GUI 主迴圈"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()