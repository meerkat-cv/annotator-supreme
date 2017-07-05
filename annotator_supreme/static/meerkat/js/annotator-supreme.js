(function (global, $) {
    var Annotator = {},
        anno_div = $('#annotation-container'),
        dataset_sel = $("#dataset-sel"),
        image_sel = $("#image-sel"),
        curr_page = 0,
        anchorRadius = 6;

    Annotator.init = function () {
        $('#anno-img').attr('src','/annotator-supreme/static/meerkat/images/heineken.jpg');
        anno_div = $('#annotation-container');
        var image = new Image(),
            self = this;
        image.onload = function() {
            self.setStage(image);
        };
        image.src = "/annotator-supreme/static/meerkat/images/heineken.jpg";
        this.bboxes = [];

        this.bindSelectors();
        this.bindKeyEvents();

        // Populate the default selected dataset
        self.dataset = $('#dataset-sel').find(":selected").text().trim();
        self.getDatasetImages(self);
    }

    Annotator.bindSelectors = function() {
        var self = this;
        dataset_sel.on("change", function() {
            self.dataset = this.value;
            self.getDatasetImages(self);
        })

        image_sel.on("change", function() {
            anno_div = $('#annotation-container');
            var image = new Image();
            image.onload = function() {
                self.setStage(image);
            };
            image.src = '/annotator-supreme/image/'+self.image_list[this.value].url;
        });
    }

    Annotator.getDatasetImages = function(self) {
        // populate the list of images
        $.get( "/annotator-supreme/image/"+self.dataset+"/all", function( data ) {
            self.image_list = self.imagesToDict(data.images);
            for (var i = 0; i < data.images.length; ++i) {
                var option = new Option(data.images[i].phash, data.images[i].phash);
                image_sel.append($(option));
            }

        });
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
        $(document).keydown(function (e) {
            if (e.keyCode == 37 || e.keyCode == 40) { // Left or Down
                if (curr_page <= 0) {
                    console.log('all_imgs', self.all_imgs)
                    curr_page = self.all_imgs.length-1
                } else {curr_page = curr_page-1;
                }
            } else if (e.keyCode == 39 || e.keyCode == 38) { // Right or Up
                if (curr_page >= self.all_imgs.length-1) {
                    curr_page = 0;
                } else {
                    curr_page = curr_page+1;
                }
            } else {
                // console.log('key code ', e.keyCode);
                return;
            }

            console.log('image', self.all_imgs[curr_page].url)
            self.bboxes = []

            $.ajax({
                type: 'get',
                url: '/annotator-supreme/image/'+self.all_imgs[curr_page].url,
                success: function(data) {
                    $('#anno-img').attr('src',data);
                    anno_div = $('#annotation-container');
                    var image = new Image();
                    image.onload = function() {
                        self.setStage(image);
                    };
                    image.src = self.all_imgs[curr_page].url;
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    console.log("error on geting image");
                },
            });
        });

    }

    Annotator.setStage = function(backgroundImage) {
        // create the konva stage
        var self = this;
        var width = backgroundImage.width;
        var height = backgroundImage.height;
        if (typeof this.stage != 'undefined')
            this.stage.destroy();
        this.stage = new Konva.Stage({
            container: 'annotation-container',
            width: width,
            height: height
        });

        this.imgLayer = new Konva.Layer();
        this.stage.add(this.imgLayer);

        var context = this.imgLayer.getContext();
        context.drawImage(backgroundImage, 0, 0);

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


            // lastPointerPosition = stage.getPointerPosition();
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
                self.finishBBoxCreation(self.currentBBox);
                creatingBBox = false;
            }

        });
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
        console.log(rectGroup);

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

    Annotator.finishBBoxCreation = function(group) {
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
            this.addLabelGroup(group);

            group.on('mouseover', function() {
                console.log('MouseOver');
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
          fill: 'white'
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
            console.log("click");

            var bbox = iconGroup.getParent();
            var is_ignore = bbox.attrs.ignore;
            console.log('is_ignore', is_ignore);
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


    Annotator.addLabelGroup = function(group) {
        var labelGroup = new Konva.Group({
            x: 0,
            y: -20,
            id: 'labelBar'
        });

        // this.addLabel(labelGroup, "heineken", "green");
        // this.addLabel(labelGroup, "beer", "orange");
        // this.addLabel(labelGroup, "something", "red");

        group.add(labelGroup);
    }



        // self.enableLoading();
        // var host = "http://"+window.location.host;
        // $.ajax({
        //     type: 'get',
        //     url: '/frapi/recognition/verify/images',
        //     data: {'image1Url': host+self.canvas1.image_url,
        //             'image2Url': host+self.canvas2.image_url},
        //     success: function (response) {
        //         self.showResult(response);
        //     },
        //     error: function (jqXHR, textStatus, errorThrown) {
        //         self.showError(jqXHR.responseText);
        //     },
        //     complete: function() {
        //         self.disableLoading();
        //     }
        // });


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
            fill: 'white'
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
