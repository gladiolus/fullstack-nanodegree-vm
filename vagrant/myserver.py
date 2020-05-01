from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi
from database_setup import DBSession, Restaurant, RestaurantSession

NEW_LINK = "/restaurants/new"
LIST_LINK = "/restaurants"
EDIT_LINK = "/edit"
DELETE_LINK = "/delete"


def postform(path, action):
    form = "<form method='POST' enctype='multipart/form-data' action='{path}'>" \
           "<input name='restaurantName' type='text'  placeholder = 'Restaurant Name'>" \
           "<input name='action' type='submit' value='{action}'>" \
           " </form>"
    return form.format(path=path, action=action)


def wrapwithbody(text):
    return "".join(["<html><body>", text, "</body></html>"])


def wrapwithh1(text):
    return "".join(["<h1>", text, "</h1>"])


def link(text, link=None):
    link = link if link else text
    return " <a href='{link}'>{text}</a>".format(text=text, link=link)


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def _create_ok_header(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _send_responce(self, out):
        out = wrapwithbody(out)
        print(out)
        self.wfile.write(out.encode("UTF-8"))
        return

    def _get_post_param(self):
        fields = None
        ctype, pdict = cgi.parse_header(self.headers.get("content-type"))
        if ctype == "multipart/form-data":
            fields = cgi.parse_multipart(self.rfile, pdict)
        return fields

    def _get_server_path(self):
        return self.path[ : -self.path.rfind("/")]

    def _restaurants(self):
        self._create_ok_header()
        path = self._get_server_path()
        out = ""
        out += link(text="Make a new restaurant here", link=path + NEW_LINK)
        out += "<br/><br/>"
        with DBSession() as sess:
            restaurants = sess.query(Restaurant).all()
            for rest in restaurants:
                out += "".join(["<br/>",
                                str(rest.name),
                                link("Edit", link="/{}/edit".format(rest.id)),
                                link("Delete", link="/{}/delete".format(rest.id))
                                ])
        self._send_responce(out)

    def _new_restaurant_form(self):
        self._create_ok_header()
        out = ""
        out += wrapwithh1("Create a new Restaurant.")

        out += postform(self.path, action='Create')
        self._send_responce(out)

    def _edit_restaurant_form(self):
        self._create_ok_header()
        id = self.path.split("/")[-2]
        sess = RestaurantSession()
        restaurant = sess.query(Restaurant).filter_by(id=id).first()
        out = ""
        out += wrapwithh1("Edit the existing Restaurant {}.".format(restaurant.name))

        out += postform(self.path, action='Rename')
        self._send_responce(out)

    def _delete_restaurant_form(self):
        self._create_ok_header()
        out = ""
        id = self.path.split("/")[-2]
        with DBSession() as sess:
            restaurant = sess.query(Restaurant).filter_by(id=id).first()
            nameofrestaurant = restaurant.name

        out += wrapwithh1("Are you sure that you want to delete the Restaurant {}?".format(nameofrestaurant))
        out += "<form method='POST' enctype='multipart/form-data' action='{}'>" \
               "<input name='action' type='submit' value='Delete'>" \
               " </form>".format(self.path)

        out += "<br/>"
        out += link(text="Back to Restaurants list", link=LIST_LINK)
        self._send_responce(out)

    def do_GET(self):
        print(self.log_request())
        try:
            if self.path.endswith(NEW_LINK):
                return self._new_restaurant_form()
            elif self.path.endswith(LIST_LINK):
                return self._restaurants()
            elif self.path.endswith(EDIT_LINK):
                return self._edit_restaurant_form()
            elif self.path.endswith(DELETE_LINK):
                return self._delete_restaurant_form()
        except OSError:
            self.send_error(404, "Path not found {}".format(self.path))

    def do_POST(self):
        print(self.log_request())
        try:
            if self.path.endswith(NEW_LINK) or self.path.endswith(EDIT_LINK) or self.path.endswith(DELETE_LINK):
                self.send_response(301)
                self.send_header("Content-type", "text/html")
                self.send_header('Location', '/restaurants')
                out = ""
                if self.path.endswith(NEW_LINK):
                    fields = self._get_post_param()
                    nameofrestaurant = fields.get("restaurantName")[0] if fields else None
                    with DBSession() as sess:
                        restaurant = Restaurant(name=nameofrestaurant)
                        sess.add(restaurant)
                    out += wrapwithh1("Restaurant {} was added successfully!".format(nameofrestaurant))
                elif self.path.endswith(EDIT_LINK):
                    fields = self._get_post_param()
                    nameofrestaurant = fields.get("restaurantName")[0] if fields else None
                    if nameofrestaurant:
                        id = self.path.split("/")[-2]
                        with DBSession() as sess:
                            restaurant = sess.query(Restaurant).filter_by(id=id).first()
                            restaurant.name = nameofrestaurant
                        out += wrapwithh1("Restaurant {} was edited successfully!".format(nameofrestaurant))
                elif self.path.endswith(DELETE_LINK):
                    id = self.path.split("/")[-2]
                    with DBSession() as sess:
                        restaurant = sess.query(Restaurant).filter_by(id=id).first()
                        nameofrestaurant = restaurant.name
                        sess.delete(restaurant)
                    out += wrapwithh1("Restaurant {} was deleted successfully!".format(nameofrestaurant))

                out += "<br/>"
                out += link(text="Back to Restaurants list", link=LIST_LINK)
                self.end_headers()
                self._send_responce(out)
        except Exception as e:
            raise


if __name__ == "__main__":
    httpd = None
    try:
        port = 8080
        address = ""
        httpd = HTTPServer((address, port), HTTPRequestHandler)
        print("Running web server on port {}".format(port))
        httpd.serve_forever()
    except BaseException:
        print("Stopping server ...")
        httpd.server_close()
