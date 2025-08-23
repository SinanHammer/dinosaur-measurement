import math
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageTk
import os
import sys


class SimpleMeasurementTool:
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

        self.root = tk.Tk()
        self.root.geometry("800x600")
        self.root.title("恐龙测量工具 - 简化版")
        
        # 创建主框架
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        self.control_frame = tk.Frame(self.main_frame, width=200)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 图片选择
        self.select_image_button = tk.Button(self.control_frame, text="选择图片", command=self.select_image, width=20)
        self.select_image_button.pack(pady=5)
        
        # 比例设置
        self.ratio_label = tk.Label(self.control_frame, text="比例尺长度 (cm):")
        self.ratio_label.pack(pady=5)
        self.ratio_entry = tk.Entry(self.control_frame, width=20)
        self.ratio_entry.pack(pady=5)
        self.set_ratio_button = tk.Button(self.control_frame, text="设置比例", command=self.set_pixels_to_length_ratio, width=20)
        self.set_ratio_button.pack(pady=5)
        
        # 测量按钮
        self.measurement_button = tk.Button(self.control_frame, text="开始测量", command=self.start_measurement, width=20)
        self.measurement_button.pack(pady=5)
        
        # 保存按钮
        self.save_button = tk.Button(self.control_frame, text="保存结果", command=self.save_measurement, width=20)
        self.save_button.pack(pady=5)
        
        # 重置按钮
        self.reset_button = tk.Button(self.control_frame, text="重置", command=self.reset_measurement, width=20)
        self.reset_button.pack(pady=5)
        
        # 状态显示
        self.status_label = tk.Label(self.control_frame, text="状态: 未开始", wraplength=180)
        self.status_label.pack(pady=10)
        
        # 右侧图片显示区域
        self.image_frame = tk.Frame(self.main_frame)
        self.image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 图片画布
        self.canvas = Canvas(self.image_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        
        # 信息显示区域
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.info_text = tk.Text(self.info_frame, height=6, wrap=tk.WORD)
        self.info_text.pack(fill=tk.X)
        
        self.root.mainloop()

    def select_image(self):
        """选择图片文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            try:
                self.image_path = file_path
                self.image = Image.open(file_path)
                self.display_image()
                self.print_info(f"图片加载成功: {os.path.basename(file_path)}")
                self.status_label.config(text="状态: 图片已加载")
            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片: {e}")

    def display_image(self):
        """在画布上显示图片"""
        if self.image:
            # 获取画布大小
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
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
            self.canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
            
            # 保存缩放比例用于坐标转换
            self.scale_factor = scale

    def set_pixels_to_length_ratio(self):
        """设置像素到实际长度的比例"""
        try:
            ratio = float(self.ratio_entry.get())
            if ratio <= 0:
                raise ValueError("比例必须大于0")
            self.pixels_to_length_ratio = ratio
            self.print_info(f"比例尺已设置为: {ratio} cm")
        except ValueError as e:
            messagebox.showerror("错误", f"请输入有效的数字: {e}")

    def start_measurement(self):
        """开始测量流程"""
        if not self.image:
            messagebox.showerror("错误", "请先选择图片")
            return
        
        if self.pixels_to_length_ratio <= 0:
            messagebox.showerror("错误", "请先设置比例尺")
            return
        
        self.current_measurement = 0
        self.distance_pixels = []
        self.points = []
        self.status_label.config(text=f"状态: 测量 {self.measurement_names[0]}")
        self.print_info("开始测量，请点击两个点...")

    def on_canvas_click(self, event):
        """处理画布左键点击"""
        if self.current_measurement >= 5:
            return
        
        # 转换坐标
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
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
        self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="red", outline="red")
        if len(self.points) == 2:
            # 绘制连线
            x1, y1 = self.points[0]
            x2, y2 = self.points[1]
            # 转换回画布坐标
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
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
            
            self.canvas.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2, fill="blue", width=2)

    def redraw_points(self):
        """重新绘制所有点"""
        self.canvas.delete("all")
        if self.photo:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            x = (canvas_width - self.photo.width()) // 2
            y = (canvas_height - self.photo.height()) // 2
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
        
        for i, point in enumerate(self.points):
            # 转换坐标
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
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
            
            self.canvas.create_oval(canvas_x-3, canvas_y-3, canvas_x+3, canvas_y-3, fill="red", outline="red")
            
            if i == 1 and len(self.points) == 2:
                # 绘制连线
                canvas_x1 = self.points[0][0] * scale + x_offset
                canvas_y1 = self.points[0][1] * scale + y_offset
                self.canvas.create_line(canvas_x1, canvas_y1, canvas_x, canvas_y, fill="blue", width=2)

    def complete_measurement(self):
        """完成一次测量"""
        if len(self.points) == 2:
            distance = self.calculate_distance(self.points[0], self.points[1])
            self.distance_pixels.append(distance)
            
            self.print_info(f"{self.measurement_names[self.current_measurement]}: {distance:.2f} 像素")
            
            self.current_measurement += 1
            self.points = []
            
            if self.current_measurement < 5:
                self.status_label.config(text=f"状态: 测量 {self.measurement_names[self.current_measurement]}")
                self.print_info("请继续点击两个点...")
            else:
                self.calculate_results()

    def calculate_distance(self, point1, point2):
        """计算两点间距离"""
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def calculate_results(self):
        """计算最终结果"""
        if len(self.distance_pixels) == 5:
            # 计算头部长度
            self.actual_headlength_cm = ((self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio) * (
                        self.distance_pixels[3] / self.distance_pixels[2])
            
            # 计算身体长度
            self.actual_bodylength_cm = ((self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio) * (
                        self.distance_pixels[4] / self.distance_pixels[2])
            
            self.print_info(f"头部长度: {self.actual_headlength_cm:.2f} cm")
            self.print_info(f"身体长度: {self.actual_bodylength_cm:.2f} cm")
            
            self.status_label.config(text="状态: 测量完成")
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
            self.print_info(f"结果已保存到: {output_file}")
            messagebox.showinfo("成功", "测量结果已保存！")

    def reset_measurement(self):
        """重置测量"""
        self.current_measurement = 0
        self.distance_pixels = []
        self.points = []
        self.actual_headlength_cm = None
        self.actual_bodylength_cm = None
        self.status_label.config(text="状态: 已重置")
        self.print_info("测量已重置")
        self.redraw_points()

    def print_info(self, message):
        """在信息区域显示消息"""
        self.info_text.insert(tk.END, message + "\n")
        self.info_text.see(tk.END)


if __name__ == "__main__":
    try:
        app = SimpleMeasurementTool()
    except Exception as e:
        print(f"程序启动错误: {e}")
        input("按回车键退出...")
