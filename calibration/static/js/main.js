

var socket = new WebSocket('ws://localhost:8000/ws/calibration/' + $('#title')[0].className);

function add_row(text, id){
    return `<tr id="id_${id}">
                <th scope="row"><span id="id_${id}_load" class="loader fas fa-spinner"></span></th>
                <td>${text}</td>
                <td ><div class="container limit-height"><small id="id_${id}_msg"></small></div></td>
            </tr>`
}

function add_msg(msg, err=false){
    let color = err? 'text-danger': 'text-muted';
    return `<p class="font-weight-light line-small ${color}">${msg}</p>`
}

socket.onmessage = function (e) {
    let data = JSON.parse(e.data);
    let id = Object.keys(data)[0];
    let cate = Object.keys(data[id])[0];
        if (cate === "msg"){
            $('#id_'+ id + '_msg').append(add_msg(data[id]['msg'], false));
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
            $('#id_calib_msg').append(
                `<table class="table" id="id_calib_table"><tr class="text-muted"><th></th>${data[id][cate]}</tr></table>`)
        }else if(cate === 'ing') {
            $("#id_calib_table").append(`<tr class="text-muted"><th></th>${data[id][cate]}</tr>`)
        } else if(cate === 'good') {
            $($('#id_calib_table')[0].lastChild.lastChild).removeClass("text-muted").addClass('text-danger')
        } else if(cate === 'res') {
            $("#id_calib_table").append(`<tr class="text-info"><th>result</th>${data[id][cate]}</tr>`)
    }


}

function stop(){
    socket.send('stop pressed');
}