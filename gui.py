from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
from detector import Detector
import os
import threading


class Application(Frame):

    def __split_file_name(self, filename):
        filepath, tempfilename = os.path.split(filename)
        shotname, extension = os.path.splitext(tempfilename)
        return shotname

    def __detect(self):
        if self.img_path['text'] == '未选择图片' or self.target_path['text'] == '未选择文件夹':
            tkinter.messagebox.showinfo('提示', '请先选择文件！')
            return

        if self.detect_thread is not None:
            if self.detect_thread.is_alive():
                tkinter.messagebox.showinfo('提示', '正在检测其他大图片，请等待！')
                return
            else:
                self.detect_thread = None

        img_name = self.__split_file_name(self.img_path['text'])
        target_dir = os.path.join(self.target_path['text'], img_name)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        # 得到复选框的选项
        err_choice = {}
        for k, v in self.err_types.items():
            err_choice[k] = v.get()
        # print(err_choice)

        detector = Detector(self.text, err_choice=err_choice)
        self.detect_thread = threading.Thread(target=detector.detect, args=(self.img_path['text'], target_dir))
        self.detect_thread.start()

    def __choose_directory(self, lb):
        directory = tkinter.filedialog.askdirectory()
        if directory != '':
            lb.config(text=directory)
        else:
            lb.config(text="未选择文件夹")

    def __choose_file(self, lb):
        filename = tkinter.filedialog.askopenfilename(filetypes=[('image files', ('.bmp', '.png', '.jpg')),
                                                                 ])
        if filename != '':
            lb.config(text=filename)
        else:
            lb.config(text="未选择图片")

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.detect_thread = None
        self.pack()
        row = 0

        self.img_path_lable = Label(master=self, text='请选择大图片路径')
        self.img_path_lable.grid(row=row, columnspan=2)
        row += 1
        self.img_path = Label(master=self, text='未选择图片', fg='gray')
        self.img_path.grid(row=row, column=0)
        self.img_btn = Button(master=self, text="选择大图片", command=lambda: self.__choose_file(self.img_path))
        self.img_btn.grid(row=row, column=1)
        row += 1

        self.target_path_lable = Label(master=self, text='请选择存放检测结果结果的文件夹')
        self.target_path_lable.grid(row=row, columnspan=2)
        row += 1
        self.target_path = Label(master=self, text='未选择文件夹', fg='gray')
        self.target_path.grid(row=row, column=0)
        self.target_btn = Button(master=self, text="选择文件夹", command=lambda: self.__choose_directory(self.target_path))
        self.target_btn.grid(row=row, column=1)
        row += 1

        # 复选框
        self.checkFrame = Frame(self)
        self.checkFrame.grid(row=row, columnspan=2)
        check_row = 0
        self.err_lable = Label(master=self.checkFrame, text='请勾选需要检测的异常类型')
        self.err_lable.grid(row=check_row, columnspan=2)
        check_row += 1
        self.err_types = {'断线异常': IntVar(value=1), '边界分岔': IntVar(value=1), '亮度异常': IntVar(value=1),
                          '弯曲异常': IntVar(value=1), '过粗过细': IntVar(value=1), '粗细变化过快': IntVar(value=1)}
        for i, type in enumerate(sorted(self.err_types.keys())):
            checkbutton = Checkbutton(master=self.checkFrame, text=type, variable=self.err_types[type])
            checkbutton.grid(row=check_row, column=i % 2)
            # print(type, self.err_types[type])
            if i % 2 == 1:
                check_row += 1
        row += 1

        self.start_btn = Button(master=self, text="开始检测", command=self.__detect)
        self.start_btn.grid(row=row, columnspan=2)
        row += 1

        self.textFrame = Frame(self)
        self.textFrame.grid(row=row, columnspan=2)
        self.text = Text(self.textFrame, height=10, width=50, state=DISABLED)  # , state=DISABLED
        self.text.pack(side=LEFT)
        self.bar = Scrollbar(self.textFrame)
        self.bar.pack(side=RIGHT, fill=Y)
        self.bar.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.bar.set)


if __name__ == '__main__':
    root = Tk()
    root.title('异常检测')
    app = Application(master=root)
    # root.geometry('500x300+500+200')

    root.minsize(300, 240)
    root.mainloop()
    # os.mkdir('D:/Code/Python/lineDetection/digital_img\\20180730-002')
