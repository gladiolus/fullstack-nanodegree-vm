from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(self.path.encode())


if __name__ == "__main__":
    httpd = None
    try:
        port = 8000
        address = ""
        httpd = HTTPServer((address, port), HTTPRequestHandler)
        print("Running web server on port {}".format(port))
        httpd.serve_forever()
    except BaseException:
        print("Stopping server ...")
        httpd.server_close()
