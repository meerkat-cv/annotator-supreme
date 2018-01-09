(function (global, $) {

    var BeerManager = {},
        login_btn = $('#login-btn'),
        logout_btn = $('#logout-btn'),
        register_btn = $("#register-btn");

    BeerManager.init = function () {
        this.setBeerProgress();
        this.bindButtons();
    };


    BeerManager.bindButtons = function () {
        
    }

    BeerManager.setBeerProgress = function () {
        $(document).ready(function () {
            $('#liquid') // I Said Fill 'Er Up!
                .delay(100)
                .animate({
                    height: '100px'
                }, 2500);

            $('.beer-foam') // Keep that Foam Rollin' Toward the Top! Yahooo!
                .delay(100)
                .animate({
                    bottom: '90px'
                }, 2500);
        });

    }





    global.BeerManager = BeerManager;
    global.BeerManager.init();

}(window, jQuery));