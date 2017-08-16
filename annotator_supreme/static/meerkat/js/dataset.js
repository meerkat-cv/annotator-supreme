(function (global, $) {

    var Dataset = {},
        dataset_add_btn = $('#add-dataset-btn'),
        purge_btns = $(".bomb-btn"),
        confirm_delete_btn = $("#confirm-delete-button"),
        add_dataset_btn = $("#add-dataset-btn"),
        save_dataset_btn = $("#save-changes-btn"),
        merge_dataset_btn = $("#merge-dataset-btn");

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

        merge_dataset_btn.click(function() {
            global.Main.enableLoading("Merging dataset...");
            self.mergeDatasetsClick();
        })

        $("#transform-dataset-btn").click(function() {
            global.Main.enableLoading("Applying transformation...");
            self.ApplyTransformation($("#transform-dataset").val());
        })
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

    Dataset.mergeDatasetsClick = function() {
        var merge_dataset_out = $("#merge-dataset-output"),
            merge_dataset_in = $("#merge-dataset-input");
            input_datasets = merge_dataset_in.val(),
            output_dataset = merge_dataset_out.val();
        
        if (output_dataset in input_datasets) {
            console.warn("Output is in the input list, will duplicate your life man!");
        }

        this.sendDatasetsMerge(input_datasets, output_dataset);
    }


    Dataset.sendDatasetsMerge = function (input_datasets, output_dataset) {
        this.sendDatasetMergeLoop(0, input_datasets, output_dataset);
    }


    Dataset.sendDatasetMergeLoop = function (i, input_datasets, output_dataset) {
        var self = this,
            in_dataset = input_datasets[i];
        $.ajax({
            url: "/annotator-supreme/image/"+input_datasets[i]+"/all",
            type: 'GET',
            success: function(data) {
                console.log("Cool, ok!",data);
                var images = data.images;

                self.sendImageMergeLoop(0, images, in_dataset, output_dataset);
                if (i+1 < input_datasets.length) {
                    self.sendDatasetMergeLoop(i+1, input_datasets, output_dataset);
                }
            },
            error: function() {
                console.log("yaks, could not get image list");
                global.Main.disableLoading();
            }
        });    
    }





    Dataset.sendImageMergeLoop = function (i, images, input_dataset, output_dataset) {
        var img_url = "/annotator-supreme/image/"+images[i].url,
            only_w_anno = $("#only-with-anno-chk").prop("checked"),
            self = this;

        if (only_w_anno) {
            $.ajax({
                url: "/annotator-supreme/image/has_annotation/" + input_dataset + "/" + images[i].phash,
                type: 'GET',
                success: function(data) {
                    console.log("has anno?", data);
                    if (data.has_annotation) {
                        // ok, send the image then:
                        toDataURL(i, img_url, function(i, base64_img) {
                            // console.log("image cat", i);

                            var data = {
                                "category": images[i].category,
                                "name": images[i].name,
                                "imageB64": base64_img.replace("data:image/jpeg;base64,", "")
                            };

                            $.ajax({
                                    url: "/annotator-supreme/image/" + output_dataset + "/add",
                                    type: 'POST',
                                    contentType: 'application/json',
                                    data: JSON.stringify(data),
                                success: function(result) {
                                    console.log("Added :", result);
                                    var imageId = result.imageId;

                                    self.sendAnnotationMerge(images[i].phash, imageId, input_dataset, output_dataset);
                                    if (i+1 < images.length) {
                                        self.sendImageMergeLoop(i+1, images, input_dataset, output_dataset);
                                    }
                                    else {
                                        console.log("Finished all merging");
                                        global.Main.disableLoading();    
                                    }
                                    
                                },
                                error: function(result) {
                                    console.log("Error including image!");
                                    global.Main.disableLoading();
                                }
                            });
                            
                        });
                    }
                    else {
                        // just go in front
                        if (i+1 < images.length) {
                            self.sendImageMergeLoop(i+1, images, input_dataset, output_dataset);
                        }
                        else {
                            console.log("Finished all merging");
                            global.Main.disableLoading();    
                        }
                    }
                    
                },
                error: function() {
                    console.error("");
                }
            });
        }
        else {
            // dont need to verify if there is annotation
            toDataURL(i, img_url, function(i, base64_img) {
                // console.log("image cat", i);
                var data = {
                    "category": images[i].category,
                    "name": images[i].name,
                    "imageB64": base64_img.replace("data:image/jpeg;base64,", "")
                };

                $.ajax({
                        url: "/annotator-supreme/image/" + output_dataset + "/add",
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify(data),
                    success: function(result) {
                        console.log("Added :", result);
                        var imageId = result.imageId;

                        self.sendAnnotationMerge(images[i].phash, imageId, input_dataset, output_dataset);
                        if (i+1 < images.length) {
                            self.sendImageMergeLoop(i+1, images, input_dataset, output_dataset);
                        }
                        else {
                            console.log("Finished all merging");
                            global.Main.disableLoading();    
                        }
                        
                    },
                    error: function(result) {
                        console.log("Error including image!");
                        global.Main.disableLoading();
                    }
                });
            });
        }
    }


    Dataset.sendAnnotationMerge = function(inImageId, outImageId, input_dataset, output_dataset) {
        $.ajax({
            url: "/annotator-supreme/image/anno/" + input_dataset + "/" + inImageId,
            type: 'GET',
            success: function(result) {
                console.log("got anno from", input_dataset, inImageId, result);
                var data = {
                    "anno": result.anno
                }
                $.ajax({
                        url: "/annotator-supreme/image/anno/" + output_dataset + "/" + outImageId,
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



    Dataset.ApplyTransformation = function(dataset) {
        function get_edit_url(transformation) {
            if (transformation == "aspect_ratio_43") {
                url = "/image/edit/ratio"
                param = "aspect_ratio=4:3"
            }
            else if (transformation == "rotate_cw") {
                url = "/image/edit/rotate"
                param = "orientation=cw"
            }
            else if (transformation == "rotate_ccw") {
                url = "/image/edit/rotate"
                param = "orientation=ccw"
            }
            else if (transformation == "flip_h") {
                url = "/image/edit/flip"
                param = "direction=h"
            }
            else if (transformation == "flip_v") {
                url = "/image/edit/flip"
                param = "direction=v"
            }

            return {
                "url": url,
                "param": param
            }

        }
        var trans = $("#transform-dataset-transformation").val();
            url_opts = get_edit_url(trans),
            self = this;
            
        $.ajax({
            url: "/annotator-supreme/image/"+dataset+"/all",
            type: 'GET',
            success: function(data) {
                console.log("Cool, ok!",data);
                var images = data.images;

                self.transformImagesLoop(0, images, dataset, url_opts);
            },
            error: function() {
                console.log("yaks, could not get image list");
                global.Main.disableLoading();
            }
        });    
    }


    Dataset.transformImagesLoop = function (i, images, dataset, options) {
        var self = this;
        $.ajax({
            url: "/annotator-supreme" + options.url + "/" + dataset + "/" + images[i].phash + "?" + options.param,
            type: 'GET',
            success: function(data) {
                if (i+1 < images.length) {
                    self.transformImagesLoop(i+1, images, dataset, options);
                }
                else {
                    console.log("Done.");
                    global.Main.disableLoading();    
                }
            },
            error: function() {
                console.log("yaks, could not get image list");
                global.Main.disableLoading();
            }
        });    
    }

    

    global.Dataset = Dataset;
    global.Dataset.init();

}(window, jQuery));