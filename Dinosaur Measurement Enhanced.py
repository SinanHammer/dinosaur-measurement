import cv2
import math
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import os
import sys


class EnhancedMeasurementTool:
    def __init__(self):
        self.image_path = ''
        self.image = None
        self.points = []
        self.distance_pixels = []
        self.distance_pixel = None
        self.actual_headlength_cm = None
        self.actual_bodylength_cm = None
        self.measurements_df = pd.DataFrame(columns=["Actual headLength(cm)", "Actual bodyLength (cm)"])
        self.pixels_to_length_ratio = 1
        self.file_path = None

        # 设置matplotlib后端
        plt.switch_backend('TkAgg')
        
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
        
        self.measurement_button = tk.Button(button_frame, text="开始测量", command=self.run)
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

    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo("关于", "恐龙测量工具 v2.0\n\n基于OpenCV和Tkinter开发的恐龙尺寸测量工具\n支持多种测量模式")

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
- 模式一：标准测量模式
- 模式二：快速测量模式
- 模式三：精确测量模式

操作提示：
- 左键点击：添加测量点
- 右键点击：撤销上一个点
- 重置按钮：重新开始测量
        """
        messagebox.showinfo("使用说明", help_text)

    def select_image(self):
        """选择图片文件"""
        if self.image_path:
            return
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
        if self.image_path:
            self.image_path_text_widget.delete(1.0, tk.END)
            self.image_path_text_widget.insert(tk.END, self.image_path)
            self.image = cv2.imread(self.image_path)
            if self.image is None:
                messagebox.showerror("错误", "无法加载图片文件")
                self.image_path = ''
            else:
                self.status_label.config(text="图片已加载，可以开始测量", fg="green")
                self.print_to_monitor(f"图片加载成功: {os.path.basename(self.image_path)}")

    def set_pixels_to_length_ratio(self):
        """设置像素到实际长度的比例"""
        ratio_text = self.ratio_entry.get()
        try:
            self.pixels_to_length_ratio = float(ratio_text)
            self.status_label.config(text=f"比例尺已设置为: {self.pixels_to_length_ratio} cm", fg="green")
            self.print_to_monitor("Length of bar已设置为: {}".format(self.pixels_to_length_ratio))
        except ValueError:
            self.print_to_monitor("无效的比例值")
            messagebox.showerror("错误", "请输入有效的数字")

    def reset_measurement(self):
        """重置测量"""
        self.points = []
        self.distance_pixels = []
        self.actual_headlength_cm = None
        self.actual_bodylength_cm = None
        self.status_label.config(text="测量已重置", fg="blue")
        self.print_to_monitor("测量已重置")

    def mouse_callback(self, event, x, y, flags, param):
        """鼠标回调函数"""
        if event == cv2.EVENT_LBUTTONDOWN:
            cv2.circle(self.image, (x, y), 5, (0, 255, 0), -1)
            self.points.append((x, y))
            cv2.imshow('image', self.image)
        elif event == cv2.EVENT_RBUTTONDOWN:
            if self.points:
                self.points.pop()
                self.image = cv2.imread(self.image_path)
                for point in self.points:
                    cv2.circle(self.image, point, 5, (0, 255, 0), -1)
                cv2.imshow('image', self.image)

    def perform_measurement(self):
        """执行测量"""
        if self.image is None:
            messagebox.showerror("错误", "请先选择图片")
            return
            
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('image', self.mouse_callback)

        while True:
            cv2.imshow('image', self.image)
            key = cv2.waitKey(1) & 0xFF
            if key != 255:
                if len(self.points) == 2:
                    break
                else:
                    self.print_to_monitor("选择的点的数量存在问题")
                    pass
            else:
                pass

        cv2.destroyAllWindows()

        self.distance_pixel = self.calculate_distance(self.points[0], self.points[1])
        self.distance_pixels.append(self.distance_pixel)
        self.print_to_monitor("Distance in pixels: {}".format(self.distance_pixel))
        self.points = []
        
        # 根据测量模式调整计算逻辑
        if len(self.distance_pixels) == 5:
            if self.measurement_mode.get() == "模式一":
                # 标准模式
                self.actual_headlength_cm = ((self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio) * (
                            self.distance_pixels[3] / self.distance_pixels[2])
                self.actual_bodylength_cm = ((self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio) * (
                            self.distance_pixels[4] / self.distance_pixels[2])
            elif self.measurement_mode.get() == "模式二":
                # 快速模式 - 简化计算
                self.actual_headlength_cm = (self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio
                self.actual_bodylength_cm = (self.distance_pixels[2] / self.distance_pixels[0]) * self.pixels_to_length_ratio
            elif self.measurement_mode.get() == "模式三":
                # 精确模式 - 使用更多校准
                self.actual_headlength_cm = ((self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio) * (
                            self.distance_pixels[3] / self.distance_pixels[2]) * 1.02  # 精确校准因子
                self.actual_bodylength_cm = ((self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio) * (
                            self.distance_pixels[4] / self.distance_pixels[2]) * 1.02
            
            self.print_to_monitor("Actual headLength: {} cm".format(self.actual_headlength_cm))
            self.print_to_monitor("Actual bodyLength: {} cm".format(self.actual_bodylength_cm))

    def calculate_distance(self, point1, point2):
        """计算两点间距离"""
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def save_measurement(self):
        """保存测量结果"""
        if self.actual_headlength_cm is None or self.actual_bodylength_cm is None:
            messagebox.showerror("错误", "请先完成测量")
            return
            
        self.file_path = filedialog.askdirectory()
        if self.file_path:
            new_row = {"Actual headLength(cm)": self.actual_headlength_cm, "Actual bodyLength (cm)": self.actual_bodylength_cm}
            # 使用concat替代已弃用的append方法
            self.measurements_df = pd.concat([self.measurements_df, pd.DataFrame([new_row])], ignore_index=True)
            
            output_file = os.path.join(self.file_path, 'measurement.csv')
            self.measurements_df.to_csv(output_file, index=False)
            self.print_to_monitor("测量结果已保存到: {}".format(output_file))
            messagebox.showinfo("成功", "测量结果已保存！")

    def show_image(self):
        """显示图片"""
        if self.image is not None:
            plt.figure(figsize=(8, 6))
            plt.imshow(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
            plt.axis('off')
            plt.title("当前图片")
            plt.show()

    def run(self):
        """运行测量流程"""
        if self.image is None:
            messagebox.showerror("错误", "请先选择图片")
            return
            
        self.status_label.config(text=f"测量中 - {self.measurement_mode.get()}", fg="orange")
        self.print_to_monitor(f"开始测量 - 模式: {self.measurement_mode.get()}")
        
        # 根据模式调整测量次数
        if self.measurement_mode.get() == "模式一":
            measurements_needed = 5
        elif self.measurement_mode.get() == "模式二":
            measurements_needed = 3
        else:  # 模式三
            measurements_needed = 5
            
        for i in range(measurements_needed):
            self.print_to_monitor("Measurement {}".format(i + 1))
            self.perform_measurement()
            if i < measurements_needed - 1:  # 不在最后一次测量后显示图片
                self.show_image()
        
        if self.actual_headlength_cm is not None and self.actual_bodylength_cm is not None:
            self.status_label.config(text="测量完成！", fg="green")

    def print_to_monitor(self, message):
        """在监控区域显示消息"""
        self.monitor_text_widget.insert(tk.END, message + "\n")
        self.monitor_text_widget.see(tk.END)  # Scroll to the end


if __name__ == "__main__":
    try:
        app = EnhancedMeasurementTool()
    except Exception as e:
        print(f"程序启动错误: {e}")
        input("按回车键退出...")
