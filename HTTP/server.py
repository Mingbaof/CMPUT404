"This is a basic Python3 HTTP 1.1 server"

import socketserver
import pathlib

"Basic settings"
HOST = "0.0.0.0"
PORT = 8001
BUFSIZE = 4096
LINE_ENDING = '\r\n'
SERVE_PATH = pathlib.Path('www').resolve()
HTTP_1_1 = 'HTTP/1.1'

class LabServer(socketserver.TCPServer):
    "Server class"
    allow_reuse_address = True

class LabServerTCPHandler(socketserver.StreamRequestHandler):
    "Handler for incoming TCP requests"

    def __init__(self, *args, **kwargs):
        self.charset = 'utf-8'
        self.server_path = pathlib.Path("www").resolve()
        super().__init__(*args, **kwargs)

    def recieve_line(self):
        "Recieve a line from the client"
        return self.rfile.readline().strip().decode(self.charset, 'ignore')

    def send_line(self, line):
        "Send a line to the client"
        self.wfile.write((line + LINE_ENDING).encode(self.charset, 'ignore'))

    def get_content_type(self, file_path):
        "Get the content type of a file"
        extention = file_path.suffix.lower()
        if extention == '.html':
            return 'text/html'
        elif extention == '.css':
            return 'text/css'
        elif extention == '.js':
            return 'text/javascript'
        elif extention == '.png':
            return 'image/png'
        elif extention == '.jpg' or extention == '.jpeg':
            return 'image/jpeg'
        else:
            return 'application/octet-stream'

    def handle(self):
        "Handle incoming requests"
        try:
            start_line = self.recieve_line()
            print("<", start_line)

            # Parse the start line
            method, path, _ = start_line.split(' ')

            if method != 'GET':
                self.send_line(f'{HTTP_1_1} 405 Method Not Allowed')
                return

            # the file is the root, absolute form is just the authority
            if path == '/':
                path = '/index.html'

            file_path = self.server_path / path.strip('/')

            if '..' in path.split('/'):
                self.send_line(f"{HTTP_1_1} 403 Forbidden")
                self.send_line('')
                return

            # base case: path to file
            elif file_path.is_file():

                # open and parse the file content
                with file_path.open('rb') as file:
                    content = file.read()
                    content_type = self.get_content_type(file_path)

                    response_line = f"{HTTP_1_1} 200 OK"
                    headers = f"Content-Type: {content_type}{LINE_ENDING}Content-Length: {len(content)}"
                    self.send_line(response_line)
                    self.send_line(headers)

                    # seprate the headers and the binary body
                    self.send_line('')
                    self.wfile.write(content)

            # path to a directory where the default is inside, and not ending with /
            elif file_path.is_dir() and (file_path / 'index.html').is_file():

                # redirection
                self.send_line(f"{HTTP_1_1} 301 Moved Permanently")
                headers = f"Location: {path.rstrip("/")}/index.html/"
                self.send_line(headers)
                return

            # illegal path
            else:
                self.send_line(f"{HTTP_1_1} 404 Not Found")
                self.send_line('')

        except Exception as e:
            print(e)

def main():
    "Main function"
    server = LabServer((HOST, PORT), LabServerTCPHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
