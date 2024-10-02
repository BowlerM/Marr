//function for setting correct size of text areas to fit content when page is loaded
$(function() {
    $('textarea').each(function() {
        $(this).height($(this).prop('scrollHeight'));
    });
});


$(document).ready(function() {
    //set the token so that we are not rejected by server
	var csrf_token = $('meta[name=csrf-token]').attr('content');
    //configure ajaxSetup so that the CSRF token is added to the header of every request
   $.ajaxSetup({
       beforeSend: function(xhr, settings) {
           if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
               xhr.setRequestHeader("X-CSRFToken", csrf_token);
           }
       }
   });

   //like button
    $("a.like").on("click", function() {
        var clicked_obj = $(this);

        //which post was clicked
        var postId = $(this).attr("id");

        $.ajax({
            url: '/like',
            type: 'POST',
            data: JSON.stringify({ postId: postId }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response){
                console.log(response);
                
                //if post was liked
                if(response.liked) {
                    //replace hollow heart icon with solid red one
                    clicked_obj.children()[0].classList.remove('fa-regular');
                    clicked_obj.children()[0].classList.add('fa-solid');
                } 
                //if post was unliked
                else {
                    //replace solid red heart icon with regular one
                    clicked_obj.children()[0].classList.remove('fa-solid');
                    clicked_obj.children()[0].classList.add('fa-regular');           
                }
                //update like counts text to display updated like count
                clicked_obj.children()[1].innerText = " " + response.likes;
            },
            error: function(error){
                console.log(error);
            }
        });
    });

    //delete account button
    $("button.delete-account").on("click", function() {
        //show confirmation box asking user if they are sure they want to delete their account
        if (confirm("You are about to delete your account are you sure you want to do this?")) {
            $.ajax({
                url: '/delete-account',
                type: 'POST',
                data: JSON.stringify({ confirmed: true }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",

                //reload page (will take user back to login page) on successful deletion of account
                success: function(response){
                    console.log(response);
                    location.reload();
                },
                error: function(error){
                    console.log(error);
                }
            });
        }
    });
});