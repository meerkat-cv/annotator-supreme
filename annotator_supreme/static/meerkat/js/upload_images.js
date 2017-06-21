(function (global, $) {

    var UploadImages = {};

    UploadImages.init = function () {
        this.initDropZone();
        this.bind();
    };

    UploadImages.showErrorAlert = function() {
        $('#warning-alert').removeClass('hidden');
    };


    UploadImages.showSuccessAlert = function() {
        $('#success-alert').removeClass('hidden');
    };

    UploadImages.initDropZone = function() {
        var self = this;
        this.complete_send = false;

        Dropzone.autoDiscover = false;
        var myDropzone = new Dropzone("#my-awesome-dropzone", { 
            url: '/annotator-supreme/upload_images',
            autoProcessQueue: false,
            parallelUploads: 100,

            init: function () {
                var myDropzone = this; // closure

                this.on("drop", function(event) {
                    if (self.complete_send) {
                        $('#input_label4all').val('');
                        self.myDropzone.removeAllFiles(true);  
                        self.complete_send = false;
                    }
                });
                this.on(
                    "addedfile", function(file) {
                      file._inputElement = Dropzone.createElement("<input name='label_"+file.name+"' type='text' class='image_label' placeholder='Label'>");

                      // hack to remove progress of the files
                      $(".dz-progress").remove();
                      $('#clear-files-btn').prop('disabled', false);
                      $('#input_label4all').prop('disabled', false);
                });
                this.on(
                    "sending", function(file, xhr, formData){
                        // pass
                });
                this.on('error', function(file, response) {
                    $(file.previewElement).find('.dz-error-message').text(response['message']);
                    self.n_errors = self.n_errors + 1;
                });
                this.on("queuecomplete", function() {
                    if (self.n_errors > 0) {
                        self.showErrorAlert();
                    }
                    else if (self.n_errors == 0) {
                        self.showSuccessAlert();
                    }
                    self.complete_send = true;
                });
            }
        });

        this.myDropzone = myDropzone;
    };

    UploadImages.bind = function (){
        var self = this;
        $('#input_label4all').on('input', function(e) {
            $('.image_label').val($('#input_label4all').val());
        });

        $('#clear-files-btn').click( function () {
            self.myDropzone.removeAllFiles(true);    
            $('#clear-files-btn').prop('disabled', 'disabled');
            $('#input_label4all').val('');
            $('#input_label4all').prop('disabled', 'disabled');
        });

        $("#upload-submit-btn").click( function() {
            $('#success-alert').addClass('hidden');
            $('#warning-alert').addClass('hidden');
            self.n_errors = 0;
            self.myDropzone.processQueue(); // Tell Dropzone to process all queued files.
            // self.should_clear_all = true;
        });
            
    };

    global.UploadImages = UploadImages;
    global.UploadImages.init();

}(window, jQuery));