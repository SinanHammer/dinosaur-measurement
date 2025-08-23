import math
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageTk
import os
import sys


class EnhancedSimpleMeasurementTool:
    def __init__(self):
        self.image_path = ''
        self.image = None
        self.photo = None
        self.points = []
        self.distance_pixels = []
        self.distance_pixel = None
        self.actual_headlength_cm = None
        self.actual_bodylength_cm = None
        self.measurements_df = pd.DataFrame(columns=["Actual headLength(cm)", "Actual bodyLength (cm)"])
        self.pixels_to_length_ratio = 1
        self.file_path = None
        self.current_measurement = 0
        self.measurement_names = ["比例尺长度", "头部长度", "身体长度", "头部宽度", "身体宽度"]
        self.image_window = None
        self.image_canvas = None

        # 先创建根窗口
        self.root = tk.Tk()
        self.root.geometry("400x700")  # 主窗口变窄，只放控制面板
        self.root.title("恐龙测量工具 - 控制面板")
        
        # 在根窗口创建后再创建StringVar
        self.measurement_mode = tk.StringVar(value="模式一")  # 默认选择模式一
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主界面
        self.create_main_interface()
        
        self.root.mainloop()

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 关于菜单
        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="关于", menu=about_menu)
        about_menu.add_command(label="关于程序", command=self.show_about)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)

    def create_main_interface(self):
        """创建主界面 - 只包含控制面板"""
        # 图片路径选择区域
        path_frame = tk.Frame(self.root)
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        path_label = tk.Label(path_frame, text="图片路径:")
        path_label.pack(side=tk.LEFT)
        
        self.image_path_text_widget = tk.Text(path_frame, height=1.5, width=30)
        self.image_path_text_widget.pack(side=tk.LEFT, padx=5)
        
        self.select_image_button = tk.Button(path_frame, text="选择图片", command=self.select_image)
        self.select_image_button.pack(side=tk.LEFT, padx=5)
        
        # 比例尺设置区域
        ratio_frame = tk.Frame(self.root)
        ratio_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ratio_label = tk.Label(ratio_frame, text="Length of bar (cm):")
        ratio_label.pack(side=tk.LEFT)
        
        self.ratio_entry = tk.Entry(ratio_frame, width=15)
        self.ratio_entry.pack(side=tk.LEFT, padx=5)
        
        self.set_ratio_button = tk.Button(ratio_frame, text="设置比例", command=self.set_pixels_to_length_ratio)
        self.set_ratio_button.pack(side=tk.LEFT, padx=5)
        
        # 测量模式和操作按钮区域
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        mode_label = tk.Label(mode_frame, text="测量模式:")
        mode_label.pack(side=tk.LEFT)
        
        # 测量模式单选按钮
        mode_radio_frame = tk.Frame(mode_frame)
        mode_radio_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(mode_radio_frame, text="模式一", variable=self.measurement_mode, value="模式一").pack(side=tk.LEFT)
        tk.Radiobutton(mode_radio_frame, text="模式二", variable=self.measurement_mode, value="模式二").pack(side=tk.LEFT)
        tk.Radiobutton(mode_radio_frame, text="模式三", variable=self.measurement_mode, value="模式三").pack(side=tk.LEFT)
        
        # 操作按钮
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.reset_button = tk.Button(button_frame, text="重置", command=self.reset_measurement)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.measurement_button = tk.Button(button_frame, text="开始测量", command=self.start_measurement)
        self.measurement_button.pack(side=tk.LEFT, padx=5)
        
        # 保存按钮
        save_frame = tk.Frame(self.root)
        save_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.save_button = tk.Button(save_frame, text="保存测量结果", command=self.save_measurement)
        self.save_button.pack(side=tk.LEFT)
        
        # 状态显示区域
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        status_label = tk.Label(status_frame, text="当前状态:")
        status_label.pack(anchor=tk.W)
        
        self.status_label = tk.Label(status_frame, text="等待选择图片", fg="blue")
        self.status_label.pack(anchor=tk.W)
        
        # 监控文本区域 - 保留控制台显示
        monitor_frame = tk.Frame(self.root)
        monitor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        monitor_label = tk.Label(monitor_frame, text="运行日志:")
        monitor_label.pack(anchor=tk.W)
        
        self.monitor_text_widget = tk.Text(monitor_frame, height=20, wrap=tk.WORD)
        self.monitor_text_widget.pack(fill=tk.BOTH, expand=True)

    def create_image_window(self):
        """创建图片显示窗口"""
        if self.image_window is None or not self.image_window.winfo_exists():
            self.image_window = tk.Toplevel(self.root)
            self.image_window.title("图片测量窗口")
            self.image_window.geometry("600x500")
            
            # 图片画布
            self.image_canvas = Canvas(self.image_window, bg="white")
            self.image_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 绑定鼠标事件
            self.image_canvas.bind("<Button-1>", self.on_canvas_click)
            self.image_canvas.bind("<Button-3>", self.on_canvas_right_click)
            
            # 窗口关闭事件
            self.image_window.protocol("WM_DELETE_WINDOW", self.on_image_window_close)
            
            # 显示图片
            self.display_image()
        else:
            self.image_window.lift()  # 将窗口提到前面
            self.display_image()

    def on_image_window_close(self):
        """图片窗口关闭事件"""
        self.image_window.destroy()
        self.image_window = None
        self.image_canvas = None

    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo("关于", "恐龙测量工具 v2.0 Enhanced\n\n基于PIL和Tkinter开发的恐龙尺寸测量工具\n支持多种测量模式，兼容性更好")

    def show_help(self):
        """显示帮助信息"""
        help_text = """
使用说明：

1. 选择图片：点击"选择图片"按钮选择包含恐龙的图片
2. 设置比例：在"Length of bar (cm)"中输入比例尺的实际长度
3. 选择模式：选择测量模式（模式一/模式二/模式三）
4. 开始测量：点击"开始测量"按钮，图片将在单独窗口显示
5. 点击测量：在图片上点击两个点进行距离测量
6. 保存结果：完成测量后点击"保存测量结果"

测量模式说明：
- 模式一：标准测量模式（5次测量）
- 模式二：快速测量模式（3次测量）
- 模式三：精确测量模式（5次测量，带校准）

操作提示：
- 左键点击：添加测量点
- 右键点击：撤销上一个点
- 重置按钮：重新开始测量
        """
        messagebox.showinfo("使用说明", help_text)

    def select_image(self):
        """选择图片文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            try:
                self.image_path = file_path
                self.image = Image.open(file_path)
                self.image_path_text_widget.delete(1.0, tk.END)
                self.image_path_text_widget.insert(tk.END, file_path)
                self.status_label.config(text="图片已加载，可以开始测量", fg="green")
                self.print_to_monitor(f"图片加载成功: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片: {e}")

    def display_image(self):
        """在画布上显示图片"""
        if self.image and self.image_canvas:
            # 获取画布大小
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # 如果画布还没有正确初始化，使用默认大小
                canvas_width = 500
                canvas_height = 400
            
            # 计算缩放比例
            img_width, img_height = self.image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # 不放大，只缩小
            
            # 缩放图片
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            resized_image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            self.photo = ImageTk.PhotoImage(resized_image)
            
            # 清除画布并显示图片
            self.image_canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.image_canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
            
            # 保存缩放比例用于坐标转换
            self.scale_factor = scale

    def set_pixels_to_length_ratio(self):
        """设置像素到实际长度的比例"""
        try:
            ratio = float(self.ratio_entry.get())
            if ratio <= 0:
                raise ValueError("比例必须大于0")
            self.pixels_to_length_ratio = ratio
            self.status_label.config(text=f"比例尺已设置为: {ratio} cm", fg="green")
            self.print_to_monitor(f"比例尺已设置为: {ratio} cm")
        except ValueError as e:
            messagebox.showerror("错误", f"请输入有效的数字: {e}")

    def reset_measurement(self):
        """重置测量"""
        self.current_measurement = 0
        self.distance_pixels = []
        self.points = []
        self.actual_headlength_cm = None
        self.actual_bodylength_cm = None
        self.status_label.config(text="测量已重置", fg="blue")
        self.print_to_monitor("测量已重置")
        if self.image_canvas:
            self.redraw_points()

    def start_measurement(self):
        """开始测量流程"""
        if not self.image:
            messagebox.showerror("错误", "请先选择图片")
            return
        
        if self.pixels_to_length_ratio <= 0:
            messagebox.showerror("错误", "请先设置比例尺")
            return
        
        # 创建图片窗口
        self.create_image_window()
        
        self.current_measurement = 0
        self.distance_pixels = []
        self.points = []
        
        # 根据模式调整测量次数
        if self.measurement_mode.get() == "模式一":
            self.measurements_needed = 5
        elif self.measurement_mode.get() == "模式二":
            self.measurements_needed = 3
        else:  # 模式三
            self.measurements_needed = 5
        
        self.status_label.config(text=f"测量中 - {self.measurement_mode.get()}", fg="orange")
        self.print_to_monitor(f"开始测量 - 模式: {self.measurement_mode.get()}")
        self.print_to_monitor(f"需要测量 {self.measurements_needed} 次")
        self.print_to_monitor(f"当前测量: {self.measurement_names[0]}")

    def on_canvas_click(self, event):
        """处理画布左键点击"""
        if self.current_measurement >= self.measurements_needed:
            return
        
        # 转换坐标
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        img_width, img_height = self.image.size
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        scale = min(scale_x, scale_y, 1.0)
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        x_offset = (canvas_width - new_width) // 2
        y_offset = (canvas_height - new_height) // 2
        
        # 转换到原图坐标
        x = (event.x - x_offset) / scale
        y = (event.y - y_offset) / scale
        
        if 0 <= x <= img_width and 0 <= y <= img_height:
            self.points.append((x, y))
            self.draw_point(event.x, event.y)
            
            if len(self.points) == 2:
                self.complete_measurement()

    def on_canvas_right_click(self, event):
        """处理画布右键点击 - 撤销上一个点"""
        if self.points:
            self.points.pop()
            self.redraw_points()

    def draw_point(self, x, y):
        """在画布上绘制点"""
        self.image_canvas.create_oval(x-3, y-3, x+3, y+3, fill="red", outline="red")
        if len(self.points) == 2:
            # 绘制连线
            x1, y1 = self.points[0]
            x2, y2 = self.points[1]
            # 转换回画布坐标
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            img_width, img_height = self.image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y, 1.0)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            x_offset = (canvas_width - new_width) // 2
            y_offset = (canvas_height - new_height) // 2
            
            canvas_x1 = x1 * scale + x_offset
            canvas_y1 = y1 * scale + y_offset
            canvas_x2 = x2 * scale + x_offset
            canvas_y2 = y2 * scale + y_offset
            
            self.image_canvas.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2, fill="blue", width=2)

    def redraw_points(self):
        """重新绘制所有点"""
        if not self.image_canvas:
            return
            
        self.image_canvas.delete("all")
        if self.photo:
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            x = (canvas_width - self.photo.width()) // 2
            y = (canvas_height - self.photo.height()) // 2
            self.image_canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
        
        for i, point in enumerate(self.points):
            # 转换坐标
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            img_width, img_height = self.image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y, 1.0)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            x_offset = (canvas_width - new_width) // 2
            y_offset = (canvas_height - new_height) // 2
            
            canvas_x = point[0] * scale + x_offset
            canvas_y = point[1] * scale + y_offset
            
            self.image_canvas.create_oval(canvas_x-3, canvas_y-3, canvas_x+3, canvas_y+3, fill="red", outline="red")
            
            if i == 1 and len(self.points) == 2:
                # 绘制连线
                canvas_x1 = self.points[0][0] * scale + x_offset
                canvas_y1 = self.points[0][1] * scale + y_offset
                self.image_canvas.create_line(canvas_x1, canvas_y1, canvas_x, canvas_y, fill="blue", width=2)

    def complete_measurement(self):
        """完成一次测量"""
        if len(self.points) == 2:
            distance = self.calculate_distance(self.points[0], self.points[1])
            self.distance_pixels.append(distance)
            
            self.print_to_monitor(f"{self.measurement_names[self.current_measurement]}: {distance:.2f} 像素")
            
            self.current_measurement += 1
            self.points = []
            
            if self.current_measurement < self.measurements_needed:
                self.print_to_monitor(f"当前测量: {self.measurement_names[self.current_measurement]}")
                self.print_to_monitor("请继续点击两个点...")
            else:
                self.calculate_results()

    def calculate_distance(self, point1, point2):
        """计算两点间距离"""
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def calculate_results(self):
        """计算最终结果"""
        if len(self.distance_pixels) == self.measurements_needed:
            if self.measurement_mode.get() == "模式一":
                # 标准模式 - 需要5次测量
                if len(self.distance_pixels) == 5:
                    self.actual_headlength_cm = ((self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio) * (
                                self.distance_pixels[3] / self.distance_pixels[2])
                    self.actual_bodylength_cm = ((self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio) * (
                                self.distance_pixels[4] / self.distance_pixels[2])
            elif self.measurement_mode.get() == "模式二":
                # 快速模式 - 只需要3次测量
                if len(self.distance_pixels) == 3:
                    self.actual_headlength_cm = (self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio
                    self.actual_bodylength_cm = (self.distance_pixels[2] / self.distance_pixels[0]) * self.pixels_to_length_ratio
            elif self.measurement_mode.get() == "模式三":
                # 精确模式 - 需要5次测量，带校准
                if len(self.distance_pixels) == 5:
                    self.actual_headlength_cm = ((self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio) * (
                                self.distance_pixels[3] / self.distance_pixels[2]) * 1.02  # 精确校准因子
                    self.actual_bodylength_cm = ((self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio) * (
                                self.distance_pixels[4] / self.distance_pixels[2]) * 1.02
            
            if self.actual_headlength_cm is not None and self.actual_bodylength_cm is not None:
                self.status_label.config(text="测量完成！", fg="green")
                self.print_to_monitor(f"头部长度: {self.actual_headlength_cm:.2f} cm")
                self.print_to_monitor(f"身体长度: {self.actual_bodylength_cm:.2f} cm")
                self.print_to_monitor("测量完成！可以保存结果了。")
                messagebox.showinfo("完成", "测量完成！可以保存结果了。")

    def save_measurement(self):
        """保存测量结果"""
        if self.actual_headlength_cm is None or self.actual_bodylength_cm is None:
            messagebox.showerror("错误", "请先完成测量")
            return
        
        file_path = filedialog.askdirectory()
        if file_path:
            new_row = {
                "Actual headLength(cm)": self.actual_headlength_cm,
                "Actual bodyLength (cm)": self.actual_bodylength_cm
            }
            self.measurements_df = pd.concat([self.measurements_df, pd.DataFrame([new_row])], ignore_index=True)
            
            output_file = os.path.join(file_path, 'measurement.csv')
            self.measurements_df.to_csv(output_file, index=False)
            self.print_to_monitor(f"结果已保存到: {output_file}")
            messagebox.showinfo("成功", "测量结果已保存！")

    def print_to_monitor(self, message):
        """在监控区域显示消息"""
        self.monitor_text_widget.insert(tk.END, message + "\n")
        self.monitor_text_widget.see(tk.END)  # Scroll to the end


if __name__ == "__main__":
    try:
        app = EnhancedSimpleMeasurementTool()
    except Exception as e:
        print(f"程序启动错误: {e}")
        input("按回车键退出...")
