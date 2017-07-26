(function (global, $) {

    var Dataset = {},
        dataset_add_btn = $('#add-dataset-btn'),
        purge_btns = $(".bomb-btn"),
        confirm_delete_btn = $("#confirm-delete-button"),
        add_dataset_btn = $("#add-dataset-btn"),
        save_dataset_btn = $("#save-changes-btn");

    Dataset.init = function () {
        this.bindButtons();
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

        $("#supreme-url").val("http://mserver:4248");
        $("#export-dataset-btn").click(function() {
            global.Main.enableLoading("Exporting all...");
            self.checkIfDatasetExist(self.sendImages);
        });
    }


    Dataset.checkIfDatasetExist = function(callback) {
        $.ajax({
            url: $("#supreme-url").val()+"/dataset/"+$("#dataset-sel-export").val(),
            type: 'GET',
            success: function(data) {
                // if exists, for now, dont accept
                console.log("Dataset already exists, cancelled.");
                global.Main.disableLoading();
            },
            error: function() {
                console.log("not");
            }
        });
    }

    Dataset.sendImages = function () {
        $.ajall_imagesax({
            url: "http://localhost/annotator-supreme/image/"+$("#dataset-sel-export").val()+"/all",
            type: 'GET',
            success: function(data) {
                console.log("Cool, ok!",data);
                var images = data.images;

                for (var i = 0; i < images.length; ++i) {
                    var img_url = "http://localhost/annotator-supreme/image/"+images[i].url;
                    self.toDataURL(i, img_url, function(i, base64_img) {
                        console.log("image cat", i);

                        var data = {
                            "category": images[i].category,
                            "name": images[i].name,
                            "imageB64": base64_img.replace("data:image/jpg;base64,", "")
                        };

                        $.ajax({
                                url: $("#supreme-url").val()+"/image",
                                type: 'POST',
                                contentType: 'application/json',
                                data: JSON.stringify(data),
                            success: function(result) {
                                console.log("Done!");
                                window.location.reload();
                            }
                        });
                        console.log("data", data);
                    });

                    
                }

                global.Main.disableLoading();
            },
            error: function() {
                console.log("yaks, could not get image list");
                global.Main.disableLoading();
            }
        });
    }


    Dataset.toDataURL = function(i, url, callback) {
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