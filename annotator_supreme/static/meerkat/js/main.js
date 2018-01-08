(function (global, $) {

    var Main = {};

    Main.init = function () {
        var self = this;
        $(document).ready( function () {
            self.getVersion();
            self.bindLoginButtons();
        }); 
    }

    Main.getVersion = function () {
        console.log("asfdasdf");
        $.ajax({
            type: 'get',
            url: "/annotator-supreme/version",
            success: function (data) {
                console.log("ok", data.version);
                $(".annotator-version-global").html('<b>Version:</b> '+data.version);
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
