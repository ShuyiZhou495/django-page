const all_paras = ["cfx", "cfy", "cx", "cy", "ck1", "ck2", "cp1", "cp2", "ck3", "cb1"];
const cam_paras = new Map([
    ['omni', []],
    ['perspective', ["cfx", "cfy", "cx", "cy", "ck1", "ck2", "cp1", "cp2","ck3"]],
    ['pinhole', ["cfx", "cfy", "cx", "cy"]],
    ['fisheye', ["cfx", "cfy", "cx", "cy", "ck1", "ck2", "ck3", "cb1"]]
]);

var cams = new Map();
var cam_para;

window.onload = (event) =>{
    Array.from(cam_paras.keys()).map(key => {
        cams.set(key, $("#" + key).detach());
    });
    cam_para = $("#cam_para");
    let selected = $("#id_cam_type")[0];
    let v = selected[selected.selectedIndex].value;
    if (v!==''){
        cam_para.append(cams.get(v)[0].outerHTML)
    }
    alt_by_class($("#id_select_frame_by_hand")[0].checked, 'manual_select', 'random_select');

    let edge_use = $("#id_edge_use")[0].checked;
    let mi_use = $("#id_mi_use")[0].checked;
    show_by_id(edge_use, 'edge_setting');
    show_by_id(mi_use, 'mi_setting');

    let ini_type = $('#id_ini_type')[0];
    show_angles(ini_type.options[ini_type.selectedIndex].value);

    add_option('mi', mi_use);
    add_option('edge', edge_use);
    let vis_selection = $('#id_vis')[0].options[1].innerHTML;
    if(vis_selection !== ''){
        $("#vis_" + vis_selection)[0].selected=true;
    }
    show_by_id($("#id_test")[0].checked, 'if_test');
};

function show_para(selected){
    cam_para.children().remove();
    if (selected === '') {
        return;
    }
    cam_para.append(cams.get(selected)[0].outerHTML)
}

function alt_by_class(value, class1, class2){
    let target1 = $("." + class1);
    let target2 = $("." + class2);
    if (value){
        target1.show();
        target1.prop('required', true);
        target2.hide();
        target2.removeAttr('required');
    }
    else {
        target2.show();
        target2.prop('required', true);
        target1.hide();
        target1.removeAttr('required');
    }
}

function show_by_id(value, id){
    let target = $("#" + id);
    if (value){
        target.show();
        target.find('input[type=number]').prop('required', true);
        target.find('input[type=text]').prop('required', true);
    }
    else {
        target.hide();
        target.find('input').removeAttr('required');
    }
}

function add_option(method, value){
    target = $("#id_vis");
    if(method ==='mi') {
        if (value) {
            target.append("<option id='vis_mi' value='mi'>show points within a range</option>");
            target.append("<option id='vis_mi-r' value='mi-r'>show points within a range, colored by reflectivity</option>");
        } else {
            target.find('#vis_mi').remove();
            target.find('#vis_mi-r').remove();
        }
    }
    if(method ==='edge') {
        if (value) {
            target.append("<option id='vis_edge' value='edge'>show edge points</option>");
            target.append("<option id='vis_edge-e' value='edge-e'>show edge points on image of edges</option>");
        } else {
            target.find('#vis_edge').remove();
            target.find('#vis_edge-e').remove();
        }
    }
}
function show_angles(value){
    let euler = $('.euler');
    let quat = $('.quat');
    let all = $('.all');
    if(value==='euler'){
        all.show();
        euler.show();
        quat.hide();
        quat.removeAttr('required');
    } else if(value==='quaternion'){
        quat.show();
        quat.prop('required', true);
        euler.hide();
        all.show();
    }
    else {
        quat.hide();
        quat.removeAttr('required');
        euler.hide();
        all.hide();
    }
}