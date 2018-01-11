(function (global, $) {

    var LoginLogin = {};

    LoginLogin.init = function () {
        var self = this;
        $('#login-form').submit(function(e) { // bind function to submit event of form
            // e.preventDefault();
            $.ajax({
                type: $(this).attr('method'), // get type of request from 'method'
                url: $(this).attr('action'), // get url of request from 'action'
                data: $(this).serialize(), // serialize the form's data
                success: function(responseText) {
                    window.location = "/annotator-supreme/"
                },
                statusCode: {
                    432: function () {
                        self.showError("Invalid credentials.")
                    }
                }
            });
            
            return false;
        });
    }

    LoginLogin.showError = function(message) {
        $("#error-message-container").removeClass("hidden");
        $("#error-message-container .error-message").html(message);
    }

    global.LoginLogin = LoginLogin;
    global.LoginLogin.init();

}(window, jQuery));