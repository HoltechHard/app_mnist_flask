$(document).ready(function(){

    $("#upload-form").submit(function(event){
        event.preventDefault();
        var formData = new FormData($('#upload-form')[0]);
        
        $.ajax({
            url: '/upload/',
            type: 'POST',
            data: formData,
            async: false,
            cache: false,
            contentType: false,
            enctype: 'multipart/form-data',
            processData: false,
            success: function(response){

                // display the uploaded image
                $('#uploaded-image').attr('src', 'static/images/' + response.filename);                
                console.log(response.filename);

                // ajax request to make prediction
                $.ajax({
                    url: '/predict/',
                    type: 'POST',
                    data: formData,
                    async: false,
                    cache: false,
                    contentType: false,
                    enctype: 'multipart/form-data',
                    processData: false,
                    success: function(response){            
                        $('#result').empty().append(response);            
                    }
                }); 
            }
        });        
    });    
});
