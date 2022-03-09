

var socket = new WebSocket('ws://localhost:8000/ws/calibration/' + $('#title')[0].className);

function add_row(text, id){
    return `<tr id="id_${id}">
                <th scope="row"><span id="id_${id}_load" class="loader fas fa-spinner"></span></th>
                <td>${text}</td>
                <td id="id_${id}_msg"></td>
            </tr>`
}

function add_msg(msg, err=false){
    let color = err? 'text-danger': 'text-muted';
    return `<p class="font-weight-light"><small class="${color}">${msg}</small></p>`
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
        load.addClass('fa-x');
    }else if(cate === 'finish'){
        let load = $('#id_'+ id + '_load');
        load.removeClass('loader');
        load.removeClass('fa-spinner');
        load.addClass('fa-check');
    }else if(cate === 'start'){
        $("#id_table").append(add_row(data[id]['start'], id))
    }

    $('#test_show').append('<p>' + JSON.parse(e.data) + '</p>');
}

function stop(){
    socket.send('stop pressed');
}