import annotator_supreme

if __name__ == "__main__":
    app = annotator_supreme.build_app()
    print("Staring app on port {} ...".format(4242))
    app.run(debug=True, host='0.0.0.0', port=4242)
