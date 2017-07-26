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