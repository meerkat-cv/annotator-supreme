(function (global, $) {

    var AnnotateLabel = {},
        dataset_sel = $('#dataset-sel'),
        category_entry = $('#category-entry'),
        clear_btn = $("#clear-files-btn");

    AnnotateLabel.init = function () {
        this.isMobile = false; //initiate as false
        // device detection
        if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent) 
            || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) this.isMobile = true;

        if (this.isMobile) {
            $("nav").remove();
        }

        this.populateImages();
        this.bindSaveButton();

        
        $('#people-database-next').keyup(function(e){
            console.log("keyyyy")
            if (e.keyCode == 13){  
                $("#people-database-next a").click();
            }
         });
    };


    AnnotateLabel.bindSaveButton = function() {
        var self = this;
        $("#save-btn").click(function() {
            self.saveAll();
        });
    }

    AnnotateLabel.saveAll = function(finish_callback) {
        $("#save-btn").attr("disabled", "disabled");
        $("#save-btn").html('<i class="fa fa-refresh fa-spin"></i>\nSaving...')

        var cards = $("#cards-container .anno-card-clone");
        this.saveLoop(cards, 0, finish_callback);
    }

    AnnotateLabel.saveLoop = function(cards, i, finish_callback) {
        var self = this;
        if (i < cards.length) {
            var base_url = "/annotator-supreme/image/anno/modify/label/" + self.dataset + "/" + $(cards[i]).data('image_id') + "/" + $(cards[i]).data('anno_ith') 
            console.log("base_url: ", base_url);    

            var data = {
                "newLabels": [$(cards[i]).find('.anno-label-input').val()]
            }
            $.ajax({
                url: base_url,
                type: 'POST',
                data: JSON.stringify(data),
                contentType: 'application/json',
                success: function (data) {
                    self.saveLoop(cards, i+1, finish_callback);        
                }
            });
        }
        else {
            $("#save-btn").attr("disabled", false);
            $("#save-btn").html('<i class="fa fa-fw fa-save"></i>\nSave annotations');
            if (finish_callback) {
                finish_callback()
            }
        }
        

    }

    AnnotateLabel.getCardElement = function(annotation) {
        var elem = $("#anno-card").clone();
        elem.attr('id', 'card-'+annotation.image_url.split("/")[1]);
        elem.data('image_id', annotation.image_url.split("/")[1]);
        elem.data('anno_ith', annotation.anno_ith);
        elem.removeClass('hidden');
        elem.addClass('anno-card-clone');

        elem.find('.anno-img').attr('src', '/annotator-supreme/image/cropanno/' + annotation.image_url + '/' + annotation.anno_ith)
        elem.find('.anno-label-input').val(annotation.labels[0])
        return elem;
    }

    AnnotateLabel.populateImages = function () {
        function getParameterByName(name, url) {
            if (!url) url = window.location.href;
            name = name.replace(/[\[\]]/g, "\\$&");
            var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
                results = regex.exec(url);
            if (!results) return null;
            if (!results[2]) return '';
            return decodeURIComponent(results[2].replace(/\+/g, " "));
        }

        this.dataset = getParameterByName("dataset");
        this.pageNumber = getParameterByName("pageNumber") || 1;
        if (this.isMobile) {
            this.itemsPerPage = 1;     
        }
        else {
            this.itemsPerPage = 16;    
        }
        

        var self = this;
        $.ajax({
            url: '/annotator-supreme/image/anno/' + self.dataset + '/all?pageNumber=' + self.pageNumber + '&itemsPerPage=' + self.itemsPerPage,
            type: 'GET',
            success: function (data) {
                console.log("Done!", data);
                // window.location.reload();
                self.pageCount = data.totalPages;
                self.pageNumber = data.pageNumber;
                
                self.addPaginationControllers();

                self.updatePreviousNextPaginationControllers();
                self.bindPagination();


                for (var i = 0; i < data.annotations.length; ++i) {
                    elem = self.getCardElement(data.annotations[i]);    
                    elem.find(".anno-label-input").attr('tabindex', i+1);
                    $("#cards-container").append(elem);
                }

                console.log("#card-"+data.annotations[0].image_url.split("/")[1])

                $(document).ready(function() {
                    $("#card-"+data.annotations[0].image_url.split("/")[1]+" .anno-label-input").focus(); 
                    $("#card-"+data.annotations[0].image_url.split("/")[1]+" .anno-label-input").select();
                    $("#people-database-next").attr('tabindex', self.itemsPerPage+1);
                    if (self.isMobile) {
                        $(".anno-label-input").removeClass("input-sm");
                        $(".anno-label-input").addClass("input-lg");
                    }
                })
                


            }
        });
    };

    AnnotateLabel.addPaginationControllers = function () {
            var page;
            var pageNumber = 0;

            var first = this.pageNumber - 1;
            var last = this.pageNumber + 1;

            $('.people-database-page').remove();
            $('.paginate_button.people-separator').remove();

            if (this.pageCount > 1) {
                if (!this.isMobile) {
                    if (this.pageNumber < 5) {
                        first = 1;
                        last = Math.min(5, this.pageCount);
                    } else if (this.pageCount - this.pageNumber < 5) {
                        first = Math.max(1, this.pageCount - 5);
                        last = this.pageCount;
                    }

                    for (pageNumber = last; pageNumber >= first; pageNumber--) {
                        page = this.createPageButton(pageNumber);
                        $('#people-database-prev').after(page);
                    }

                    if (first != 1) {
                        this.addPageButtons(1, true);
                    }
                    if (last != this.pageCount) {
                        this.addPageButtons(this.pageCount, false);
                    }
                }
                $('#people-database-next').show();
                $('#people-database-prev').show();
            }
        },

        AnnotateLabel.createPageButton = function (pageNumber) {
            var self = this;
            var page = $(
                '<li id="people-database-p' + pageNumber + '" class="people-database-page paginate_button">' +
                '<a href="#">' + pageNumber + '</a>' +
                '</li>'
            );

            page.click(function (event) {
                self.pageNumber = parseInt(event.target.text);
                self.saveAll(function() {
                    window.location = "/annotator-supreme/label-annotation?dataset="+self.dataset+"&pageNumber="+self.pageNumber+"&itemsPerPage="+self.pageCount    
                });

                

            });

            if (pageNumber == this.pageNumber) {
                page.addClass("active");
            }
            return page;
        }

    AnnotateLabel.addPageButtons = function (pageNumber, first) {
        var page = this.createPageButton(pageNumber);

        if (first) {
            $('#people-database-prev').after(page);
            page.after('<li class="paginate_button people-separator disabled"><a href="#">...</a></li>');
        } else {
            $('#people-database-next').before(page);
            page.before('<li class="paginate_button people-separator disabled"><a href="#">...</a></li>');
        }
    }


    AnnotateLabel.updatePreviousNextPaginationControllers = function() {
        $('#people-database-next').removeClass("disabled");
        $('#people-database-prev').removeClass("disabled");

        if (this.pageNumber == 1) {
          $('#people-database-prev').addClass("disabled");
        }
        if (this.pageNumber == this.pageCount) {
          $('#people-database-next').addClass("disabled");
        }
      }

      AnnotateLabel.bindPagination = function() {
        var self = this;
        
        $('#people-database-prev').click(function(event) {
            // event.preventDefault();
            if (self.pageNumber > 1) {
                self.pageNumber -= 1;
                self.saveAll(function() {
                    window.location = "/annotator-supreme/label-annotation?dataset="+self.dataset+"&pageNumber="+self.pageNumber+"&itemsPerPage="+self.pageCount    
                });
            }
        });

        $('#people-database-next').click(function(event) {
            // event.preventDefault();
            if (self.pageNumber < self.pageCount) {
                self.pageNumber += 1;
                self.saveAll(function() {
                    window.location = "/annotator-supreme/label-annotation?dataset="+self.dataset+"&pageNumber="+self.pageNumber+"&itemsPerPage="+self.pageCount    
                });
            }
        });
      }

    global.AnnotateLabel = AnnotateLabel;
    global.AnnotateLabel.init();

}(window, jQuery));