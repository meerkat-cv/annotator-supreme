(function (global, $) {

    var Dataset = {},
        dataset_add_btn = $('#add-dataset-btn'),
        purge_btns = $(".bomb-btn"),
        confirm_delete_btn = $("#confirm-delete-button");

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

    }

    Dataset.purgeDataset = function(dataset) {
        // make the request to remove dataset and associated images
        console.log("will remove dataset", dataset)
        $.ajax({
            url: '/annotator-supreme/dataset/'+dataset,
            type: 'DELETE',
            success: function(result) {
                console.log("Done!");
                window.location.reload();
            }
        });
    }

    global.Dataset = Dataset;
    global.Dataset.init();

}(window, jQuery));