var canvas = document.getElementById("paint");
var ctx = canvas.getContext("2d");
var width = canvas.width;
var height = canvas.height;
var curX, curY, prevX, prevY;
var hold = false;
ctx.lineWidth = 2;
var fill_value = true;
var stroke_value = false;
var marking = [];
// var canvas_data = {"hcc_mark": [], "ccc_mark": [], "eraser": []};
var canvas_data = {"stroke": []};

function load(){
    if (prev_click == 'hcc'){
        hcc_mark();
        
        };
    if (prev_unsure == 1){
        document.querySelector('#unsure').checked = true;
    }else{
        document.querySelector('#unsure').checked = false;
        };
    if (prev_bad_frame == 1){
        document.querySelector('#bad_frame').checked = true;
    }else{
        document.querySelector('#bad_frame').checked = false;
        };
        
    if (prev_click == 'ccc'){
        ccc_mark();
        
        };
    if (prev_click == 'era'){
        eraser();
        
        };
    console.log(prev_canv.length)
    if (prev_canv.length >= 1){
    
        for (let prev_draw_id = 0 ; prev_draw_id < prev_canv.length; prev_draw_id ++){
        
            console.log(prev_canv[prev_draw_id][0])
            if (prev_canv[prev_draw_id][0] == 0){
            
                
               draw_prev('hcc',prev_canv[prev_draw_id][1]) 
            
            }; 
            if (prev_canv[prev_draw_id][0] == 1){
        
               draw_prev('ccc',prev_canv[prev_draw_id][1]) 
               
            };
            if (prev_canv[prev_draw_id][0] == 2){
        
               erase(prev_canv[prev_draw_id][1]) 
               
            };
            

        
            function draw_prev(type, mat){
            

        
                if (type== 'hcc'){
                    ctx.strokeStyle = 'red';
                }else{
                ctx.strokeStyle = 'blue';
                };
            
                ctx.beginPath();
                ctx.moveTo(mat[0][0], mat[0][1]);
                
                
                if (type== 'hcc'){
                canvas_data.stroke.push({ "type":"hcc","startx": mat[0][0], "starty": mat[0][1]});
                
    
                    }else {
               
                canvas_data.stroke.push({ "type":"ccc","startx": mat[0][0], "starty": mat[0][1]});
                    };
                for (let obj = 1; obj < mat.length; obj++) {
    
                    ctx.lineTo(mat[obj][0], mat[obj][1]);
                    ctx.stroke();
                    
                    canvas_data.stroke.push({ "endx": mat[obj][0], "endy": mat[obj][1]});

                    };
                
                    
        
            };
            function erase(mat){
            

                console.log(mat[0]);
                console.log(mat[1]);
                ctx.strokeStyle = 'red';
            
            
                ctx.beginPath();
                ctx.moveTo(mat[0][0], mat[0][1]);
                
                canvas_data.stroke.push({ "type":"era","startx": mat[0][0], "starty": mat[0][1]});
                  
                
                for (let i = 1; i < mat.length; i++) {
                    x = mat[i][0];
                    y = mat[i][1];
                    ctx.clearRect(x ,y, -45, -45 ); 
                    ctx.stroke();
                                   
                    canvas_data.stroke.push({ "endx": mat[i][0], "endy": mat[i][1]});
                    };
            
                    
                
                };
        
        };
    
    };
};
   
function reset(){
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    canvas_data = {"stroke": []};
}

        
// pencil tool
        
function hcc_mark(){
    prev_click = 'hcc';
    
    ctx.strokeStyle = 'red';
    
    canvas.onmousedown = function(e){
        curX = e.clientX - canvas.offsetLeft;
        curY = e.clientY - canvas.offsetTop;
        hold = true;
            
        prevX = curX;
        prevY = curY;
        ctx.beginPath();
        ctx.moveTo(prevX, prevY);
        canvas_data.stroke.push({ "type":"hcc","startx": prevX, "starty": prevY});
    };
        
    canvas.onmousemove = function(e){
        if(hold){
            curX = e.clientX - canvas.offsetLeft;
            curY = e.clientY - canvas.offsetTop;
            draw();
        }
    };
        
    canvas.onmouseup = function(e){
        hold = false;
        append();
        
        
    };
        
    canvas.onmouseout = function(e){
        hold = false;
    };
        
    function draw(){
        ctx.lineTo(curX, curY);
        ctx.stroke();
        
        canvas_data.stroke.push({"endx": curX, "endy": curY});
        
    };
    function append(){
        // marking =ctx.getImageData(0,0,canvas.width, canvas.height);
        // ctx.putImageData(marking,0,0);
    };    

}
        
