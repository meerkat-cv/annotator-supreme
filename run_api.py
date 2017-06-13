import annotator_supreme

if __name__ == "__main__":
    app = annotator_supreme.build_app()
    app.run(debug=True, host='0.0.0.0', port=4242)
    print("Running app on port {}".format(4242))
