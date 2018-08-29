import PySimpleGUI as sg


def captcha_input(img_path):
    with sg.FlexForm('验证码输入') as form:
        layout = [
            [sg.Image(filename=img_path)],
            [sg.Text('输入上述图片中的字母或数字：', auto_size_text=True)],
            [sg.InputText()],
            [sg.Submit('确认'), sg.Cancel('取消')]
        ]
    _, values = form.LayoutAndRead(layout)
    return values


if __name__ == '__main__':
    print(captcha_input(r'C:\Users\zhang\Desktop\test\test.png'))