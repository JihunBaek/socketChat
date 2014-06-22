import socket, sqlite3, crypt
import threading

#기본 socket 커넥션 설정
HOST = ''
PORT = 8097
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
users = []
login_users = {}

#sql3를 사용하기 위해 테이블과 데이터베이스 생성
con = sqlite3.connect('member.db')
cur = con.cursor()
#유저의 id를 유니크하게 primary key 설정
query = 'CREATE TABLE members(id TEXT PRIMARY KEY, password TEXT );'
try:#초기 테이블 생성 시도후 존재하면 pass
    cur.execute(query) #데이터베이스 초기 테이블 생성
    cur.commit()
except:
    pass

def service(conn):
    connect = sqlite3.connect('member.db') #같은 쓰레드내에서만 데이터베이스 커서가 공유되기에 다시 db 연결
    cursor = connect.cursor()
    try:
        while conn:
            recv_data = conn.recv(1024) #사용자가 보내는 데이터 받기
            recv_data = recv_data.decode('utf-8')
            print(">> " + recv_data)
            recv_split_data = recv_data.split()
            if recv_split_data[0] == 'REGISTER':
                try:
                    encrypted = crypt.crypt(recv_split_data[2], "22") #교수님의 암호화 코드(패스워드 암호화)
                    cursor.execute("INSERT INTO members VALUES (?,?);", (recv_split_data[1], encrypted))#암호화하여 db에 insert
                    connect.commit()
                    conn.send("232 User register success".encode('utf-8'))
                    print("<< " + "232 User register success")
                except: #데이터베이스에 있는 사용자id일 경우 리턴
                    conn.send("510 User register fail".encode('utf-8'))
                    print("<< " + "510 User register fail")
            elif recv_split_data[0] == 'USER': #로그인
                try:
                    encrypted = crypt.crypt(recv_split_data[2], "22")
                    #사용자의 데이터를 암호화하여 비교하고 데이터베이스에서 select로 사용자의 id가 있는지 찾고 가져온다
                    cursor.execute("SELECT id, password FROM members WHERE id=?", (recv_split_data[1],))
                    user = cursor.fetchone() #결과값의 처음 데이터만 가져온다. id가 유니크키이기에 하나만 가져와도 된다
                    if user[1] == encrypted: #데이터베이스에 있는 것과 유저가 보낸데이터를 암호화한것을 비교
                        conn.send("230 User logged in".encode('utf-8'))
                        print("<< " + "230 User loggen in")
                        login_users[conn] = recv_split_data[1] #login user id 저장
                    else:
                        conn.send("531 invalid user or password".encode('utf-8'))
                        print("<< " + "531 invalid user or password")
                except:
                    conn.send("531 invalid user or password".encode('utf-8'))
                    print("<< " + "531 invalid user or password")
            elif recv_split_data[0] == 'LIST': #리스트 데이터를 유저에게 전송
                user_list = ""
                if login_users:
                    for each in login_users:
                        user_list = user_list + login_users[each] + " "
                    conn.send(("231 Users: " + user_list).encode('utf-8'))
                    print("<< 231 Users: " + user_list)
            elif recv_split_data[0] == 'QUIT': #quit 요청을 받았을때
                conn.send(("221 service closeing server close this socket").encode('utf-8'))
                print("<< 221 service closeing server close this socket")
                del login_users[conn] #login된 유저딕셔너리에 있는 데이터 삭제
                users.remove(conn) #소켓 정보 삭제
                conn.close() #소켓 종료
                break

            elif recv_split_data[0] == 'FROM': #사용자가 보낸 FROM 메시지 처리
                for each in users:
                    if each is conn:
                        each.send(("200 OK").encode('utf-8'))
                        print("<< 200 OK")
                    else:
                        each.send(("299 " + recv_data).encode('utf-8'))
                        print("<< 299" + recv_data)
    except:#오류가 발생할 경우 유저와의 연결을 종료시킨다.
        users.remove(conn)
        del login_users[conn]
        conn.close()

while 1: #사용자들의 접속을 계속 받는 루프문
    conn, addr = s.accept()
    global users, login_users
    print(str(conn) + " 접속")
    users.append(conn)
    threading._start_new_thread(service, (conn, )) #service 함수를 쓰레드로 실행
    pass
