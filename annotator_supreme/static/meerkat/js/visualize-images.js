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
    }

    VisualizeImages.bindExpand = function () {
        //bind click events
        $cell.find('.image--basic').click(function() {
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
                url: '/annotator-supreme/image/'+self.dataset+'/'+img_id,
                type: 'DELETE',
                success: function(result) {
                    elem.parent().hide(500);
                }
            });
        });
    }


    global.VisualizeImages = VisualizeImages;
    global.VisualizeImages.init();

}(window, jQuery));