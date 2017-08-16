(function (global, $) {

    var Dataset = {},
        dataset_add_btn = $('#add-dataset-btn'),
        purge_btns = $(".bomb-btn"),
        confirm_delete_btn = $("#confirm-delete-button"),
        add_dataset_btn = $("#add-dataset-btn"),
        save_dataset_btn = $("#save-changes-btn");

    Dataset.init = function () {
        this.bindButtons();
        this.initSlider();
        this.TRAINING_PERCENTAGE = 80/100.0;
    };

    Dataset.bindButtons = function() {
        var self = this;
        dataset_add_btn.click(function(e) {
            e.preventDefault();
        });

        purge_btns.off('click').on('click', function (event) {
            var dataset = $(this).data("dataset");
            self.dataset_to_remove = dataset;
            $('#confirm-delete-dataset-label').html(dataset);
            $('#modal-confirm-delete').modal('show');
        });

        confirm_delete_btn.click(function() {
            self.purgeDataset(self.dataset_to_remove);
        })

        add_dataset_btn.click(function () {
            $('#modal-dataset').modal('show');    
        });

        save_dataset_btn.click(function() {
            var data = {
                "name": $("#datasetName").val(),
                "tags": $("#tagsInput").tagsinput('items')
            }
            $.ajax({
                    url: '/annotator-supreme/dataset/create',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(data),
                success: function(result) {
                    console.log("Done!");
                    window.location.reload();
                }
            });
        });

        $("#part-dataset-btn").click(function() {
            var post_data = {
                "partitions": ["training", "testing"],
                "percentages": [self.TRAINING_PERCENTAGE, 1-self.TRAINING_PERCENTAGE]
            }
            $.ajax({
                url: '/annotator-supreme/dataset/' + $("#dataset-sel").val() + "/partition",
                type: 'POST',
                data: JSON.stringify(post_data),
                contentType: 'application/json',
                success: function(result) {
                    console.log("ok");
                },
                error: function() {
                    console.log("error");
                }
            })
        });


        $("#check-supreme-server-btn").click(function() {
            var btn = $(this);
            btn.html('<i class="fa fa-refresh"></i>\nCheck')
            $.ajax({
                url: $("#supreme-url").val() + '/version',
                type: 'GET',
                success: function(d) {
                    console.log("Cool, ok!",d);
                    btn.html('<i class="fa fa-check"></i>\nCheck')

                },
                error: function() {
                    console.log("yaks, is off")
                    btn.html('<i class="fa fa-close"></i>\nCheck')
                }
            })
        });

        $("#export-dataset-btn").click(function() {
            global.Main.enableLoading("Exporting all...");
            self.checkIfDatasetExist(self.sendImages.bind(self));
        });
    }


    Dataset.checkIfDatasetExist = function(callback) {
        var self = this,
            dataset_name = $("#dataset-sel-export").val();
        $.ajax({
            url: $("#supreme-url").val()+"/dataset/"+dataset_name,
            type: 'GET',
            success: function(data) {
                // if exists, for now, dont accept
                console.log("Dataset already exists, cancelled.");
                global.Main.disableLoading();
            },
            statusCode: {
                404: function() {
                    // dataset does not exist, so create and send all images
                    var data = {
                        "name": dataset_name,
                        "tags": ["exported"]
                    };
                    $.ajax({
                        url: $("#supreme-url").val()+"/dataset/create",
                        type: 'POST',
                        data: JSON.stringify(data),
                        contentType: "application/json",
                        success: function () {
                            fn = callback.bind(self);
                            fn();
                        },
                        error: function() {
                            console.log("Could not create dataset remotely.");            
                            global.Main.disableLoading();
                        }
                    });
                }
            }
        });
    }



    toDataURL = function(i, url, callback) {
        var xhr = new XMLHttpRequest();
        xhr.onload = function () {
            var reader = new FileReader();
            reader.onloadend = function () {
                callback(i, reader.result);
            }
            reader.readAsDataURL(xhr.response);
        };
        xhr.open('GET', url);
        xhr.responseType = 'blob';
        xhr.send();
    }

    Dataset.sendImages = function () {
        var self = this,
            dataset = $("#dataset-sel-export").val();
        $.ajax({
            url: "/annotator-supreme/image/"+dataset+"/all",
            type: 'GET',
            success: function(data) {
                console.log("Cool, ok!",data);
                var images = data.images;

                self.sendImageLoop(0, images);
            },
            error: function() {
                console.log("yaks, could not get image list");
                global.Main.disableLoading();
            }
        });
    }

    Dataset.sendImageLoop = function (i, images) {
        var dataset = $("#dataset-sel-export").val(),
            img_url = "/annotator-supreme/image/"+images[i].url,
            self = this;
        toDataURL(i, img_url, function(i, base64_img) {
            console.log("image cat", i);

            var data = {
                "category": images[i].category,
                "name": images[i].name,
                "imageB64": base64_img.replace("data:image/jpeg;base64,", "")
            };

            $.ajax({
                    url: $("#supreme-url").val()+"/image/" + dataset + "/add",
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(data),
                success: function(result) {
                    console.log("Added :", result);
                    var imageId = result.imageId;

                    self.sendAnnotation(images[i].phash, imageId);
                    if (i+1 < images.length) {
                        self.sendImageLoop(i+1, images);
                    }
                    else {
                        console.log("Finished all");
                        global.Main.disableLoading();    
                    }
                    
                },
                error: function(result) {
                    console.log("Error including image!");
                    global.Main.disableLoading();
                }
            });
            console.log("data", data);
        });
    }



    Dataset.sendAnnotation = function(localImageId, remoteImageId) {
        var dataset = $("#dataset-sel-export").val();
        $.ajax({
            url: "/annotator-supreme/image/anno/" + dataset + "/" + localImageId,
            type: 'GET',
            success: function(result) {
                console.log("anno", result);
                var data = {
                    "anno": result.anno
                }
                $.ajax({
                        url: $("#supreme-url").val()+"/image/anno/" + dataset + "/" + remoteImageId,
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify(data),
                    success: function(result) {
                        console.log("Added annotation!:", result);
                    },
                    error: function(result) {
                        console.log("Error including annotation!");
                        global.Main.disableLoading();
                    }
                });

            },
            error: function() {
                global.Main.disableLoading();
                console.log("Unable to obtain annotation of image!");
            }
        });
    }




    Dataset.initSlider = function () {
        var self = this;
        this.slider = new Slider('#percentageSlider', {
            formatter: function (value) {
                return 'Training percentage: ' + value + '%.';
            }
        }).on('slide', function (value) {
            self.TRAINING_PERCENTAGE = parseInt(value, 10)/100.0;
            $('.part-percentage.training').html(value+"%");
            $('.part-percentage.testing').html((100-value)+"%");
        });
    } 

    Dataset.purgeDataset = function(dataset) {
        // make the request to remove dataset and associated images
        $.ajax({
            url: '/annotator-supreme/dataset/'+dataset,
            type: 'DELETE',
            success: function(result) {
                window.location.reload();
            }
        });
    }

    global.Dataset = Dataset;
    global.Dataset.init();

}(window, jQuery));