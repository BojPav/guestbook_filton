#!/usr/bin/env python
import os
import jinja2
import webapp2
from models import Guestbook
import cgi
from models import Uporabnik
from google.appengine.api import users

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            logiran = True
            logout_url = users.create_logout_url('/')

            params = {"logiran": logiran, "logout_url": logout_url, "user": user}
        else:
            logiran = False
            login_url = users.create_login_url('/')

            params = {"logiran": logiran, "login_url": login_url, "user": user}
        return self.render_template("hello.html", params)

    def post(self):     # shranjevanje user emaila v sporocilo model
        user_email = user.email()
        save_user_email = Guestbook(sporocilo=user_email)
        save_user_email.put()

        return self.render_template("hello.html", params)


class RezutatHandler(BaseHandler):
    def post(self):
        ime = self.request.get("ime")
        priimek = self.request.get("priimek")
        email = self.request.get("email")
        sporocilo = self.request.get("sporocilo")
        #   datum = self.request.get("nastanek")   # datume generira avtomaticno

        sporocilo = cgi.escape(sporocilo)  # prepreci javascript injection

        guestbook = Guestbook(ime=ime, priimek=priimek, email=email, sporocilo=sporocilo)
        guestbook.put()

        return self.write("You have successfully added your message...click back on your browser.")


class SeznamSporocilHandler(BaseHandler):
    def get(self):
        seznam = Guestbook.query().fetch()
        params = {"seznam": seznam}
        return self.render_template("seznam_sporocil.html", params=params)


class PosameznoSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Guestbook.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("posamezno_sporocilo.html", params=params)


class UrediSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Guestbook.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("uredi_sporocilo.html", params=params)

    def post(self, sporocilo_id):
        vnos = self.request.get("vnos")
        sporocilo = Guestbook.get_by_id(int(sporocilo_id))
        sporocilo.sporocilo = vnos
        sporocilo.put()
        return self.redirect_to("seznam-sporocil")


class IzbrisiSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Guestbook.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("izbrisi_sporocilo.html", params=params)

    def post(self, sporocilo_id):
        sporocilo = Guestbook.get_by_id(int(sporocilo_id))
        sporocilo.key.delete()
        return self.redirect_to("seznam-sporocil")


class RegistracijaHandler(BaseHandler):
    def get(self):
        return self.render_template("registracija.html")

    def post(self):
        ime = self.request.get("ime")
        priimek = self.request.get("priimek")
        email = self.request.get("email")
        geslo = self.request.get("geslo")

        if "@" in email:
            novi_uporabnik = Uporabnik(ime=ime, priimek=priimek, email=email, geslo=geslo)
            novi_uporabnik.put()
        else:
            return self.write("Niste vpisali svoj email...")

        return self.redirect_to("main")


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="main"),
    webapp2.Route('/rezultat', RezutatHandler),
    webapp2.Route('/seznam-sporocil', SeznamSporocilHandler, name="seznam-sporocil"),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', PosameznoSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/uredi', UrediSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/izbrisi', IzbrisiSporociloHandler),
    webapp2.Route('/registracija', RegistracijaHandler),
], debug=True)
