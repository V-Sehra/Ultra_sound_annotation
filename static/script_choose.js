function continue_click(){
    const body_check = document.querySelector('#pictograph');

    if (body_check.checked){
     body = 1
    }else{
    body = 0 
    };
    
    $.ajax({
      type: "POST",
      url: "http://127.0.0.1:5000/collect_body_bool",
      data:{
        body_bool: body,
        
      }
    }).done(function() {
      window.location.href = "/correct_crop";
    });

}