function ccc_mark(){
    prev_click = 'ccc';
    ctx.strokeStyle = 'blue';
        
    canvas.onmousedown = function(e){
        curX = e.clientX - canvas.offsetLeft;
        curY = e.clientY - canvas.offsetTop;
        hold = true;
            
        prevX = curX;
        prevY = curY;
        ctx.beginPath();
        ctx.moveTo(prevX, prevY);
        canvas_data.stroke.push({ "type":"ccc","startx": prevX, "starty": prevY});
    };
        
    canvas.onmousemove = function(e){
        if(hold){
            curX = e.clientX - canvas.offsetLeft;
            curY = e.clientY - canvas.offsetTop;
            draw();
        }
    };
        
    canvas.onmouseup = function(e){
        hold = false;
        append();

    };
        
    canvas.onmouseout = function(e){
        hold = false;
    };
        
    function draw(){
        ctx.lineTo(curX, curY);
        ctx.stroke();
       
        canvas_data.stroke.push({"endx": curX, "endy": curY});

    };
    function append(){
        // marking =ctx.getImageData(0,0,canvas.width, canvas.height);    
        // ctx.putImageData(marking,0,0);

    };    

}
        
// eraser tool
        
function eraser(){
    prev_click = 'era';
    canvas.onmousedown = function(e){
        curX = e.clientX - canvas.offsetLeft;
        curY = e.clientY - canvas.offsetTop;
        hold = true;
            
        prevX = curX;
        prevY = curY;
        ctx.beginPath();
        ctx.moveTo(prevX, prevY);
        canvas_data.stroke.push({ "type":"era","startx": prevX, "starty": prevY});
    };
        
    canvas.onmousemove = function(e){
        if(hold){
            curX = e.clientX - canvas.offsetLeft;
            curY = e.clientY - canvas.offsetTop;
            draw(curX,curY);;
        }
    };
        
    canvas.onmouseup = function(e){
        hold = false;
        append();
    };
        
    canvas.onmouseout = function(e){
        hold = false;
    };
        
    function draw(x,y){
        ctx.clearRect(x ,y, -45, -45 ); 
        canvas_data.stroke.push({"endx": curX, "endy": curY});

        };
    function append(){
        // marking =ctx.getImageData(0,0,canvas.width, canvas.height);    
        // ctx.putImageData(marking,0,0);

    };  
}  
function prev_click_but(){
    var image = canvas.toDataURL();
    var canv_dat = JSON.stringify(canvas_data);
    var un = 0;
    const cb = document.querySelector('#unsure');
    const cb_bad_frame = document.querySelector('#bad_frame');
    //var p_ck = prev_click
    
    if (cb.checked){
     un = 1
    }else{
    un = 0 
    };
    
     if (cb_bad_frame.checked){
      b_frame = 1
     }else{
     b_frame = 0 
     };
        
    $.ajax({
      type: "POST",
      url: " http://127.0.0.1:5000/can_im",
      data:{
        imageBase64: image,
        data: canv_dat,
        bad_frame : b_frame,
        un_sure : un,
        prev_ck : prev_click,
      }
    }).done(function() {
      window.location.href = "/prev_frame";
    });

}


function next_click_but(){
    var image = canvas.toDataURL();
    var canv_dat = JSON.stringify(canvas_data);
    var un = 0;
    const cb = document.querySelector('#unsure');
    const cb_bad_frame = document.querySelector('#bad_frame');

    
    if (cb.checked){
     un = 1
    }else{
    un = 0 
    };

     if (cb_bad_frame.checked){
      b_frame = 1
     }else{
     b_frame = 0 
     };
        
    $.ajax({
      type: "POST",
      url: "http://127.0.0.1:5000/can_im",
      data:{
        imageBase64: image,
        data: canv_dat,
        un_sure : un,
        bad_frame : b_frame,
        prev_ck : prev_click,
        
      }
    }).done(function() {
      window.location.href = "/next_frame";
    });

}
function save_exit(){
    var image = canvas.toDataURL();
    var canv_dat = JSON.stringify(canvas_data);
    var un = 0;
    const cb = document.querySelector('#unsure');
    const cb_bad_frame = document.querySelector('#bad_frame');

    if (cb.checked){
     un = 1
    }else{
    un = 0 
    };

    if (cb_bad_frame.checked){
     b_frame = 1
    }else{
    b_frame = 0 
    };

    
    $.ajax({
      type: "POST",
      url: "http://127.0.0.1:5000/can_im",
      data:{
        imageBase64: image,
        data: canv_dat,
        un_sure : un,
        bad_frame : b_frame,
        prev_ck : prev_click,
        
      }
    }).done(function() {
      window.location.href = "/save_and_exit";
    });

}

function prev_mark_click(){

      window.location.href = "/get_prev_mark";


}