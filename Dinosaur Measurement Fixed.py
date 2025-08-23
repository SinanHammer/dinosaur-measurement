import cv2
import math
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import os
import sys


class MeasurementTool:
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

        # 设置matplotlib后端为TkAgg以确保与tkinter兼容
        plt.switch_backend('TkAgg')
        
        self.root = tk.Tk()
        self.root.geometry("600x400")
        self.root.title("Dinosaur Measurement - Windows 11 Compatible")
        
        # 设置DPI感知以改善Windows 11显示
        try:
            self.root.tk.call('tk', 'scaling', 1.0)
        except:
            pass
            
        self.label = tk.Label(self.root, text="图片路径:")
        self.label.pack()
        self.image_path_text_widget = tk.Text(self.root, height=1.5)
        self.image_path_text_widget.pack()
        self.select_image_button = tk.Button(self.root, text="选择图片", command=self.select_image)
        self.select_image_button.pack()

        self.ratio_label = tk.Label(self.root, text="Length of bar (cm):")
        self.ratio_label.pack()
        self.ratio_entry = tk.Entry(self.root)
        self.ratio_entry.pack()
        self.set_ratio_button = tk.Button(self.root, text="设置比例", command=self.set_pixels_to_length_ratio)
        self.set_ratio_button.pack()

        self.measurement_button = tk.Button(self.root, text="测量", command=self.run)
        self.measurement_button.pack()
        self.save_button = tk.Button(self.root, text="保存测量结果", command=self.save_measurement)
        self.save_button.pack()

        self.monitor_text_widget = tk.Text(self.root, height=10)
        self.monitor_text_widget.pack()

        self.root.mainloop()

    def select_image(self):
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
                self.print_to_monitor("图片加载成功: {}".format(os.path.basename(self.image_path)))

    def set_pixels_to_length_ratio(self):
        ratio_text = self.ratio_entry.get()
        try:
            self.pixels_to_length_ratio = float(ratio_text)
            self.print_to_monitor("Length of bar已设置为: {}".format(self.pixels_to_length_ratio))
        except ValueError:
            self.print_to_monitor("无效的比例值")
            messagebox.showerror("错误", "请输入有效的数字")

    def mouse_callback(self, event, x, y, flags, param):
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
        if len(self.distance_pixels) == 5:
            self.actual_headlength_cm = ((self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio) * (
                        self.distance_pixels[3] / self.distance_pixels[2])
            self.print_to_monitor("Actual headLength: {} cm".format(self.actual_headlength_cm))
            self.actual_bodylength_cm = ((self.distance_pixels[1] / self.distance_pixels[0]) * self.pixels_to_length_ratio) * (
                        self.distance_pixels[4] / self.distance_pixels[2])
            self.print_to_monitor("Actual bodyLength: {} cm".format(self.actual_bodylength_cm))

    def calculate_distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def save_measurement(self):
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
        if self.image is not None:
            plt.figure(figsize=(8, 6))
            plt.imshow(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
            plt.axis('off')
            plt.title("当前图片")
            plt.show()

    def run(self):
        if self.image is None:
            messagebox.showerror("错误", "请先选择图片")
            return
            
        for i in range(5):
            self.print_to_monitor("Measurement {}".format(i + 1))
            self.perform_measurement()
            if i < 4:  # 不在最后一次测量后显示图片
                self.show_image()

    def print_to_monitor(self, message):
        self.monitor_text_widget.insert(tk.END, message + "\n")
        self.monitor_text_widget.see(tk.END)  # Scroll to the end


if __name__ == "__main__":
    try:
        a = MeasurementTool()
    except Exception as e:
        print(f"程序启动错误: {e}")
        input("按回车键退出...")
