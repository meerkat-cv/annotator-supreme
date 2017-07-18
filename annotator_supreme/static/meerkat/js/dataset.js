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