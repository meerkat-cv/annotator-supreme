(function (global, $) {

    var UploadVideo = {},
        dataset_sel = $('#dataset-sel'),
        category_entry = $('#category-entry'),
        clear_btn = $("#clear-files-btn");

    UploadVideo.init = function () {
        this.EXTRACT_FRAME_STEP = 50;
        this.initDropZone();
        this.initSlider();
        this.bind();
    };

    UploadVideo.initSlider = function () {
        var self = this;
        this.slider = new Slider('#stepSlider', {
            formatter: function (value) {
                return 'Extract images at each ' + value + ' frames.';
            }
        }).on('slide', function (value) {
            self.EXTRACT_FRAME_STEP = parseInt(value, 10);
        });
    } 

    UploadVideo.showErrorAlert = function() {
        $('#warning-alert').removeClass('hidden');
    };


    UploadVideo.showSuccessAlert = function() {
        $('#success-alert').removeClass('hidden');
    };

    UploadVideo.initDropZone = function() {
        var self = this;
        this.complete_send = false;

        Dropzone.autoDiscover = false;
        var myDropzone = new Dropzone("#my-awesome-dropzone", { 
            url: '/annotator-supreme/video/front-upload',
            autoProcessQueue: false,
            parallelUploads: 10000,

            init: function () {
                var myDropzone = this; // closure

                this.on("drop", function(event) {
                    if (self.complete_send) {
                        $('#input_label4all').val('');
                        self.myDropzone.removeAllFiles(true);  
                        self.complete_send = false;
                    }
                });

                this.on("processing", function(file) {
                    self.enableExtractLoading();
                    // this.options.url = "/annotator-supreme/image/"+self.dataset+"/add";
                });
                this.on("success", function(file, response) {
                    var frames = response.frames_b64;
                    for (var i = 0; i < frames.length; ++i) {
                        self.addExtractedFrame("data:image/jpg;base64,"+frames[i]);
                    }
                }),
                this.on("complete", function() {
                    if (this.getUploadingFiles().length === 0 && this.getQueuedFiles().length === 0) {
                        self.disableLoading();
                    }
                })
                this.on(
                    "addedfile", function(file) {
                      // file._inputElement = Dropzone.createElement("<input name='label_"+file.name+"' type='text' class='image_label' placeholder='Label'>");

                      // hack to remove progress of the files
                      $(".dz-progress").remove();
                      $('#clear-files-btn').prop('disabled', false);
                      $('#input_label4all').prop('disabled', false);
                });
                this.on(
                    "sending", function(file, xhr, formData){
                        formData.append('step_frame', self.EXTRACT_FRAME_STEP);
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

    UploadVideo.getCategory = function() {
        var v = category_entry.val();
        if (v && v != "") {
            return v;
        }
        return "default";
    }


    UploadVideo.addExtractedFrame = function (imageb64) {
        var frame_html = 
        '<li>'+
            '<div class="frame-thumb">'+
              '<img src="'+ imageb64 +'">'+
              '<a href="#" class="del-frame">'+
                '<i class="fa fa-fw fa-times-circle"></i>'+
              '</a>'+
              '<div class="success-frame hidden"><i class="fa fa-fw fa-check-circle"></div>'+
            '</div>'+
        '</li>';

        $('#frames-ul').prepend(frame_html);
        this.bindRemoveFrame();
    } 

    UploadVideo.bindRemoveFrame = function() {
        $('.del-frame').click(function(event){
            event.preventDefault();
            $(this).closest('li').remove();
        })
    }

    UploadVideo.enableSubmitLoading = function () {
        $('#loading-msg').html('Submitting frames...');
        $('#modal-loading').modal('show');
    }

    UploadVideo.enableExtractLoading = function () {
        $('#loading-msg').html('Extracting frames...');
        $('#modal-loading').modal('show');
    }

    UploadVideo.disableLoading = function () {
        $('#modal-loading').modal('hide');        
    }

    UploadVideo.bind = function (){
        var self = this;

        $(document).ready(function () {
            self.dataset = dataset_sel.val();
            console.log('dataset on load', self.dataset);
        })

        dataset_sel.on("change", function () {
            self.dataset = this.value;
        });

        clear_btn.click( function () {
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

        $("#add-submit-btn").click( function() {
            self.enableSubmitLoading();
            var frames = $('.frame-samples-list li');
            
            self.n_frames = frames.length;
            self.proccessed_frames = 0;
            for (var i = 0; i < frames.length; ++i) {
                frame_image = $(frames[i]).find('img').attr("src");
                base64_img = frame_image.replace("data:image/jpg;base64,", "")
                data = {
                    "imageB64": base64_img,
                    "category": $("#category-entry").val()
                }
                $.ajax(
                        {
                            type: "POST",
                            url: "/annotator-supreme/image/"+self.dataset+"/add",
                            dataType: "json",
                            contentType: 'application/json',
                            data: JSON.stringify(data),
                            indexI: i
                        }
                    )
                    .done(function() {
                        $(frames[this.indexI]).find('.del-frame').addClass('hidden');
                        $(frames[this.indexI]).find('.success-frame').removeClass('hidden');
                        console.log("success!");
                    })
                    .fail(function() {
                        $(frames[this.indexI]).find('.del-frame').addClass('hidden');
                        console.log("fail!");
                    })
                    .always(function() {
                        self.proccessed_frames = self.proccessed_frames + 1;
                        if (self.proccessed_frames >= self.n_frames)
                            self.disableLoading();
                    });
            }
        });
            
    };

    global.UploadVideo = UploadVideo;
    global.UploadVideo.init();

}(window, jQuery));