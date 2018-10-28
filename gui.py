from tkinter import *
import tkinter.filedialog


class Application(Frame):

    def __chose_file(self, lb):
        filename = tkinter.filedialog.askopenfilename()
        if filename != '':
            lb.config(text="选择的文件是：" + filename)
        else:
            lb.config(text="未选择任何文件")

    def createWidgets(self):
        path_lable = Label(master=self, text='请选择大图片路径')
        path_lable.grid(row=0, columnspan=2)
        img_path = Label(master=self, text='未选择任何文件')
        img_path.grid(row=1, column=0)
        img_btn = Button(master=self, text="弹出选择文件对话框", command=lambda: self.__chose_file(img_path))
        img_btn.grid(row=1, column=1)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()


if __name__ == '__main__':
    root = Tk()
    app = Application(master=root)
    # root.geometry('500x300+500+200')
    root.mainloop()
