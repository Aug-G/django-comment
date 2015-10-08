/**
 * Created by guohui on 15-9-29.
 */

define(function () {

    var ws;
    var init = function(thread_id, onmessage){
        ws = new WebSocket("ws://127.0.0.1:8000/ws/thread-"+thread_id+"?subscribe-broadcast&publish-broadcast");

        // What do we do when we get a message?
        ws.onmessage = function (response) {
            return onmessage(JSON.parse(response.data));
        };
        // Just update our conn_status field with the connection status
        ws.onopen = function (evt) {
            console.log('Connected!')
        };
        ws.onerror = function (evt) {
            console.log(evt);
        };
        ws.onclose = function (evt) {
            console.log('Closed!')
        };
    };


    var send_message = function(type, data){
        message = {'type': type, 'data': data};
        if(!ws) return;
        ws.send(JSON.stringify(message));
    };

    return {
        init:init,
        send_message:send_message
    };

});
