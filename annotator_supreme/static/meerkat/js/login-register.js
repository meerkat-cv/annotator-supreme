(function (global, $) {

    var LoginRegister = {};

    LoginRegister.init = function () {
        var self = this;
        $('#register-form').submit(function() { // bind function to submit event of form
            if ($("#pass1").val() != $("#pass2").val()) {
                self.showError("Passwords don't match!");
                return false; // important: prevent the form from submitting
            }
            // if id="pass1"
            $.ajax({
                type: $(this).attr('method'), // get type of request from 'method'
                url: $(this).attr('action'), // get url of request from 'action'
                data: $(this).serialize(), // serialize the form's data
                success: function(responseText) {
                    window.location = "/annotator-supreme/login"
                },
                statusCode: {
                    432: function () {
                        self.showError("Username already taken.")
                    }
                }
            });
            return false;
        });
    }


    LoginRegister.showError = function(message) {
        $("#error-message-container").removeClass("hidden");
        $("#error-message-container .error-message").html(message);
    }

    global.LoginRegister = LoginRegister;
    global.LoginRegister.init();

}(window, jQuery));