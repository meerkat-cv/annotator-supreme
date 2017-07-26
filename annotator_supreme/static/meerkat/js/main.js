(function (global, $) {

    var Main = {};

    Main.init = function () {
        var self = this;
        $(document).ready( function () {
            self.bindChangeAPIKey();
            self.bindBackupImages();
        }); 
    }

    Main.bindChangeAPIKey = function () {
        $('#change-apikey-btn').click(function () {
            var user_api_key = $('#change-apikey-text').val();
            $.ajax({
                type: 'get',
                url: '/frapi/session_apikey/'+user_api_key,
                success: function() {
                    location.reload();
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    $('#api-error-alert').removeClass('hidden');
                    var error = JSON.parse(jqXHR.responseText);
                    $('#api-error-msg').html(error['message']);
                },
            });
        });
    }

    Main.bindBackupImages = function () {
        $('#backup-images-btn').click(function () {
            $.ajax({
                type: 'get',
                url: '/frapi/tools/backup_images',
                success: function(data) {
                    console.log('data', data);
                    window.location = '/frapi' + data;
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    console.log("error on downloading images");
                },
            });
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

    global.Main = Main;
    global.Main.init();

}(window, jQuery));
