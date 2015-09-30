/**
 * Created by guohui on 15-9-29.
 */

define(["app/api", "app/isso"], function (api, isso) {

    return function (thread_id) {
        var ws = new WebSocket("ws://127.0.0.1:8000/ws/thread-"+thread_id+"?subscribe-broadcast");

        // What do we do when we get a message?
        ws.onmessage = function (response) {
            console.log(response.data);

            isso.insert(JSON.parse(response.data), false);
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

    }


});
