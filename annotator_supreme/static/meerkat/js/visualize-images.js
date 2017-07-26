(function (global, $) {

    var VisualizeImages = {},
        $cell = $('.image__cell');

    VisualizeImages.init = function () {
        this.bindRemove();
        this.bindExpand();
    }

    VisualizeImages.setDataset = function(dataset) {
        console.log(dataset);
        this.dataset = dataset;
        var self = this;
        $(document).ready(function() {
            self.assignCategoryColors();
        });
    }

    VisualizeImages.bindExpand = function () {
        //bind click events
        $cell.find('.image--basic').click(function(e) {
            e.preventDefault();
          var $thisCell = $(this).closest('.image__cell');
          
          if ($thisCell.hasClass('is-collapsed')) {
            $cell.not($thisCell).removeClass('is-expanded').addClass('is-collapsed');
            $thisCell.removeClass('is-collapsed').addClass('is-expanded');
          } else {
            $thisCell.removeClass('is-expanded').addClass('is-collapsed');
          }
        });

        $cell.find('.expand__close').click(function(){
          
          var $thisCell = $(this).closest('.image__cell');
          
          $thisCell.removeClass('is-expanded').addClass('is-collapsed');
        });
    }

    VisualizeImages.bindRemove = function () {
        var self = this;
        $cell.find('.remove-img').click(function (event) {
            event.preventDefault();
            var img_id = $(this).data('id');
            var elem = $(this);
            $.ajax({
                url: '/annotator-supreme/image/'+self.dataset.name+'/'+img_id,
                type: 'DELETE',
                success: function(result) {
                    elem.parent().hide(500);
                }
            });
        });
    }

    VisualizeImages.assignCategoryColors = function () {

        function hexToRgb(hex) {
            var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            } : null;
        }


        var category_tags = $(".category-img")
        for (var i = 0; i < category_tags.length; ++i) {
            var ind_color = this.dataset.image_categories.indexOf($(category_tags[i]).html());
            if (ind_color >= 0) {
                var color = this.dataset.category_colors[ind_color];
                $(category_tags[i]).css('background-color', color);

                // maybe I should change from black to white color the font:
                rgbcolor = hexToRgb(color);
                if ((rgbcolor.r*0.299 + rgbcolor.g*0.587 + rgbcolor.b*0.114) > 186)
                    $(category_tags[i]).css('color', 'black');
                else
                    $(category_tags[i]).css('color', 'white');
                    

            }
        }
    }


    global.VisualizeImages = VisualizeImages;
    global.VisualizeImages.init();

}(window, jQuery));