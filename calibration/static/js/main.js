

var socket = new WebSocket('ws://localhost:8000/ws/calibration/' + $('#title')[0].className);

function add_row(text, id){
    return `<tr id="id_${id}">
                <th scope="row"><span id="id_${id}_load" class="loader fas fa-spinner"></span></th>
                <td>${text}</td>
                <td ><div class="container limit-height" id="id_${id}_box"><small id="id_${id}_msg"></small></div></td>
            </tr>`
}

function add_msg(msg, err=false){
    let color = err? 'text-danger': 'text-muted';
    return `<p class="font-weight-light ${color}">${msg}</p>`
}

socket.onmessage = function (e) {
    try {
        let data = JSON.parse(e.data);
        let id = Object.keys(data)[0];
        let cate = Object.keys(data[id])[0];
        if (cate === "msg"){
            $('#id_'+ id + '_msg').append(add_msg(data[id]['msg'], false));
            let container = $('#id_'+id+'_box')[0];
            container.scrollTop = container.scrollHeight-container.offsetHeight;
        }else if(cate === 'err'){
            $('#id_'+ id + '_msg').append(add_msg(data[id]['err'], true));
            let load = $('#id_'+ id + '_load');
            load.removeClass('loader');
            load.removeClass('fa-spinner');
            load.addClass('fa-exclamation');
        }else if(cate === 'finish'){
            let load = $('#id_'+ id + '_load');
            load.removeClass('loader');
            load.removeClass('fa-spinner');
            load.addClass('fa-check');
        }else if(cate === 'start') {
            $("#id_table").append(add_row(data[id]['start'], id));
        }else if(cate === 'ing1'){
            $('#id_calib_opt').append(
                `<table class="table" id="id_calib_table" ><tr class="text-muted"><th></th>${data[id][cate]}</tr></table>`)
        }else if(cate === 'ing') {
            $("#id_calib_table").append(`<tr class="text-muted"><td></td>${data[id][cate]}</tr>`)
        } else if(cate === 'good') {
            $($('#id_calib_table')[0].lastChild.lastChild).removeClass("text-muted").addClass('text-info')
            let container = $('#id_calib_opt')[0];
            container.scrollTop = container.scrollHeight-container.offsetHeight - 16.5;
        } else if(cate === 'res') {
            $("#id_calib_table").append(`<tr class="text-danger"><td>result</td>${data[id][cate]}</tr>`)
            let container = $('#id_calib_opt')[0];
            container.scrollTop = container.scrollHeight-container.offsetHeight - 16.5;
        } else if(cate === 'edge-start' || cate === 'edge-inv-start') {
            $('#id_'+ id + '_msg').append(`
<div class="row">
<div class="col-10">
<div class="progress">
<div class="progress-bar progress-bar-striped bg-info"
id=${"id_" + cate} role="progressbar"  style="width: ${data[id][cate]}%" 
aria-valuenow="${data[id][cate]}" aria-valuemin="0" aria-valuemax="100"></div></div>
</div>` + ( cate=== 'edge-inv-start'?
`<div class="col-2">
<a class="badge badge-danger" href="#" type="button" onclick="pause_edge()">
<span class="fas fa-pause"></span></a>        
</div>          </div>                       
`:''))
        } else if (cate === 'edge' || cate === 'edge-inv') {
            let f = $("#id_" + cate + '-start')[0];
            f.setAttribute( 'style', "width: "+data[id][cate]+"%");
            f.setAttribute( 'aria-valuenow', data[id][cate]);
        }
    }catch (error) {
        console.log(error);
        $('#id_img')[0].innerHTML = `<img class='img-fluid img-thumbnail rounded mx-auto d-block' src=${ e.data } />`
    }

}

function stop(){
    socket.send('kill');
}

function pause_edge(){
    socket.send('edge_pause');
}