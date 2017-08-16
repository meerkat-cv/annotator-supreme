(function (global, $) {
    var ImageProcessing = {},
        imgproc_div1 = $('#image-proc-container1'),
        imgproc_div2 = $('#image-proc-container2'),
        dataset_sel = $("#dataset-sel"),
        image_sel = $("#image-sel"),
        plugin_sel = $("#plugin-sel"),
        curr_page = 0,
        curr_image_id = '', // Keeping the "previous" image so that we can save their annotations when the image is changed
        anchorRadius = 6;

    ImageProcessing.init = function () {
        var self = this;
        this.bindSelectors();

        // bind apply plugin buttons
        $('#apply-image-plugin-btn').click(function () {
            console.log('apply-image-plugin-btn');
            self.applyPluginOnImage();
        });

        $('#apply-dataset-plugin-btn').click(function () {
            self.applyPluginOnDataset();
        });

        // Populate the default selected dataset
        self.dataset = $('#dataset-sel').find(":selected").text().trim();
        self.getDatasetImages(self);

        $.get( "/annotator-supreme/plugins/all", function( data ) {
            for (var i = 0; i < data.plugins.length; ++i) {
                var option = new Option(data.plugins[i], data.plugins[i]);
                plugin_sel.append($(option));
            }
            self.plugin = data.plugins[0];
            plugin_sel.val(self.plugin).change();
        });

    }

    ImageProcessing.bindSelectors = function() {
        var self = this;
        dataset_sel.on("change", function() {
            self.dataset = this.value;
            self.getDatasetImages(self);
            $(this).blur();
        })

        image_sel.on("change", function() {
            var image = new Image();
            var option_value = this.value;
            $("#img1").attr('src', '/annotator-supreme/image/'+self.image_list[this.value].url);
            $(this).blur();
        });

        plugin_sel.on("change", function() {
            console.log('pluging changing', this.value);
            self.plugin = this.value;
            $(this).blur();
        })
    }


    ImageProcessing.getDatasetImages = function(self) {
        // populate the list of images
        $.get( "/annotator-supreme/image/"+self.dataset+"/all", function( data ) {
            self.image_list = self.imagesToDict(data.images);
            for (var i = 0; i < data.images.length; ++i) {
                var option = new Option(data.images[i].phash, data.images[i].phash);
                image_sel.append($(option));
            }
            // Set the curr image id
            curr_image_id = data.images[0].phash;
            image_sel.val(curr_image_id).change();
        });
    }

    ImageProcessing.imagesToDict = function(image_list) {
        // this function transform a list of images to a dict where
        // the key is the perceptual hash, should be easy to work with
        d = {}
        for (var i = 0; i < image_list.length; ++i) {
            d[image_list[i].phash] = image_list[i];
        }

        return d;
    }

    ImageProcessing.applyPluginOnImage = function() {
        var self = this;

        $.get("/annotator-supreme/plugins/process/"+self.image_list[curr_image_id].url+'?plugin='+self.plugin, function( data ) {
            $('#img2').attr('src', 'data:image/png;base64,'+data.image);
        });
    }

    ImageProcessing.applyPluginOnDataset = function() {
        var self = this,
            partition = $("input[name='options-partition']:checked").val();

        if (partition == "all") {
            $.get("/annotator-supreme/plugins/process/"+self.dataset+'?plugin='+self.plugin);
        }
        else if (partition == "training" || partition == "testing") {
            $.get("/annotator-supreme/plugins/process/partition/"+self.dataset+'/'+partition+'?plugin='+self.plugin);
        }
    }


    global.ImageProcessing = ImageProcessing;
    global.ImageProcessing.init();

}(window, jQuery));
