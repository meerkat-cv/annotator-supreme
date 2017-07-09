// Demo by Dan Rose.
// See: http://www.sitepoint.com/recreating-google-images-search-layout-css

// dynamically create loads of image cells
function cells(count) {
  if (typeof count !== 'number' || count > 99) return false;
  
  var html = '',
      imageNum;
  
  for (i = 0; i < count; i++) {
    imageNum = Math.floor(Math.random() * 9) + 1;
    html += '<article class="image__cell is-collapsed">' +
        '<div class="image--basic">' +
            '<a href="#expand-jump-'+i+'">' +
                '<img id="expand-jump-'+i+'" class="basic__img" src="http://lorempixel.com/250/250/fashion/'+ imageNum +'" alt="Fashion '+ imageNum +'" />' +
          '</a>' +
          '<div class="arrow--up"></div>' +
        '</div>' +
        '<div class="image--expand">' +
            '<a href="#close-jump-'+i+'" class="expand__close"></a>' +
          '<img class="image--large" src="http://lorempixel.com/400/400/fashion/'+ imageNum +'" alt="Fashion '+ imageNum +'" />' +
        '</div>' +
      '</article>';
  }
  return html;
}

//apend cells to grid
// $('.image-grid').empty().html(cells(50));


//bind click events
var $cell = $('.image__cell');

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