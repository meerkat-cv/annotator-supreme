import annotator_supreme
import tornado

if __name__ == "__main__":
    tornado_app = annotator_supreme.build_app()
    tornado_app.listen(4242)
    print("Running app on port {}".format(4242))
    tornado.ioloop.IOLoop.instance().start()
