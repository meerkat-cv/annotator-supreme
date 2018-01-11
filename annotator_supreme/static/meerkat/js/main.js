(function (global, $) {

    var Main = {};

    Main.init = function () {
        var self = this;
        $(document).ready(function () {
            self.getVersion();
            self.bindLoginButtons();
        });
    }


    Main.setCurrentUsername = function (username) {
        if (username !== '') {
            console.log("username", username);
            this.getBeerCount();
        }
    }

    Main.getBeerCount = function () {
        var self = this;

        $('[data-toggle="control-sidebar"]').click(function () {
            console.log("opened?", $(".control-sidebar").hasClass("control-sidebar-open"))
            if (!$(".control-sidebar").hasClass("control-sidebar-open")) {
                // indeed the control panel is opening
                $.ajax({
                    type: 'get',
                    url: "/annotator-supreme/beer_count",
                    success: function (data) {
                        self.setBeersToCollect(data.total_beers);
                        self.animateNextBeer(data.next_beer_percentage);
                    }
                });
            }
        });
    }

    Main.setBeersToCollect = function (n_beers) {
        $(".beer-count-desc span").html(n_beers);

        $(".beer-count .fa-beer").remove();
        beer_marker = '<i class="fa fa-beer" aria-hidden="true"></i>\n';
        for (var i = 0; i < n_beers; ++i) {
            $(".beer-count").append(beer_marker)
        }
    }

    Main.animateNextBeer = function (percentage) {

        max_liquid = 150
        max_foam = 130
        liquid = max_liquid * percentage;
        foam = max_foam * percentage;
        $('#liquid') // I Said Fill 'Er Up!
            .delay(40)
            .animate({
                height: liquid + 'px'
            }, 2000);

        $('.beer-foam') // Keep that Foam Rollin' Toward the Top! Yahooo!
            .delay(40)
            .animate({
                bottom: foam + 'px'
            }, 2000);

        $(".beer-current-status span").html(Math.ceil(percentage*100));

    }

    Main.getVersion = function () {
        console.log("asfdasdf");
        $.ajax({
            type: 'get',
            url: "/annotator-supreme/version",
            success: function (data) {
                console.log("ok", data.version);
                $(".annotator-version-global").html('<b>Version:</b> ' + data.version);
            },
            error: function () {
                console.log("Could not get version, something is wierd!");
            }
        });
    }

    Main.enableLoading = function (msg) {
        if (msg) {
            $('#loading-msg').html(msg);
        }
        $('#modal-loading').modal('show');
    }

    Main.disableLoading = function (msg) {
        $('#modal-loading').modal('hide');
    }

    Main.bindLoginButtons = function () {
        $("#logout-btn").click(function () {
            $.ajax({
                type: 'get',
                url: "/annotator-supreme/logout",
                success: function () {
                    location.reload();
                }
            });
        });

        $("#login-btn").click(function () {
            location.href = "/annotator-supreme/login";
        });

        $("#register-btn").click(function () {
            location.href = "/annotator-supreme/register";
        })

    }

    global.Main = Main;
    global.Main.init();

}(window, jQuery));