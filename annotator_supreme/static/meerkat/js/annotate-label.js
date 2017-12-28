(function (global, $) {

    var AnnotateLabel = {},
        dataset_sel = $('#dataset-sel'),
        category_entry = $('#category-entry'),
        clear_btn = $("#clear-files-btn");

    AnnotateLabel.init = function () {
        this.populateImages();
        // this.bind();
    };

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
        this.itemsPerPage = 10; //TODO: in mobile could be one

        var self = this;
        $.ajax({
            url: '/annotator-supreme/image/' + self.dataset + '/all?pageNumber=' + self.pageNumber + '&itemsPerPage=' + self.itemsPerPage,
            type: 'GET',
            success: function (data) {
                console.log("Done!", data);
                // window.location.reload();
                self.pageCount = data.totalPages;
                self.pageNumber = data.pageNumber;
                self.addPaginationControllers();
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
                event.preventDefault();
                self.pageNumber = parseInt(event.target.text);

                window.location = "/annotator-supreme/label-annotation?dataset="+self.dataset+"&pageNumber="+self.pageNumber+"&itemsPerPage="+self.pageCount

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

    global.AnnotateLabel = AnnotateLabel;
    global.AnnotateLabel.init();

}(window, jQuery));