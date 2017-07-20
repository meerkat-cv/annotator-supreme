(function (global, $) {
    var Annotator = {},
        anno_div = $('#konva-container'),
        dataset_sel = $("#dataset-sel"),
        image_sel = $("#image-sel"),
        curr_page = 0,
        curr_image_id = '', // Keeping the "previous" image so that we can save their annotations when the image is changed
        anchorRadius = 6;

    Annotator.init = function () {
        this.sel_labels = [];
        this.bboxes = [];
        this.color_pallete = {};

        this.bind();
        
        // Populate the default selected dataset
        this.dataset = $('#dataset-sel').find(":selected").text().trim();
        
        if (global.location.search.search("dataset=") == -1 && global.location.search.search("image=") == -1) {
            this.getDatasetImages(function() {
                image_sel.trigger("change");
            });    
        }
    }

    Annotator.selectDatasetImage = function(dataset, image) {
        var self = this;
        if (dataset !== "" && image !== "") {
            console.log('Trying to change to ',dataset, image);
            dataset_sel.val(dataset);
            this.getDatasetImages(function() {
                self.selectImage(image);    
            });
            
        }
        
    }

    Annotator.textColorFromBackgroundColor = function(background_color) {
        function hexToRgb(hex) {
            var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            } : null;
        }

        rgbcolor = hexToRgb(background_color);
        if ((rgbcolor.r*0.299 + rgbcolor.g*0.587 + rgbcolor.b*0.114) > 186)
            return 'black'
        else
            return 'white';

    }

    Annotator.computeColorPallete = function(dataset_list) {
        console.log("dataset_list", dataset_list);
        this.color_pallete = {}
        css_rules = ""
        for (var i = 0; i < dataset_list.length; ++i) {
            console.log("dataset_list")
            this.color_pallete[dataset_list[i].name] = {}

            for (var j = 0; j < dataset_list[i].image_categories.length; ++j) {
                var cat = dataset_list[i].image_categories[j].toLowerCase(),
                    bck_color = dataset_list[i].category_colors[j],
                    txt_color = this.textColorFromBackgroundColor(bck_color);
                css_rules = css_rules +"\
                .label-"+dataset_list[i].name.toLowerCase()+"-"+cat+" {\
                    background-color: "+bck_color+" !important;\
                    color: "+txt_color+" !important;\
                }"

                // also add to color pallete
                this.color_pallete[dataset_list[i].name][cat] = {
                    "background": bck_color,
                    "text": txt_color
                };
            }
        }
        console.log("css_rules", css_rules);
        // add rules to labels
        $("<style>")
            .prop("type", "text/css")
            .html(css_rules)
            .appendTo("head");
    }

    Annotator.bind = function () {
        this.bindSelectors();
        this.bindKeyEvents();
        this.bindCategoryCheckbox();
        this.bindLabelInput();
    }

    Annotator.bindLabelInput = function() {
        $("#labelInput").tagsinput({
            tagClass: function(item) {
                return "label label-default label-"+dataset_sel.val().toLowerCase()+"-"+item.toLowerCase();
            }
        })
    }

    Annotator.bindCategoryCheckbox = function() {
        $("#use-categories-chk").change(function () {
            if ($(this).is(":checked")) {
                $(".bootstrap-tagsinput").addClass("disabled");
            }
            else {
                $(".bootstrap-tagsinput").removeClass("disabled");
            }
        });

        $("#use-categories-chk").prop('checked', true);
        $(".bootstrap-tagsinput").addClass("disabled");
    }

    Annotator.bindSelectors = function() {
        var self = this;
        dataset_sel.on("change", function() {
            console.log("datasetl change")
            self.dataset = this.value;
            self.getDatasetImages();
            $(this).blur();
        })

        image_sel.on("change", function() {
            // first thing here is to save the annotations of the previous guy
            var previous_img = $(this).data("previous") || "";
            if (previous_img != "") {
                var anno_data = self.getCanvasAnnotationData(),
                    elem = $(this);
                self.saveAnnotation(dataset_sel.val(), previous_img, anno_data, function () {
                    self.setImageTag(elem);
                });
            }
            else {
                self.setImageTag(this);    
            }
        });

        $("#img-to-anno").on("load", function() {
            console.log("image load");
            // self.saveAnnotation(dataset_sel)
            self.setStage();
            self.getStoredAnnotations();
            self.getDetails();
            
        });
    }

    Annotator.setImageTag = function(elem) {
        $("#annotation-title").html("Annotating <b>"+image_sel.val()+"</b> from <b>"+dataset_sel.val()+"</b>");
        $("#img-to-anno").attr("src", '/annotator-supreme/image/'+dataset_sel.val()+"/"+$(elem).val());
        $(elem).data("previous", $(elem).val());
        $(elem).blur();
    }


    Annotator.getDetails = function() {
        var self = this;
        // also make a request to get the details of the image
        $.ajax({
            type: 'get',
            url: "/annotator-supreme/image/details/"+dataset_sel.val()+"/"+image_sel.val(),
            error: function (jqXHR, textStatus, errorThrown) {
                console.log("error"+jqXHR.responseText);
            },
            success: function (data) {
                if ($("#use-categories-chk").is(":checked")) {
                    self.setLabelsInInput([data.image.category]);
                }
            }
        });
    }

    Annotator.setLabelsInInput = function(labels) {
        $("#labelInput").tagsinput('removeAll');
        for (var i = 0; i < labels.length; ++i) {
            $("#labelInput").tagsinput('add', labels[i]);
        }
    }


    Annotator.saveAnnotation = function(dataset, image_id, anno_data, callback) {
        console.log("saveAnnotation");
        // Update Konva stage after the annotations are saved, otherwise
        // they will be destroyed
        $.ajax({
            type: 'post',
            url: "/annotator-supreme/image/anno/"+dataset+"/"+image_id,
            data: JSON.stringify(anno_data),
            contentType: 'application/json',
            error: function (jqXHR, textStatus, errorThrown) {
                console.log("error saveAnnotation:",(jqXHR.responseText));
            },
            complete: function () {
                console.log("calling callback!");
                if (callback) {
                    callback();
                }
            }
        });
    }


    Annotator.getStoredAnnotations = function() {
        console.log("getting stored annotations for",image_sel.val());
        var self = this;
        $.get( "/annotator-supreme/image/anno/"+dataset_sel.val()+"/"+image_sel.val(), function( data ) {
            self.bboxes = [];
            for (var i=0; i<data.anno.length; ++i) {
                self.createCompleteBBox(data.anno[i].left, 
                                        data.anno[i].top, 
                                        data.anno[i].right, 
                                        data.anno[i].bottom, 
                                        data.anno[i].labels, 
                                        data.anno[i].ignore,
                                        self.scale);
            }
        });
    }


    Annotator.getCanvasAnnotationData = function() {
        var d = { 'anno': []};
        var default_label = '';
        for (var i=0; i<this.bboxes.length; i++) {
            if (this.bboxes[i].children.length <= 0) {
                continue;
            }
            var tag = this.bboxes[i].findOne('#tag');
            if (tag == null) {
                continue;
            } else if (tag == 'ignore') {
                continue;
            }
            default_label = tag.attrs.text;
        }

        for (var i=0; i<this.bboxes.length; i++) {
            if (this.bboxes[i].children.length <= 0) {
                console.log('SKIPING');
                continue;
            }

            var curr_anno = {};
            var tag = this.bboxes[i].findOne('#tag');
            curr_anno['left'] = this.bboxes[i].attrs.x;
            curr_anno['top'] = this.bboxes[i].attrs.y;
            curr_anno['right'] = curr_anno['left'] + this.bboxes[i].get('Rect')[0].attrs.width;
            curr_anno['bottom'] = curr_anno['top'] + this.bboxes[i].get('Rect')[0].attrs.height;
            curr_anno['ignore'] = this.bboxes[i].attrs.ignore;
            if (tag == null) {
                curr_anno['labels'] = [default_label];
            } else {
                curr_anno['labels'] = [tag.attrs.text];
            }
            d['anno'].push(curr_anno);
        }

        // The images were annotated in scaled version
        d['scale'] = 1.0/this.scale;

        return d;
    }

    Annotator.getDatasetImages = function(callback) {
        var self = this;
        // populate the list of images
        this.image_list = [];
        image_sel.empty();
        $.get( "/annotator-supreme/image/" + dataset_sel.val() + "/all", function( data ) {
            self.image_list = self.imagesToDict(data.images);
            for (var i = 0; i < data.images.length; ++i) {
                var option = new Option(data.images[i].phash, data.images[i].phash);
                image_sel.append($(option));
            }

            if (callback) {
                callback();
            }

            
            // Set the curr image id
            // curr_image_id = data.images[0].phash;
            // self.getStoredAnnotations();
            // image_sel.val(curr_image_id).change();
        });
    }

    Annotator.selectImage = function(selected_image) {
        // MAKE sure that the image is in the options
        if (selected_image) {
            image_sel.val(selected_image).trigger("change");
            image_sel.data("previous", image_sel.val());
        }
    }
    



    Annotator.imagesToDict = function(image_list) {
        // this function transform a list of images to a dict where
        // the key is the perceptual hash, should be easy to work with
        d = {}
        for (var i = 0; i < image_list.length; ++i) {
            d[image_list[i].phash] = image_list[i];
        }

        return d;
    }

    Annotator.bindKeyEvents = function() {
        var self = this;
        $(document).keydown(function (e) {
            if (e.keyCode == 37 || e.keyCode == 40) { // Left or Down
                console.log("down");
                var curr_index = $('#image-sel').prop("selectedIndex");
                    prev_value = $($('#image-sel option')[curr_index-1]).val();

                if (prev_value) {
                    image_sel.val(prev_value).trigger("change");
                }
            } 
            else if (e.keyCode == 39 || e.keyCode == 38) { // Right or Up
                console.log("up");
                var curr_index = $('#image-sel').prop("selectedIndex");
                    next_value = $($('#image-sel option')[curr_index+1]).val();

                if (next_value) {
                    image_sel.val(next_value).trigger("change");
                }
            } 
            else {
                // console.log('key code ', e.keyCode);
                return;
            }
        });
    }

    Annotator.setStage = function() {
        console.log("setting stage");
        // create the konva stage
        var self = this,
            width = $("#img-to-anno").width(),
            height =$("#img-to-anno").height();
        
        this.scale = width/$("#img-to-anno")[0].naturalWidth
        if (typeof this.stage != 'undefined')
            this.stage.destroy();
        this.stage = new Konva.Stage({
            container: 'konva-container',
            width: width,
            height: height
        });

        this.annoLayer = new Konva.Layer();
        this.stage.add(this.annoLayer);


        // could load from somewhere
        this.annoLayer.draw();

        // set the mouse events
        var creatingBBox = false;
        this.overButton = false;
        this.overBBox = false;
        this.stage.on('contentMousedown.proto', function() {
            console.log('mouse down');
            var currPoint = self.stage.getPointerPosition();
            if (!creatingBBox && !self.overButton && !self.overBBox) {
                creatingBBox = true;
                startPoint = self.stage.getPointerPosition();
                self.createBBox(startPoint);
            }
        });

        this.stage.on('contentMousemove.proto', function() {
            if (creatingBBox) {
                var currPoint = self.stage.getPointerPosition();
                self.updateBBoxWhileCreating(self.currentBBox, currPoint);
            }
        });

        this.stage.on('contentMouseup.proto', function() {
            if (creatingBBox) {
                // now, the bbox was officially created
                self.bboxes.push(self.currentBBox);
                self.finishBBoxCreation(self.currentBBox, self.getCurrentLabels());
                creatingBBox = false;
            }

        });

        console.log("setting ready");

    }

    Annotator.getCurrentLabels = function() {
        // the current labels are always those in the tags input
        return $("#labelInput").tagsinput("items");
    }

    Annotator.createBBox = function(startPoint) {
        var self = this;
        var rect = new Konva.Rect({
            width: 1,
            height: 1,
            stroke: 'red',
            strokeWidth: 3
        });
        var rectGroup = new Konva.Group({
            x: startPoint.x,
            y: startPoint.y,
            draggable: true,
            ignore: false
        });


        // add a rect to a group and group to layer
        rectGroup.add(rect);
        this.annoLayer.add(rectGroup);
        this.currentBBox = rectGroup;
    }

    Annotator.createCompleteBBox = function(l, t, r, b, labels, ignore, scale) {
        var self = this;

        if (scale && scale != 1.0) {
            l = l*scale;
            r = r*scale;
            t = t*scale;
            b = b*scale;
        }

        var rect = new Konva.Rect({
            width: (r-l),
            height: (b-t),
            stroke: 'red',
            strokeWidth: 3
        });
        var rectGroup = new Konva.Group({
            x: l,
            y: t,
            draggable: true,
            ignore: false
        });


        // add a rect to a group and group to layer
        rectGroup.add(rect);
        this.annoLayer.add(rectGroup);
        this.finishBBoxCreation(rectGroup, labels);
        // console.log(rectGroup.find('#ignoreButtonText'));
        if (ignore) {
            console.log('Activating ignore');
            rectGroup.find('#ignoreButtonText').fire('mousedown');
        }
        this.bboxes.push(rectGroup);
    }

    Annotator.updateBBoxWhileCreating = function(group, newBottomRight) {
        var topLeftX = group.getX(),
            topLeftY = group.getY();

        var width = newBottomRight.x - topLeftX;
        var height = newBottomRight.y - topLeftY;

        var rect = group.get('Rect')[0];
        if(width && height) {
            rect.width(width);
            rect.height(height);
        }

        this.annoLayer.draw();
    }



    Annotator.getBBoxTopLeft = function(group) {
        var topLeft = {
            x: group.getX(),
            y: group.getY()
        }

        return topLeft;
    }

    Annotator.getBBoxTopRight = function(group) {
        var rect = group.get('Rect')[0];
        var topRight = {
            x: group.getX() + rect.width(),
            y: group.getY()
        }

        return topRight;
    }


    Annotator.getBBoxBottomLeft = function(group) {
        var rect = group.get('Rect')[0];
        var bottomLeft = {
            x: group.getX(),
            y: group.getY() + rect.height()
        }

        return bottomLeft;
    }

    Annotator.getBBoxBottomRight = function(group) {
        var rect = group.get('Rect')[0];
        var BottomRight = {
            x: group.getX() + rect.width(),
            y: group.getY() + rect.height()
        }

        return BottomRight;
    }

    Annotator.finishBBoxCreation = function(group, labels=[]) {
        var rect = group.get('Rect')[0],
            self = this;

        if (rect.width() < 10 && rect.height() < 10) {
            // it the bbox is too small I am assuming an accidental clicl
            group.destroy();
            this.annoLayer.draw();
        }
        else {
            this.addBBoxAnchors(group);
            this.addIconBar(group);
            this.addLabelGroup(group, labels);

            group.on('mouseover', function() {
                var rect = group.get('Rect')[0],
                    is_ignore = group.attrs.ignore;
                if (!is_ignore) {
                    rect.fill('rgba(200,0,0,0.2)');
                }
                self.showAnchorAndIcons(group);
                self.annoLayer.draw();
                self.overBBox = true;
            });

            group.on('mouseout', function() {
                console.log('MouseOut');
                var rect = group.get('Rect')[0],
                    is_ignore = group.attrs.ignore;
                if (!is_ignore) {
                    rect.fill(null);
                }
                self.hideAnchorAndIcons(group);
                self.annoLayer.draw();
                self.overBBox = false;
            });

            this.annoLayer.draw();
        }
    }


    Annotator.showAnchorAndIcons = function(group) {
        group.get('Circle').visible(true);
        group.get('#iconBar').visible(true);
    }

    Annotator.hideAnchorAndIcons = function(group) {
        // group.get('Circle').visible(false);
        // group.get('#iconBar').visible(false);
    }



    Annotator.addBBoxAnchors = function(group) {
        var rect = group.get('Rect')[0];

        this.addAnchor(group, {x: 0, y: 0}, 'topLeft');
        this.addAnchor(group, {x: rect.width(), y: 0}, 'topRight');
        this.addAnchor(group, {x: 0, y: rect.height()}, 'bottomLeft');
        this.addAnchor(group, {x: rect.width(), y: rect.height()}, 'bottomRight');

        this.annoLayer.draw();
    }



    Annotator.addAnchor = function(group, point, name) {
        var self = this;
        var x = point.x,
            y = point.y;
        var anchor = new Konva.Circle({
            x: x,
            y: y,
            stroke: '#666',
            fill: '#ddd',
            strokeWidth: 1,
            radius: anchorRadius,
            name: name,
            draggable: true,
            dragOnTop: false,
            visible: true
        });

        anchor.on('dragmove', function() {
            self.updateUsingAnchor(this);
        });
        anchor.on('mousedown touchstart', function() {
            group.setDraggable(false);
            this.moveToTop();
        });
        anchor.on('dragend', function() {
            group.setDraggable(true);
        });
        // add hover styling
        anchor.on('mouseover', function() {
            var layer = this.getLayer();
            document.body.style.cursor = 'pointer';
            this.overButton = true;
            console.log("over anchor");
            this.setStrokeWidth(4);
        });
        anchor.on('mouseout', function() {
            var layer = this.getLayer();
            document.body.style.cursor = 'default';
            this.overButton = false;
            console.log("NOT over anchor");
            this.setStrokeWidth(2);
        });
        group.add(anchor);
    }

    Annotator.updateUsingAnchor = function(activeAnchor) {
        var group       = activeAnchor.getParent();
        var topLeft     = group.get('.topLeft')[0];
        var topRight    = group.get('.topRight')[0];
        var bottomRight = group.get('.bottomRight')[0];
        var bottomLeft  = group.get('.bottomLeft')[0];
        var rect        = group.get('Rect')[0];
        var anchorX     = activeAnchor.getX();
        var anchorY     = activeAnchor.getY();
        // update anchor positions
        switch (activeAnchor.getName()) {
            case 'topLeft':
                console.log('topLeft before setting');
                console.log(topRight.getY());
                topRight.setY(anchorY);
                bottomLeft.setX(anchorX);
                break;
            case 'topRight':
                topLeft.setY(anchorY);
                bottomRight.setX(anchorX);
                break;
            case 'bottomRight':
                bottomLeft.setY(anchorY);
                topRight.setX(anchorX);
                break;
            case 'bottomLeft':
                bottomRight.setY(anchorY);
                topLeft.setX(anchorX);
                break;
        }

        rect.position(topLeft.position());

        // should also move all icons
        var icons = group.get('Text'),
            labels = group.get('Label');

        this.repositionIcons(group, topLeft.position())
        this.repositionLabels(group, topLeft.position())

        var width = topRight.getX() - topLeft.getX();
        var height = bottomLeft.getY() - topLeft.getY();
        if(width && height) {
            rect.width(width);
            rect.height(height);
        }
    }

    Annotator.repositionIcons = function(group, topLeft) {
        var icon_bar = group.find("#iconBar");
        var new_pos = {
            x: topLeft.x + 10,
            y: topLeft.y + 10
        };

        icon_bar.position(new_pos);
    }

    Annotator.repositionLabels = function(group, topLeft) {
        var label_bar = group.find("#labelBar");
        var new_pos = {
            x: topLeft.x,
            y: topLeft.y - 20
        };
        label_bar.position(new_pos);
    }

    Annotator.isPointInsideAnyBbox = function(point) {
        var isInside = false;
        for (var i = 0; i < this.bboxes.length; ++i) {
            if (this.isPointInsideBbox(this.bboxes[i], point)) {
                isInside = true;
                break;
            }
        }

        return isInside;
    }

    Annotator.isPointInsideBbox = function(bbox, point) {
        var topLeft = this.getBBoxTopLeft(bbox),
            bottomRight = this.getBBoxBottomRight(bbox);

        if (point.x >= topLeft.x && point.y >= topLeft.y &&
                point.x <= bottomRight.x && point.y <= bottomRight.y)
            return true;

        return false;
    }

    Annotator.addIconBar = function(group) {
        var iconsGroup = new Konva.Group({
            x: 10,
            y: 10,
            id: 'iconBar',
            visible: true
        });

        this.addRemoveButton(iconsGroup);
        this.addIgnoreButton(iconsGroup);
        this.addAddLabelButton(iconsGroup);

        group.add(iconsGroup);
    }

    Annotator.addRemoveButton = function(iconGroup) {
        var self = this;
        var removeButtonText = new Konva.Text({
          x: 0,
          y: 0,
          text: "\uf014",
          fontSize: 18,
          fontFamily: 'FontAwesome',
          fill: 'white'
        });

        removeButtonText.on('mouseover', function() {
            document.body.style.cursor = 'pointer';
            this.setFontSize(20);
            self.annoLayer.draw();
            self.overButton = true;
        });
        removeButtonText.on('mouseout', function() {
            document.body.style.cursor = 'default';
            this.setFontSize(18);
            self.annoLayer.draw();
            self.overButton = false;
        });

        removeButtonText.on('mousedown', function() {
            // should destroy the whole bbox
            iconGroup.getParent().destroy();
            console.log('iconGroup.getParent', iconGroup.getParent());
            self.annoLayer.draw();
        });

        iconGroup.add(removeButtonText);
    }

    Annotator.addIgnoreButton = function(iconGroup) {
        var self = this;
        var ignoreButtonText = new Konva.Text({
          x: 20,
          y: 0,
          text: "\uf05e",
          fontSize: 18,
          fontFamily: 'FontAwesome',
          fill: 'white',
          id: 'ignoreButtonText'
        });

        ignoreButtonText.on('mouseover', function() {
            document.body.style.cursor = 'pointer';
            this.setFontSize(20);
            self.annoLayer.draw();
            self.overButton = true;
        });
        ignoreButtonText.on('mouseout', function() {
            document.body.style.cursor = 'default';
            this.setFontSize(18);
            self.annoLayer.draw();
            self.overButton = false;
        });

        ignoreButtonText.on('mousedown', function() {
            var bbox = iconGroup.getParent();
            var is_ignore = bbox.attrs.ignore;
            if (is_ignore) {
                bbox.attrs.ignore = false;
                var rect = bbox.get('Rect')[0];
                rect.fill(null);
                rect.stroke('red');
                self.clearLabels(bbox);
            }
            else {
                bbox.attrs.ignore = true;
                var rect = bbox.get('Rect')[0];
                rect.fill('rgba(100,100,100,0.5)');
                rect.stroke('rgba(100,100,100,1.0)');
                self.setIgnoreLabel(bbox);
            }
            self.annoLayer.draw();
        });

        iconGroup.add(ignoreButtonText);
    }

    Annotator.addAddLabelButton = function(iconGroup) {
        var self = this;
        var addButtonText = new Konva.Text({
          x: 42,
          y: 0,
          text: "\uf067",
          fontSize: 18,
          fontFamily: 'FontAwesome',
          fill: 'white'
        });

        addButtonText.on('mouseover', function() {
            document.body.style.cursor = 'pointer';
            this.setFontSize(20);
            self.annoLayer.draw();
            self.overButton = true;
        });
        addButtonText.on('mouseout', function() {
            document.body.style.cursor = 'default';
            this.setFontSize(18);
            self.annoLayer.draw();
            self.overButton = false;
        });

        addButtonText.on('mousedown', function() {
            console.log("click add label");
            // iconGroup.destroy();
            self.annoLayer.draw();
        });

        iconGroup.add(addButtonText);
    }


    Annotator.addLabelGroup = function(group, labels=[]) {
        var labelGroup = new Konva.Group({
            x: 0,
            y: -20,
            id: 'labelBar'
        });

        for (var i=0; i<labels.length; ++i) {
            this.addLabel(labelGroup, labels[i], "green");
        }

        group.add(labelGroup);
    }


    Annotator.addLabel = function(group, label, color) {
        var labelsAdded = group.get('Label'),
            offsetX = 10
        for (var i = 0; i < labelsAdded.length; ++i)
            offsetX = offsetX + labelsAdded[i].width() + 10;

        var simpleLabel = new Konva.Label({
            x: offsetX,
            y: 0,
            opacity: 0.85
        });
        simpleLabel.add(new Konva.Tag({
            fill: color
        }));

        simpleLabel.add(new Konva.Text({
            text: label,
            fontFamily: 'Calibri',
            fontSize: 14,
            padding: 3,
            fill: 'white',
            id: 'tag'
        }));

        group.add(simpleLabel);
    }

    Annotator.clearLabels = function(group) {
        group.get('#labelBar').destroyChildren();

    }

    Annotator.setIgnoreLabel = function(group) {
        this.clearLabels(group);
        this.addLabel(group.findOne("#labelBar"), "ignore", "gray");
    }


    global.Annotator = Annotator;
    global.Annotator.init();

}(window, jQuery));
