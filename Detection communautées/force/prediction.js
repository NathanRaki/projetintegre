function get_prediction_data(){
    httpRequest = new XMLHttpRequest();
    httpRequest.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = httpRequest.response;
            // div = document.createElement('div');
            // div.innerHTML = response;
            // document.getElementById('prediction_chart').appendChild(div);
            script = response.split('<script>')
            script2 = script[1].split('</script>')
            document.getElementById('prediction_chart').innerHTML += script[0] + eval(script2[0]);
            console.log(document.getElementById('prediction_chart'))
        }
    };
    httpRequest.open('GET', 'http://localhost:10546/get_prediction_graph', true);
    httpRequest.send();
}
get_prediction_data();