function check_preview() {

}


function check_alias() {
    var length_pass = true, charset_pass = true;
    var alias = $("#alias");
    length_pass = /^.{7,32}$/.test(alias.val());
    charset_pass = /^[a-zA-Z0-9_-]+$/.test(alias.val());

    if (!length_pass && alias.val().length > 0) {
        $("#length-warner").removeClass('valid').addClass('invalid');
    }
    else {
        $("#length-warner").removeClass('invalid').addClass('valid');
    }

    if (!charset_pass && alias.val().length > 0) {
        $("#charset-warner").removeClass('valid').addClass('invalid');
    }
    else {
        $("#charset-warner").removeClass('invalid').addClass('valid');
    }

    if ((!length_pass || !charset_pass) && alias.val().length > 0) {
        $("#invalid-input-warner").css('display', 'block');
        $("#alias-input-gp").addClass('has-error');
    }
    else {
        $("#invalid-input-warner").css('display', 'none');
        if (alias.val().length > 0) {
            $("#alias-input-gp").removeClass('has-error').addClass('has-success');
        }
        else {
            $("#alias-input-gp").removeClass('has-error').removeClass('has-success');
        }
    }
}


function upload_file() {
    var file = $("#file")[0].files[0];
    var progress_bar = $(".bottom-progress-bar");
    var button = $("#upload-file-bt");
    var formData = new FormData();

    if (file) {
        if (file.size > 200000 * 1024 * 1024) {
            alert("This file is too large");
        }
        else if ($("#invalid-input-warner").css("display") !== "none") {
            alert("Invalid tag name");
        }
        else {
            formData.append("alias", $("#alias").val());
            formData.append("file", file);
            formData.append("public", $("#publicity")[0].checked);

            console.log(formData);
            // Upload
            $.ajax({
                // Your server script to process the upload
                url: "/upload/",
                type: 'POST',

                // Form data
                data: formData,

                // Tell jQuery not to process data or worry about content-type
                // You *must* include these options!
                cache: false,
                contentType: false,
                processData: false,

                // Custom XMLHttpRequest
                xhr: function () {
                    var myXhr = $.ajaxSettings.xhr();
                    if (myXhr.upload) {
                        // For handling the progress of the upload
                        myXhr.upload.addEventListener('progress', function (e) {
                            var percent;
                            if (e.lengthComputable) {
                                percent = 99 * e.loaded / e.total;
                                progress_bar.css("width", percent + "%");
                                button.text("Uploading...");
                                button.prop('disabled', true);
                            }

                            if (percent === 99) {
                                progress_bar.css("width", percent + "%");
                                button.text("Processing...");
                            }

                        }, false);
                    }
                    return myXhr;
                },
                success: function (res) {
                    var status = res["status"];
                    var data = res["data"];
                    var container = $("#upload-result-container");

                    progress_bar.css("width", "0");

                    if (status === true) {
                        container.children().each(function () {
                            this.remove();
                        });
                        container.append(data);
                    }
                    else {
                        alert(data);
                        location.reload();
                    }
                },
                error: function () {
                    alert("Oops, something went wrong, check your connection and try again");
                    location.reload();
                }
            });
        }
    }
    else {
        alert("Please choose a file");
    }
}


function copyToClipboard(element) {
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val($(element).text()).select();
    document.execCommand("copy");
    $temp.remove();
}


$("#file").change(function () {
    var file = this.files[0];
    var filename;
    var file_holder = $(".upload-file-label");

    file_holder.children().each(function () {
        this.remove();
    });

    if (file) {
        filename = file.name;
        file_holder.append("<i class=\"glyphicon glyphicon-cloud-upload\" style=\"padding-right: 5px\"></i>");
        file_holder.append($("<span></span>").text(filename));
    }
    else {
        file_holder.append("<span>\n" +
            "<i class=\"glyphicon glyphicon-cloud-upload\"\n" +
            "style=\"padding-right: 5px\"></i>Choose a file<br>\n" +
            "<span style=\"font-size: large\">&nbsp&nbsp&nbsp&nbsp&nbsp(Maximum size: 20MB)</span>\n" +
            "</span>");
    }
});


$("#publicity").change(function () {
    if (this.checked) {
        $("#alias").val("").prop('disabled', true);
        check_alias();
    }
    else {
        $("#alias").prop('disabled', false);
    }
});


$(document).ready(function () {
    $("#alias").keyup(check_alias);
});
