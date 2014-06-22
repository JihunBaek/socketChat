import tkinter, socket
import tkinter.messagebox
import threading

# 기본 socket 커넥션 설정
HOST = "127.0.0.1"
PORT = 8097
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
debug = 0
window = tkinter.Tk()
window.configure(background="#a1abcd")
window.title("지영's 채팅 클라이언트")
window.geometry('700x700') #프로그램 사이즈 설정
recv_chat_window = tkinter.Text(window) #서버에서 받은 데이터를 보여주는 창
send_chat_data = tkinter.Entry(window) #사용자의 입력을 받는 창
user_id = "" #로그인 유저 아이디 저장

def gettingMsg():
    global debug, user_id
    while True:
        recv_data = s.recv(1024).decode('utf-8')
        recv_split_data = recv_data.split(" ") #받은 데이터 파싱하기 위해 문자열 자르기

        if debug is 1: #디버그 모드일때 출력하기 위함
            recv_chat_window.insert(tkinter.INSERT, ">> " + recv_data + '\n')
        else:
            if recv_split_data[0] is 531:
                recv_chat_window.insert(tkinter.INSERT, recv_data + '\n')

        if recv_split_data[0] == '230': #230값을 받았을때 ui바꾼다
            tkinter.messagebox.showinfo("로그인 결과", "로그인 성공.채팅화면으로 이동합니다")
            user_id = login_id.get()
            labelInst.pack_forget()
            register_id.pack_forget()
            register_password.pack_forget()
            login_id.pack_forget()
            login_password.pack_forget()
            btn_login.pack_forget()
            btn_register.pack_forget()
            recv_chat_window.pack()
            send_chat_data.pack()
            send_chat_data.bind('<Return>', send_data) #텍스트 입력창에 엔터키 이벤트를 바인딩

        if recv_split_data[0] == '221': #221값을 받았을때 서비스 종료
            global window
            window.destroy()
            s.close()

        if recv_split_data[0] == '299' or recv_split_data[0] == '231': #299나 231일때 파싱하여 출력
            message = recv_data.split(' ', 2)
            recv_chat_window.insert(tkinter.INSERT, message[2] + '\n')

        if recv_split_data[0] == '232': #회원가입 성공 메시지
            tkinter.messagebox.showinfo("회원가입 결과", "가입이 완료되었습니다. 로그인 해주세요")
        elif recv_split_data[0] == '510': #회원가입 실패 메시지
            tkinter.messagebox.showinfo("회원가입 결과", "이미 존재하는 아이디입니다. 다른 아이디를 입력하세요")

    s.close()

def print_debug(data): #디버그 모드일때 출력하는 함수
    global debug
    if debug is 1:
        recv_chat_window.insert(tkinter.INSERT, "<< "  + data + '\n')

def send_data(event): #텍스트 입력창에 바인딩된 함수로서 서버에 데이터를 보내는 역할
    global debug, user_id
    message = send_chat_data.get()
    recv_chat_window.insert(tkinter.INSERT, send_chat_data.get() + '\n')
    temp_message = message.split(" ")

    if temp_message[0] == '.list': #사용자의 입력값을 파싱하여 서버에 데이터를 보낸다
        s.send(("LIST").encode('utf-8'))
        print_debug("LIST")
    elif temp_message[0] == '.quit':
        s.send(("QUIT").encode('utf-8'))
        print_debug("QUIT")
    elif temp_message[0] == '.debug':
        if debug is 0:
            debug = 1
            recv_chat_window.insert(tkinter.INSERT, "debug mode on" + '\n') #텍스트창에 출력
        else:
            debug = 0
            recv_chat_window.insert(tkinter.INSERT, "debug mode off" + '\n')
    else:
        s.send(("FROM " + user_id + ": " + message).encode('utf-8'))
        print_debug(("FROM " + user_id + ": " + message))

    send_chat_data.delete(0, tkinter.END)

def register(): # btn_register에 반응하는 함수
    str = "REGISTER " + register_id.get() + " " + register_password.get()
    s.send(str.encode('utf-8'))
    register_id.delete(0, tkinter.END)
    register_password.delete(0, tkinter.END)

def login(): # btn_login에 반응하는 함수
    login_message = "USER " + login_id.get() + " " + login_password.get()
    s.send(login_message.encode('utf-8'))

#소켓 데이터 읽기 쓰레드 활성화(gettingMsg 함수가 쓰레드로 실행된다)
threading._start_new_thread(gettingMsg,())

#명령어 메뉴
labelInst = tkinter.Label(window, text="메뉴를 고르세요", bg="#383a39", fg="#a1abcd", font=("Helvetica", 16))
labelInst.pack()

#회원가입에 관련된 ui 설정
register_id = tkinter.Entry(window)
register_password = tkinter.Entry(window)
btn_register = tkinter.Button(window, text="회원가입", bg="#383a39", fg="#a1abcd", command=register)
register_id.pack()
register_password.pack()
btn_register.pack()

#로그인에 관련된 ui 설정
btn_login = tkinter.Button(window, text="Login", bg="#383a39", fg="#a1abcd", command=login)
login_id = tkinter.Entry(window)
login_password = tkinter.Entry(window)
login_id.pack()
login_password.pack()
btn_login.pack()
window.mainloop()