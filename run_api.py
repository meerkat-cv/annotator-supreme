import annotator_supreme

if __name__ == "__main__":
    app = annotator_supreme.build_app()
    app.logger.info("Staring app on port {} ...".format(4242))
    app.run(debug = app.debug, host='0.0.0.0', port=4242)

    
